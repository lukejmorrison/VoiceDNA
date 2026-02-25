#pragma once

#include "PluginProcessor.h"

class VoiceDNAAudioProcessorEditor final : public juce::AudioProcessorEditor
{
public:
    explicit VoiceDNAAudioProcessorEditor(VoiceDNAAudioProcessor&);
    ~VoiceDNAAudioProcessorEditor() override = default;

    void paint(juce::Graphics&) override;
    void resized() override;

private:
    VoiceDNAAudioProcessor& audioProcessor;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(VoiceDNAAudioProcessorEditor)
};
