"""
This type stub file was generated by pyright.
"""

"""
Each generator will return float samples from -1.0 to 1.0, which can be 
converted to actual audio with 8, 16, 24, or 32 bit depth using the
SiganlGenerator.to_audio_segment() method (on any of it's subclasses).

See Wikipedia's "waveform" page for info on some of the generators included 
here: http://en.wikipedia.org/wiki/Waveform
"""
class SignalGenerator:
    def __init__(self, sample_rate=..., bit_depth=...) -> None:
        ...
    
    def to_audio_segment(self, duration=..., volume=...): # -> AudioSegment:
        """
        Duration in milliseconds
            (default: 1 second)
        Volume in DB relative to maximum amplitude
            (default 0.0 dBFS, which is the maximum value)
        """
        ...
    
    def generate(self):
        ...
    


class Sine(SignalGenerator):
    def __init__(self, freq, **kwargs) -> None:
        ...
    
    def generate(self): # -> Generator[float, Any, NoReturn]:
        ...
    


class Pulse(SignalGenerator):
    def __init__(self, freq, duty_cycle=..., **kwargs) -> None:
        ...
    
    def generate(self): # -> Generator[float, Any, NoReturn]:
        ...
    


class Square(Pulse):
    def __init__(self, freq, **kwargs) -> None:
        ...
    


class Sawtooth(SignalGenerator):
    def __init__(self, freq, duty_cycle=..., **kwargs) -> None:
        ...
    
    def generate(self): # -> Generator[float, Any, NoReturn]:
        ...
    


class Triangle(Sawtooth):
    def __init__(self, freq, **kwargs) -> None:
        ...
    


class WhiteNoise(SignalGenerator):
    def generate(self): # -> Generator[float, Any, NoReturn]:
        ...
    


