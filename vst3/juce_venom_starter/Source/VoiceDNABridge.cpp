#include "VoiceDNABridge.h"

#include <juce_audio_formats/juce_audio_formats.h>

VoiceDNABridge::VoiceDNABridge(juce::String repoRootValue, juce::String pythonExecutableValue)
    : repoRoot(std::move(repoRootValue)), pythonExecutable(std::move(pythonExecutableValue))
{
}

bool VoiceDNABridge::processBuffer(
    juce::AudioBuffer<float>& buffer,
    double sampleRate,
    const RuntimeConfig& config,
    juce::String& errorMessage) const
{
    if (config.dnaPath.isEmpty())
    {
        errorMessage = "No VoiceDNA file selected";
        return false;
    }

    const auto tempDir = juce::File::getSpecialLocation(juce::File::tempDirectory);
    const auto sessionId = juce::Uuid().toString();
    const auto inputFile = tempDir.getChildFile("vdna_in_" + sessionId + ".wav");
    const auto outputFile = tempDir.getChildFile("vdna_out_" + sessionId + ".wav");

    if (!writeBufferToWavFile(buffer, sampleRate, inputFile))
    {
        errorMessage = "Failed writing temporary input WAV";
        return false;
    }

    const auto bridgeScript = juce::File(repoRoot).getChildFile("vst3").getChildFile("bridge_runtime.py");
    if (!bridgeScript.existsAsFile())
    {
        errorMessage = "bridge_runtime.py not found";
        inputFile.deleteFile();
        return false;
    }

    juce::String command;
    command << quote(pythonExecutable)
            << " " << quote(bridgeScript.getFullPathName())
            << " process"
            << " --dna-path " << quote(config.dnaPath)
            << " --password " << quote(config.password)
            << " --input-wav " << quote(inputFile.getFullPathName())
            << " --output-wav " << quote(outputFile.getFullPathName())
            << " --base-model " << quote(config.baseModel)
            << " --force-age " << juce::String(config.forceAge, 2)
            << " --imprint-strength " << juce::String(config.imprintStrength, 3);

    juce::ChildProcess process;
    if (!process.start(command))
    {
        errorMessage = "Failed launching Python runtime bridge";
        inputFile.deleteFile();
        return false;
    }

    const auto finished = process.waitForProcessToFinish(1200);
    const auto outputText = process.readAllProcessOutput();
    inputFile.deleteFile();

    if (!finished || process.getExitCode() != 0)
    {
        errorMessage = outputText.isNotEmpty() ? outputText : "Python bridge process failed";
        outputFile.deleteFile();
        return false;
    }

    const auto loaded = readWavFileToBuffer(outputFile, buffer);
    outputFile.deleteFile();

    if (!loaded)
    {
        errorMessage = "Python bridge produced unreadable WAV output";
        return false;
    }

    return true;
}

bool VoiceDNABridge::birthVoice(
    const juce::String& parentAPath,
    const juce::String& parentBPath,
    const juce::String& childUserName,
    float inheritParentA,
    float inheritParentB,
    float randomness,
    const juce::String& outputPath,
    const juce::String& password,
    juce::String& statusMessage) const
{
    const auto bridgeScript = juce::File(repoRoot).getChildFile("vst3").getChildFile("bridge_runtime.py");
    if (!bridgeScript.existsAsFile())
    {
        statusMessage = "bridge_runtime.py not found";
        return false;
    }

    juce::String command;
    command << quote(pythonExecutable)
            << " " << quote(bridgeScript.getFullPathName())
            << " birth"
            << " --parent-a " << quote(parentAPath)
            << " --parent-b " << quote(parentBPath)
            << " --child-user " << quote(childUserName)
            << " --inherit-a " << juce::String(inheritParentA, 2)
            << " --inherit-b " << juce::String(inheritParentB, 2)
            << " --randomness " << juce::String(randomness, 2)
            << " --out " << quote(outputPath)
            << " --password " << quote(password);

    juce::ChildProcess process;
    if (!process.start(command))
    {
        statusMessage = "Failed launching birth runtime bridge";
        return false;
    }

    const auto finished = process.waitForProcessToFinish(15000);
    const auto outputText = process.readAllProcessOutput();

    if (!finished || process.getExitCode() != 0)
    {
        statusMessage = outputText.isNotEmpty() ? outputText : "Birth process failed";
        return false;
    }

    statusMessage = outputText.isNotEmpty() ? outputText.trim() : "Voice birth completed";
    return true;
}

bool VoiceDNABridge::writeBufferToWavFile(const juce::AudioBuffer<float>& buffer, double sampleRate, const juce::File& file) const
{
    juce::WavAudioFormat format;
    auto stream = file.createOutputStream();
    if (stream == nullptr)
    {
        return false;
    }

    std::unique_ptr<juce::AudioFormatWriter> writer(
        format.createWriterFor(stream.get(), sampleRate, static_cast<unsigned int>(buffer.getNumChannels()), 16, {}, 0));

    if (writer == nullptr)
    {
        return false;
    }

    stream.release();
    return writer->writeFromAudioSampleBuffer(buffer, 0, buffer.getNumSamples());
}

bool VoiceDNABridge::readWavFileToBuffer(const juce::File& file, juce::AudioBuffer<float>& buffer) const
{
    juce::AudioFormatManager manager;
    manager.registerBasicFormats();

    std::unique_ptr<juce::AudioFormatReader> reader(manager.createReaderFor(file));
    if (reader == nullptr)
    {
        return false;
    }

    juce::AudioBuffer<float> loadedBuffer(static_cast<int>(reader->numChannels), static_cast<int>(reader->lengthInSamples));
    if (!reader->read(&loadedBuffer, 0, static_cast<int>(reader->lengthInSamples), 0, true, true))
    {
        return false;
    }

    const auto channelsToCopy = juce::jmin(buffer.getNumChannels(), loadedBuffer.getNumChannels());
    const auto samplesToCopy = juce::jmin(buffer.getNumSamples(), loadedBuffer.getNumSamples());

    buffer.clear();
    for (int channel = 0; channel < channelsToCopy; ++channel)
    {
        buffer.copyFrom(channel, 0, loadedBuffer, channel, 0, samplesToCopy);
    }

    return true;
}

juce::String VoiceDNABridge::quote(const juce::String& value) const
{
    return "\"" + value.replace("\"", "\\\"") + "\"";
}
