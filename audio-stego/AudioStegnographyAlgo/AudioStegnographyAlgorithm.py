from abc import ABC, abstractmethod


# abstract class for a  audio steganography algorithm
# all the methods in this class need to be over written to make a new audio steganography algorithm
class AudioStego(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def encodeAudio(self, audioLocation, stringToEncode) -> str:
        pass

    @abstractmethod
    def decodeAudio(self, audioLocation) -> str:
        pass

    @abstractmethod
    def convertToByteArray(self, audio):
        pass

    @abstractmethod
    def saveToLocation(self, audioArray, location) -> str:
        pass