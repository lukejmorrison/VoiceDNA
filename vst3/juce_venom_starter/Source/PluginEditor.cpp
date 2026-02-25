#include "PluginEditor.h"

VoiceDNAAudioProcessorEditor::VoiceDNAAudioProcessorEditor(VoiceDNAAudioProcessor& processor)
    : AudioProcessorEditor(&processor), audioProcessor(processor)
{
    setSize(560, 220);
}

void VoiceDNAAudioProcessorEditor::paint(juce::Graphics& graphics)
{
    graphics.fillAll(juce::Colours::black);
    graphics.setColour(juce::Colours::white);
    graphics.setFont(18.0f);
    graphics.drawText("VoiceDNA VST3 (JUCE + VENOM Starter)", getLocalBounds().removeFromTop(40), juce::Justification::centred);

    graphics.setFont(13.0f);
    graphics.drawText(
        "Bridge target: vst3/venom_bridge.py\n"
        "Use this scaffold to integrate VoiceDNA processing for Reaper.",
        getLocalBounds().reduced(16),
        juce::Justification::topLeft,
        true);
}

void VoiceDNAAudioProcessorEditor::resized()
{
}
