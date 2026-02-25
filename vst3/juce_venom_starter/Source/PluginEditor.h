#pragma once

#include "PluginProcessor.h"

#include <array>

class VoiceDNAAudioProcessorEditor final : public juce::AudioProcessorEditor
{
public:
    explicit VoiceDNAAudioProcessorEditor(VoiceDNAAudioProcessor&);
    ~VoiceDNAAudioProcessorEditor() override = default;

    void paint(juce::Graphics&) override;
    void resized() override;

private:
    VoiceDNAAudioProcessor& audioProcessor;

    juce::Label titleLabel;
    juce::Label statusLabel;
    juce::Label lineageLabel;

    juce::TextButton loadDnaButton;
    juce::TextButton parentAButton;
    juce::TextButton parentBButton;
    juce::TextButton birthButton;

    juce::Label dnaPathLabel;
    juce::Label parentALabel;
    juce::Label parentBLabel;

    juce::Label passwordLabel;
    juce::TextEditor passwordEditor;
    juce::Label childUserLabel;
    juce::TextEditor childUserEditor;

    juce::Label modeLabel;
    juce::ComboBox modeBox;
    juce::ToggleButton bridgeToggle;

    juce::Slider ageSlider;
    juce::Slider imprintSlider;
    juce::Slider parentASlider;
    juce::Slider parentBSlider;
    juce::Slider randomnessSlider;
    std::array<juce::Label, 5> sliderLabels;

    using SliderAttachment = juce::AudioProcessorValueTreeState::SliderAttachment;
    using ComboAttachment = juce::AudioProcessorValueTreeState::ComboBoxAttachment;
    using ButtonAttachment = juce::AudioProcessorValueTreeState::ButtonAttachment;

    std::unique_ptr<SliderAttachment> ageAttachment;
    std::unique_ptr<SliderAttachment> imprintAttachment;
    std::unique_ptr<SliderAttachment> parentAAttachment;
    std::unique_ptr<SliderAttachment> parentBAttachment;
    std::unique_ptr<SliderAttachment> randomnessAttachment;
    std::unique_ptr<ComboAttachment> modeAttachment;
    std::unique_ptr<ButtonAttachment> bridgeAttachment;

    void configureSlider(juce::Slider& slider, juce::Label& label, const juce::String& text);
    void refreshLabels();
    void loadDnaFile();
    void chooseParentA();
    void chooseParentB();
    void birthVoice();

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(VoiceDNAAudioProcessorEditor)
};
