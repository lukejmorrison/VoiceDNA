#include "PluginEditor.h"

VoiceDNAAudioProcessorEditor::VoiceDNAAudioProcessorEditor(VoiceDNAAudioProcessor& processor)
    : AudioProcessorEditor(&processor), audioProcessor(processor)
{
    setSize(920, 520);

    titleLabel.setText("VoiceDNA v3.0 — VST3 Voice Genetics Plugin", juce::dontSendNotification);
    titleLabel.setFont(juce::Font(24.0f, juce::Font::bold));
    addAndMakeVisible(titleLabel);

    statusLabel.setText("Ready", juce::dontSendNotification);
    statusLabel.setColour(juce::Label::textColourId, juce::Colours::lightgreen);
    addAndMakeVisible(statusLabel);

    lineageLabel.setText("Lineage: (unset) × (unset) -> child", juce::dontSendNotification);
    addAndMakeVisible(lineageLabel);

    loadDnaButton.setButtonText("Load .voicedna");
    loadDnaButton.onClick = [this]() { loadDnaFile(); };
    addAndMakeVisible(loadDnaButton);

    parentAButton.setButtonText("Select Parent A Audio");
    parentAButton.onClick = [this]() { chooseParentA(); };
    addAndMakeVisible(parentAButton);

    parentBButton.setButtonText("Select Parent B Audio");
    parentBButton.onClick = [this]() { chooseParentB(); };
    addAndMakeVisible(parentBButton);

    birthButton.setButtonText("Birth New Voice");
    birthButton.onClick = [this]() { birthVoice(); };
    addAndMakeVisible(birthButton);

    dnaPathLabel.setText("DNA: (not loaded)", juce::dontSendNotification);
    addAndMakeVisible(dnaPathLabel);

    parentALabel.setText("Parent A: (not selected)", juce::dontSendNotification);
    addAndMakeVisible(parentALabel);

    parentBLabel.setText("Parent B: (not selected)", juce::dontSendNotification);
    addAndMakeVisible(parentBLabel);

    passwordLabel.setText("DNA Password", juce::dontSendNotification);
    addAndMakeVisible(passwordLabel);

    passwordEditor.setPasswordCharacter('*');
    passwordEditor.onTextChange = [this]() {
        audioProcessor.setBridgePassword(passwordEditor.getText());
    };
    addAndMakeVisible(passwordEditor);

    childUserLabel.setText("Child User", juce::dontSendNotification);
    addAndMakeVisible(childUserLabel);

    childUserEditor.setText("agent_child", juce::dontSendNotification);
    addAndMakeVisible(childUserEditor);

    modeLabel.setText("Mode", juce::dontSendNotification);
    addAndMakeVisible(modeLabel);

    modeBox.addItem("Create / Imprint", 1);
    modeBox.addItem("Real-time Filter", 2);
    addAndMakeVisible(modeBox);

    bridgeToggle.setButtonText("Enable Python Bridge Processing");
    addAndMakeVisible(bridgeToggle);

    configureSlider(ageSlider, sliderLabels[0], "Age");
    configureSlider(imprintSlider, sliderLabels[1], "Imprint Strength");
    configureSlider(parentASlider, sliderLabels[2], "Parent A %");
    configureSlider(parentBSlider, sliderLabels[3], "Parent B %");
    configureSlider(randomnessSlider, sliderLabels[4], "Randomness");

    auto& state = audioProcessor.getState();
    ageAttachment = std::make_unique<SliderAttachment>(state, "age_years", ageSlider);
    imprintAttachment = std::make_unique<SliderAttachment>(state, "imprint_strength", imprintSlider);
    parentAAttachment = std::make_unique<SliderAttachment>(state, "inherit_parent_a", parentASlider);
    parentBAttachment = std::make_unique<SliderAttachment>(state, "inherit_parent_b", parentBSlider);
    randomnessAttachment = std::make_unique<SliderAttachment>(state, "lineage_randomness", randomnessSlider);
    modeAttachment = std::make_unique<ComboAttachment>(state, "processing_mode", modeBox);
    bridgeAttachment = std::make_unique<ButtonAttachment>(state, "bridge_enabled", bridgeToggle);

    refreshLabels();
}

void VoiceDNAAudioProcessorEditor::paint(juce::Graphics& graphics)
{
    graphics.fillAll(juce::Colour(0xff12151f));
    graphics.setColour(juce::Colour(0xff304269));
    graphics.drawRoundedRectangle(getLocalBounds().toFloat().reduced(8.0f), 12.0f, 1.0f);
}

