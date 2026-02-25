#pragma once

#include <juce_audio_processors/juce_audio_processors.h>

#include "VoiceDNABridge.h"

class VoiceDNAAudioProcessor final : public juce::AudioProcessor
{
public:
    VoiceDNAAudioProcessor();
    ~VoiceDNAAudioProcessor() override = default;

    void prepareToPlay(double sampleRate, int samplesPerBlock) override;
    void releaseResources() override;
    bool isBusesLayoutSupported(const BusesLayout& layouts) const override;
    void processBlock(juce::AudioBuffer<float>&, juce::MidiBuffer&) override;

    juce::AudioProcessorEditor* createEditor() override;
    bool hasEditor() const override { return true; }

    const juce::String getName() const override { return "VoiceDNAVST3"; }
    bool acceptsMidi() const override { return false; }
    bool producesMidi() const override { return false; }
    bool isMidiEffect() const override { return false; }
    double getTailLengthSeconds() const override { return 0.0; }

    int getNumPrograms() override { return 1; }
    int getCurrentProgram() override { return 0; }
    void setCurrentProgram(int) override {}
    const juce::String getProgramName(int) override { return {}; }
    void changeProgramName(int, const juce::String&) override {}

    void getStateInformation(juce::MemoryBlock& destData) override;
    void setStateInformation(const void* data, int sizeInBytes) override;

    juce::AudioProcessorValueTreeState& getState() { return state; }
    static juce::AudioProcessorValueTreeState::ParameterLayout createParameterLayout();

    void setDnaPath(const juce::String& path);
    juce::String getDnaPath() const;

    void setBridgePassword(const juce::String& passwordValue);
    juce::String getBridgePassword() const;

    void setParentAPath(const juce::String& path);
    void setParentBPath(const juce::String& path);
    juce::String getParentAPath() const;
    juce::String getParentBPath() const;

    juce::String getLineageDisplay() const;

    bool birthNewVoice(
        const juce::String& childUserName,
        const juce::String& outputPath,
        juce::String& statusMessage);

    juce::String getLastBridgeStatus() const;

private:
    juce::AudioProcessorValueTreeState state;
    VoiceDNABridge bridge;

    mutable juce::CriticalSection configLock;
    juce::String dnaPath;
    juce::String bridgePassword;
    juce::String parentAPath;
    juce::String parentBPath;
    juce::String lastBridgeStatus;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(VoiceDNAAudioProcessor)
};
