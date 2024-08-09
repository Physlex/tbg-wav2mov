
import typing as ty
import typing_extensions as ty_ext # type: ignore
import dataclasses

import pydub as pd
import numpy as np

FrameDTypes = ty.Literal["float64", "float32", "int32", "int16"]

@dataclasses.dataclass(frozen=True)
class AudioFileFormat(object):
    """ Defines the File Format in place of the audio file header

    Used to describe the manner in which the audio file format stores it's audio
    data. It is effectively a replacement for the audio files 'header' section
    if the header is unavaliable.

    The formatter is only used as a parameter to the `AudioFile` class's
    constructor, and is hence useless on it's own.

    The only time in which it is recommended to supply the file format is when
    you need the file format that currently exists to be transformed into the
    specified type.

    In the case that you want to read a RAW file from disk, you must supply
    an audio file format, in which case it is reccomended that you use the
    'RawFileFormat' dataclass instead.

    Fields
    ------

    :major: The major format for the specified file (ex: RAW, WAV, WAVEx, etc)

    :subtype: The subtype of the given audio format (ex: PCM_24, PCM_16, etc)

    :endian: The endian-ness of the file format, defaulting to FILE.

    :channels: The number of channels in the file format.

    :samplerate: The samplerate of the file format.

    """

    # TODO: Use ast module to generate literal boilerplate for major
    major      : str
    subtype    : str
    channels   : int
    samplerate : int
    endian     : ty.Literal["FILE", "LITTLE", "BIG", "CPU"] = 'FILE'

@dataclasses.dataclass(frozen=True)
class RawFileFormat(AudioFileFormat):
    """ RAW file format helper Dataclass

    Exactly the same as `AudioFileFormat` but field is supplied automatically
    """

    major: str = dataclasses.field(init=False, default="RAW")

@dataclasses.dataclass
class FrameFormat(object):
    """ The format in which frames are meant to be read in

    Params
    ------

    :frames: the number of frames to read on a given instance. Leave default
    to read all frames in the given file.

    :dtype: the data type of the resultant audio wave, default is "float64"

    """

    frames : int = -1
    dtype  : FrameDTypes = "float64"

class AudioFile(object):
    """Audio file read-only mode class


    TODO: UPDATE
    This class defines implementation details for reading an audiofile from
    any format supported by the c-library `libsnd`.

    For more details, see the `__init__` defintition.

    """

    class _Reader(object):
        """ Read-Only typestate of the AudioFile class
        """

        def __init__(self, soundfile: sf.Soundfile):
            """ Creates a reader typestate variant of the AudioFile class
            """

            self._soundfile = soundfile
            self._frame_format = FrameFormat()
            pass

        def frames(self, frames: int) -> np.ndarray[ty.Any, np.dtype[ty.Any]]:
            """ Reads the frames using the specified configuration
            """

            frames = self._soundfile.read() # type: ignore
            assert type(frames) is np.ndarray[ty.Any, np.dtype[ty.Any]]
            return frames

        def close(self):
            """ Closes the soundfile
            """

            self._soundfile.close()
            pass

        @property
        def dtype(self) -> FrameDTypes:
            return self._frame_format.dtype

        @dtype.setter
        def dtype(self, val: FrameDTypes):
            self._frame_format.dtype = val
            pass

        _soundfile: sf.SoundFile
        _frame_format: FrameFormat

    class _Chunker(object):
        """ Chunked typestate of the AudioFile class

        Context manager for chunked soundfile variants

        """

        def __init__(self, soundfile: sf.SoundFile):
            """ Creates a chunker typestate variant of the AudioFile class
            """

            self._soundfile = soundfile
            pass

        def __enter__(self):
            """ ContextManager protocol entry point
            """

            return self

        def __exit__(self, *args: ty.Any):
            """ ContextManager protocol exit point
            """

            self._soundfile.close()
            pass

        _soundfile: sf.SoundFile

    def __init__(
            self,
            filename: str,
            format: ty.Optional[AudioFileFormat] = None,
    ) -> None:
        """ Create an AudioReader object

        TODO: Explain the public interface

        Parameters
        ----------

        :filename: the name of the file, appended to a path denoting where the
        file resides in memory.

        :num_channels: The number of channels residing in your audio format,
        default is 

        Examples
        -------

        >>> from ty import List, float
        >>> # Supports any audio formats listed [here](http://www.mega-nerd.com/libsndfile/)
        >>> filename: str = "test.wav"

        Capture raw audio frames using the audio reader type and 'with'

        >>> frames: List[float] = []
        >>> with AudioReader(filename) as wav: AudioWave:
        >>>     frames.append(wav.read_frame())

        Note that in both cases the audio reader is explicitly just a means of
        reading and converting an audio file in memory into an audio file format
        that is parsable from the wav2mov libraries perspective

        """

        self._filename = filename
        self._format = format

    def as_chunked(self) -> ty.Optional[_Chunker]:
        """ Specify the AudioReader as a chunker audiofile typestate
        """

        chunker = None
        try:
            chunker = self._Chunker(self._guarded_soundfile())
        except AudioException:
            raise

        return chunker

    def __enter__(self) -> _Reader:
        """ Reads audio as an AudioReader ContextManager

        Returns a reader type to process soundfiles using the standard frames
        operations. See `_Reader` class' `__init__` for more information

        """

        try:
            self._reader = self._Reader(self._guarded_soundfile())
        except AudioException:
            raise

        return self._reader

    def __exit__(self, *args: ty.Any):
        """ Implementation of exit semantics for python 'with' statement
        """
        self._reader.close()
        pass

    def _guarded_soundfile(self) -> sf.SoundFile:
        """ Creates a soundfile with guarded exception clauses

        Exceptions
        ----------

        Can throw an AudioException upon invocation, which must be handled with
        appropriately by the caller. Arguments provided are teh error and type.

        """

        soundfile = None
        try:
            match self.format:
                case None:
                    soundfile = sf.SoundFile(self.filename, 'r')
                case _:
                    soundfile = sf.SoundFile(
                        self.filename,
                        'r',
                        samplerate=self.format.samplerate,
                        channels=self.format.channels,
                        format=self.format.major,
                        subtype=self.format.subtype,
                        endian=self.format.endian
                    )
        except OSError as err:
            print("OSError: ", err)
        except sf.SoundFileError as err:
            print("SoundFileError: ", err)
        except Exception as err:
            raise AudioException(f"Unexpected {err=}, {type(err)}")
        
        assert soundfile is not None
        return soundfile

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def format(self) -> ty.Optional[AudioFileFormat]:
        return self._format

    _filename: str
    _format: ty.Optional[AudioFileFormat]

class AudioWave(object):
    """ A sampled and formatted audio wave datatype
    """

    def __init__(self):
        """ Create an AudioWave object
        """

        pass

class AudioException(Exception):
    """ Base class for all Audio Error Types
    """
    def __init__(self, *args: object):
        """ Constructs on audio exception
        """
        super().__init__(*args)

class AudioReaderError(AudioException):
    """ Audio Reader Exception class
    """
    def __init__(self, *args: object):
        """ Constructs an Audio Reader Error
        """
        super().__init__(*args)