void VoiceDNAAudioProcessorEditor::resized()
{
    auto area = getLocalBounds().reduced(14);
    auto top = area.removeFromTop(56);
    titleLabel.setBounds(top.removeFromLeft(580));
    statusLabel.setBounds(top.removeFromLeft(320));

    auto row1 = area.removeFromTop(30);
    modeLabel.setBounds(row1.removeFromLeft(60));
    modeBox.setBounds(row1.removeFromLeft(220));
    bridgeToggle.setBounds(row1.removeFromLeft(300));

    area.removeFromTop(8);
    auto row2 = area.removeFromTop(32);
    loadDnaButton.setBounds(row2.removeFromLeft(170));
    dnaPathLabel.setBounds(row2);

    area.removeFromTop(6);
    auto row3 = area.removeFromTop(32);
    passwordLabel.setBounds(row3.removeFromLeft(120));
    passwordEditor.setBounds(row3.removeFromLeft(260));
    childUserLabel.setBounds(row3.removeFromLeft(90));
    childUserEditor.setBounds(row3.removeFromLeft(220));

    area.removeFromTop(8);
    auto row4 = area.removeFromTop(34);
    parentAButton.setBounds(row4.removeFromLeft(210));
    parentALabel.setBounds(row4);

    area.removeFromTop(4);
    auto row5 = area.removeFromTop(34);
    parentBButton.setBounds(row5.removeFromLeft(210));
    parentBLabel.setBounds(row5);

    area.removeFromTop(6);
    lineageLabel.setBounds(area.removeFromTop(26));

    area.removeFromTop(8);
    constexpr int rowHeight = 36;
    for (size_t index = 0; index < sliderLabels.size(); ++index)
    {
        auto sliderRow = area.removeFromTop(rowHeight);
        sliderLabels[index].setBounds(sliderRow.removeFromLeft(180));
        switch (index)
        {
            case 0: ageSlider.setBounds(sliderRow); break;
            case 1: imprintSlider.setBounds(sliderRow); break;
            case 2: parentASlider.setBounds(sliderRow); break;
            case 3: parentBSlider.setBounds(sliderRow); break;
            case 4: randomnessSlider.setBounds(sliderRow); break;
            default: break;
        }
        area.removeFromTop(4);
    }

    area.removeFromTop(8);
    birthButton.setBounds(area.removeFromTop(34).removeFromLeft(200));
}

void VoiceDNAAudioProcessorEditor::configureSlider(juce::Slider& slider, juce::Label& label, const juce::String& text)
{
    slider.setSliderStyle(juce::Slider::LinearHorizontal);
    slider.setTextBoxStyle(juce::Slider::TextBoxRight, false, 90, 22);
    slider.setNumDecimalPlacesToDisplay(2);
    addAndMakeVisible(slider);

    label.setText(text, juce::dontSendNotification);
    addAndMakeVisible(label);
}

void VoiceDNAAudioProcessorEditor::refreshLabels()
{
    const auto dnaPath = audioProcessor.getDnaPath();
    dnaPathLabel.setText(
        dnaPath.isNotEmpty() ? "DNA: " + juce::File(dnaPath).getFileName() : "DNA: (not loaded)",
        juce::dontSendNotification);

    const auto parentAPath = audioProcessor.getParentAPath();
    parentALabel.setText(
        parentAPath.isNotEmpty() ? "Parent A: " + juce::File(parentAPath).getFileName() : "Parent A: (not selected)",
        juce::dontSendNotification);

    const auto parentBPath = audioProcessor.getParentBPath();
    parentBLabel.setText(
        parentBPath.isNotEmpty() ? "Parent B: " + juce::File(parentBPath).getFileName() : "Parent B: (not selected)",
        juce::dontSendNotification);

    lineageLabel.setText(audioProcessor.getLineageDisplay(), juce::dontSendNotification);
}

void VoiceDNAAudioProcessorEditor::loadDnaFile()
{
    juce::FileChooser chooser("Select VoiceDNA file", juce::File{}, "*.voicedna;*.voicedna.enc");
    if (chooser.browseForFileToOpen())
    {
        const auto selected = chooser.getResult().getFullPathName();
        audioProcessor.setDnaPath(selected);
        refreshLabels();
        statusLabel.setText("Loaded DNA file", juce::dontSendNotification);
    }
}

void VoiceDNAAudioProcessorEditor::chooseParentA()
{
    juce::FileChooser chooser("Select parent A audio", juce::File{}, "*.wav;*.mp3;*.flac;*.m4a");
    if (chooser.browseForFileToOpen())
    {
        audioProcessor.setParentAPath(chooser.getResult().getFullPathName());
        refreshLabels();
    }
}

void VoiceDNAAudioProcessorEditor::chooseParentB()
{
    juce::FileChooser chooser("Select parent B audio", juce::File{}, "*.wav;*.mp3;*.flac;*.m4a");
    if (chooser.browseForFileToOpen())
    {
        audioProcessor.setParentBPath(chooser.getResult().getFullPathName());
        refreshLabels();
    }
}

void VoiceDNAAudioProcessorEditor::birthVoice()
{
    juce::FileChooser chooser("Save child VoiceDNA", juce::File::getCurrentWorkingDirectory(), "*.voicedna.enc");
    if (!chooser.browseForFileToSave(true))
    {
        return;
    }

    audioProcessor.setBridgePassword(passwordEditor.getText());
    juce::String status;
    const auto success = audioProcessor.birthNewVoice(
        childUserEditor.getText().trim(),
        chooser.getResult().getFullPathName(),
        status);

    statusLabel.setColour(juce::Label::textColourId, success ? juce::Colours::lightgreen : juce::Colours::orange);
    statusLabel.setText(status.isNotEmpty() ? status : (success ? "Birth complete" : "Birth failed"), juce::dontSendNotification);
}
