#include "PluginProcessor.h"
#include "PluginEditor.h"

VoiceDNAAudioProcessor::VoiceDNAAudioProcessor()
    : AudioProcessor(BusesProperties()
        .withInput("Input", juce::AudioChannelSet::stereo(), true)
        .withOutput("Output", juce::AudioChannelSet::stereo(), true))
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

    // VENOM bridge hook point:
    // 1) Convert buffer -> WAV/PCM bytes
    // 2) Send to Python bridge (venom_bridge.py)
    // 3) Receive processed bytes and write back to buffer

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
    juce::MemoryOutputStream stream(destData, false);
    stream.writeString("VoiceDNA VST3 state placeholder");
}

void VoiceDNAAudioProcessor::setStateInformation(const void*, int)
{
}

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new VoiceDNAAudioProcessor();
}
