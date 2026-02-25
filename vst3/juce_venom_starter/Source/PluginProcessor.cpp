#include "PluginProcessor.h"
#include "PluginEditor.h"

#ifndef VOICEDNA_REPO_ROOT
#define VOICEDNA_REPO_ROOT "."
#endif

#ifndef VOICEDNA_PYTHON_EXECUTABLE
#define VOICEDNA_PYTHON_EXECUTABLE "python3"
#endif

VoiceDNAAudioProcessor::VoiceDNAAudioProcessor()
    : AudioProcessor(BusesProperties()
        .withInput("Input", juce::AudioChannelSet::stereo(), true)
                .withOutput("Output", juce::AudioChannelSet::stereo(), true)),
            state(*this, nullptr, "voice_dna_state", createParameterLayout()),
            bridge(VOICEDNA_REPO_ROOT, VOICEDNA_PYTHON_EXECUTABLE)
{
}

void VoiceDNAAudioProcessor::prepareToPlay(double, int)
{
}

void VoiceDNAAudioProcessor::releaseResources()
{
}

bool VoiceDNAAudioProcessor::isBusesLayoutSupported(const BusesLayout& layouts) const
{
    return layouts.getMainInputChannelSet() == layouts.getMainOutputChannelSet();
}

void VoiceDNAAudioProcessor::processBlock(juce::AudioBuffer<float>& buffer, juce::MidiBuffer&)
{
    juce::ScopedNoDenormals noDenormals;

    const auto bridgeEnabled = state.getRawParameterValue("bridge_enabled")->load() >= 0.5f;
    const auto modeValue = state.getRawParameterValue("processing_mode")->load();

    if (bridgeEnabled && modeValue >= 0.5f)
    {
        VoiceDNABridge::RuntimeConfig runtimeConfig;
        {
            const juce::ScopedLock lock(configLock);
            runtimeConfig.dnaPath = dnaPath;
            runtimeConfig.password = bridgePassword;
        }
        runtimeConfig.forceAge = state.getRawParameterValue("age_years")->load();
        runtimeConfig.imprintStrength = state.getRawParameterValue("imprint_strength")->load();

        juce::String errorMessage;
        if (!bridge.processBuffer(buffer, getSampleRate(), runtimeConfig, errorMessage))
        {
            const juce::ScopedLock lock(configLock);
            lastBridgeStatus = "Bridge error: " + errorMessage;
        }
        else
        {
            const juce::ScopedLock lock(configLock);
            lastBridgeStatus = "Bridge process ok";
        }
    }

    for (int channel = getTotalNumInputChannels(); channel < getTotalNumOutputChannels(); ++channel)
    {
        buffer.clear(channel, 0, buffer.getNumSamples());
    }
}

juce::AudioProcessorEditor* VoiceDNAAudioProcessor::createEditor()
{
    return new VoiceDNAAudioProcessorEditor(*this);
}

void VoiceDNAAudioProcessor::getStateInformation(juce::MemoryBlock& destData)
{
    if (const auto xml = state.copyState().createXml())
    {
        copyXmlToBinary(*xml, destData);
    }
}

void VoiceDNAAudioProcessor::setStateInformation(const void* data, int sizeInBytes)
{
    if (const auto xml = getXmlFromBinary(data, sizeInBytes))
    {
        if (xml->hasTagName(state.state.getType()))
        {
            state.replaceState(juce::ValueTree::fromXml(*xml));
        }
    }
}

