import os.path
import time
import numpy as np
from scipy.io import wavfile

from AudioStegnographyAlgo.AudioStegnographyAlgorithm import AudioStego


class PhaseEncodingAudioStego(AudioStego):

    # encode
    def encodeAudio(self, audioLocation, stringToEncode) -> str:

        self.convertToByteArray(audioLocation)

        stringToEncode = stringToEncode.ljust(100, '~')

        # step 1 divide into chunks
        textLength = 8 * len(stringToEncode)

        blockLength = int(2 * 2 ** np.ceil(np.log2(2 * textLength)))
        blockNumber = int(np.ceil(self.audioData.shape[0] / blockLength))

        # checks shape to change data to 1 axis
        if len(self.audioData.shape) == 1:
            self.audioData.resize(blockNumber * blockLength, refcheck=False)
            self.audioData = self.audioData[np.newaxis]
        else:
            self.audioData.resize((blockNumber * blockLength, self.audioData.shape[1]), refcheck=False)
            self.audioData = self.audioData.T

        blocks = self.audioData[0].reshape((blockNumber, blockLength))

        # Calculate DFT using fft
        blocks = np.fft.fft(blocks)

        # calculate magnitudes
        magnitudes = np.abs(blocks)

        # create phase matrix
        phases = np.angle(blocks)

        # get phase differences
        phaseDiffs = np.diff(phases, axis=0)

        # conert message to encode into binary
        textInBinary = np.ravel([[int(y) for y in format(ord(x), "08b")] for x in stringToEncode])

        # Convert txt to phase differences
        textInPi = textInBinary.copy()
        textInPi[textInPi == 0] = -1
        textInPi = textInPi * -np.pi / 2

        blockMid = blockLength // 2

        # do phase conversion
        phases[0, blockMid - textLength: blockMid] = textInPi
        phases[0, blockMid + 1: blockMid + 1 + textLength] = -textInPi[::-1]

        # re compute  the ophase amtrix
        for i in range(1, len(phases)):
            phases[i] = phases[i - 1] + phaseDiffs[i - 1]

        # apply i-dft
        blocks = (magnitudes * np.exp(1j * phases))
        blocks = np.fft.ifft(blocks).real

        # combining all block of audio again
        self.audioData[0] = blocks.ravel().astype(np.int16)

        return self.saveToLocation(self.audioData.T, audioLocation)

    def decodeAudio(self, audioLocation) -> str:

        self.convertToByteArray(audioLocation)
        textLength = 800
        blockLength = 2 * int(2 ** np.ceil(np.log2(2 * textLength)))
        blockMid = blockLength // 2

        # get header info
        if len(self.audioData.shape) == 1:
            secret = self.audioData[:blockLength]
        else:
            secret = self.audioData[:blockLength, 0]

        # get the phase and convert it to binary
        secretPhases = np.angle(np.fft.fft(secret))[blockMid - textLength:blockMid]
        secretInBinary = (secretPhases < 0).astype(np.int8)

        #  convert into characters
        secretInIntCode = secretInBinary.reshape((-1, 8)).dot(1 << np.arange(8 - 1, -1, -1))

        # combine characters to original text
        return "".join(np.char.mod("%c", secretInIntCode)).replace("~", "")

    def convertToByteArray(self, audio):
        # convert into byte array
        try:
            self.rate, self.audioData = wavfile.read(audio)
        except:
            pass
        self.audioData = self.audioData.copy()

    def saveToLocation(self, audioArray, location) -> str:
        dir = os.path.dirname(location)
        unique_filename = f"{dir}/output-pc-{int(time.time())}.wav"  # Unique filename
        wavfile.write(unique_filename, self.rate, audioArray)
        return unique_filename 