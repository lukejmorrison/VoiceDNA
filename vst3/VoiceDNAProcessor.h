#pragma once

class VoiceDNAProcessor {
public:
    VoiceDNAProcessor() = default;
    ~VoiceDNAProcessor() = default;

    void prepareToPlay(double sampleRate, int samplesPerBlock);
    void processBlock(float* interleavedBuffer, int numSamples, int numChannels);
    void releaseResources();
};
