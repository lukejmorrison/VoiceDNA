cmake_minimum_required(VERSION 3.22)
project(VoiceDNAVST3 VERSION 2.9.6)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Set JUCE_DIR to your local JUCE checkout, for example:
# cmake -DJUCE_DIR=/path/to/JUCE ..
if(NOT DEFINED JUCE_DIR)
  message(FATAL_ERROR "JUCE_DIR is not set. Point JUCE_DIR to your JUCE root directory.")
endif()

add_subdirectory(${JUCE_DIR} JUCE)

juce_add_plugin(VoiceDNAVST3
  COMPANY_NAME "VoiceDNA"
  IS_SYNTH FALSE
  NEEDS_MIDI_INPUT FALSE
  NEEDS_MIDI_OUTPUT FALSE
  IS_MIDI_EFFECT FALSE
  EDITOR_WANTS_KEYBOARD_FOCUS FALSE
  COPY_PLUGIN_AFTER_BUILD TRUE
  PLUGIN_MANUFACTURER_CODE VDNA
  PLUGIN_CODE VDN3
  FORMATS VST3
  PRODUCT_NAME "VoiceDNA VST3"
)

target_sources(VoiceDNAVST3 PRIVATE
  Source/PluginProcessor.cpp
  Source/PluginEditor.cpp
)

target_compile_definitions(VoiceDNAVST3 PRIVATE
  JUCE_WEB_BROWSER=0
  JUCE_USE_CURL=0
)

target_link_libraries(VoiceDNAVST3 PRIVATE
  juce::juce_audio_utils
)
