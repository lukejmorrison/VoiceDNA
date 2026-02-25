#pragma once

#include <juce_audio_basics/juce_audio_basics.h>
#include <juce_core/juce_core.h>

class VoiceDNABridge
{
public:
    struct RuntimeConfig
    {
        juce::String dnaPath;
        juce::String password;
        float forceAge = 12.0f;
        float imprintStrength = 0.68f;
        juce::String baseModel = "vst3_reaper";
    };

    VoiceDNABridge(juce::String repoRoot, juce::String pythonExecutable);

    bool processBuffer(
        juce::AudioBuffer<float>& buffer,
        double sampleRate,
        const RuntimeConfig& config,
        juce::String& errorMessage) const;

    bool birthVoice(
        const juce::String& parentAPath,
        const juce::String& parentBPath,
        const juce::String& childUserName,
        float inheritParentA,
        float inheritParentB,
        float randomness,
        const juce::String& outputPath,
        const juce::String& password,
        juce::String& statusMessage) const;

private:
    juce::String repoRoot;
    juce::String pythonExecutable;

    bool writeBufferToWavFile(const juce::AudioBuffer<float>& buffer, double sampleRate, const juce::File& file) const;
    bool readWavFileToBuffer(const juce::File& file, juce::AudioBuffer<float>& buffer) const;
    juce::String quote(const juce::String& value) const;
};