juce::AudioProcessorValueTreeState::ParameterLayout VoiceDNAAudioProcessor::createParameterLayout()
{
    std::vector<std::unique_ptr<juce::RangedAudioParameter>> parameters;
    parameters.push_back(std::make_unique<juce::AudioParameterChoice>(
        "processing_mode",
        "Mode",
        juce::StringArray{"Create / Imprint", "Real-time Filter"},
        1));
    parameters.push_back(std::make_unique<juce::AudioParameterBool>(
        "bridge_enabled",
        "Bridge Enabled",
        false));
    parameters.push_back(std::make_unique<juce::AudioParameterFloat>(
        "age_years",
        "Age",
        juce::NormalisableRange<float>(5.0f, 30.0f, 0.1f),
        12.0f));
    parameters.push_back(std::make_unique<juce::AudioParameterFloat>(
        "imprint_strength",
        "Imprint Strength",
        juce::NormalisableRange<float>(0.0f, 1.0f, 0.01f),
        0.68f));
    parameters.push_back(std::make_unique<juce::AudioParameterFloat>(
        "inherit_parent_a",
        "Parent A %",
        juce::NormalisableRange<float>(0.0f, 100.0f, 0.1f),
        50.0f));
    parameters.push_back(std::make_unique<juce::AudioParameterFloat>(
        "inherit_parent_b",
        "Parent B %",
        juce::NormalisableRange<float>(0.0f, 100.0f, 0.1f),
        50.0f));
    parameters.push_back(std::make_unique<juce::AudioParameterFloat>(
        "lineage_randomness",
        "Randomness",
        juce::NormalisableRange<float>(0.0f, 100.0f, 0.1f),
        10.0f));

    return {parameters.begin(), parameters.end()};
}

void VoiceDNAAudioProcessor::setDnaPath(const juce::String& path)
{
    const juce::ScopedLock lock(configLock);
    dnaPath = path;
}

juce::String VoiceDNAAudioProcessor::getDnaPath() const
{
    const juce::ScopedLock lock(configLock);
    return dnaPath;
}

void VoiceDNAAudioProcessor::setBridgePassword(const juce::String& passwordValue)
{
    const juce::ScopedLock lock(configLock);
    bridgePassword = passwordValue;
}

juce::String VoiceDNAAudioProcessor::getBridgePassword() const
{
    const juce::ScopedLock lock(configLock);
    return bridgePassword;
}

void VoiceDNAAudioProcessor::setParentAPath(const juce::String& path)
{
    const juce::ScopedLock lock(configLock);
    parentAPath = path;
}

void VoiceDNAAudioProcessor::setParentBPath(const juce::String& path)
{
    const juce::ScopedLock lock(configLock);
    parentBPath = path;
}

juce::String VoiceDNAAudioProcessor::getParentAPath() const
{
    const juce::ScopedLock lock(configLock);
    return parentAPath;
}

juce::String VoiceDNAAudioProcessor::getParentBPath() const
{
    const juce::ScopedLock lock(configLock);
    return parentBPath;
}

juce::String VoiceDNAAudioProcessor::getLineageDisplay() const
{
    const juce::ScopedLock lock(configLock);
    const auto parentA = parentAPath.isNotEmpty() ? juce::File(parentAPath).getFileName() : "(unset)";
    const auto parentB = parentBPath.isNotEmpty() ? juce::File(parentBPath).getFileName() : "(unset)";
    return "Lineage: " + parentA + " × " + parentB + " -> child";
}

bool VoiceDNAAudioProcessor::birthNewVoice(
    const juce::String& childUserName,
    const juce::String& outputPath,
    juce::String& statusMessage)
{
    const auto inheritA = state.getRawParameterValue("inherit_parent_a")->load();
    const auto inheritB = state.getRawParameterValue("inherit_parent_b")->load();
    const auto randomness = state.getRawParameterValue("lineage_randomness")->load();

    juce::String parentA;
    juce::String parentB;
    juce::String password;
    {
        const juce::ScopedLock lock(configLock);
        parentA = parentAPath;
        parentB = parentBPath;
        password = bridgePassword;
    }

    if (parentA.isEmpty() || parentB.isEmpty())
    {
        statusMessage = "Select both parent audio files first";
        return false;
    }

    if (password.isEmpty())
    {
        statusMessage = "Bridge password is required to save encrypted child VoiceDNA";
        return false;
    }

    const auto ok = bridge.birthVoice(
        parentA,
        parentB,
        childUserName,
        inheritA,
        inheritB,
        randomness,
        outputPath,
        password,
        statusMessage);

    {
        const juce::ScopedLock lock(configLock);
        lastBridgeStatus = statusMessage;
    }

    return ok;
}

juce::String VoiceDNAAudioProcessor::getLastBridgeStatus() const
{
    const juce::ScopedLock lock(configLock);
    return lastBridgeStatus;
}

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new VoiceDNAAudioProcessor();
}
