"""This file implements a toy example of basic usage of the wav2mov system
"""

import wav2mov as wm

PATH: str = "examples/assets/wav_track.wav"

if __name__ == "__main__":

    ## Normal Operation

    with wm.AudioFile(PATH) as wav_reader:
        wav_reader.frames().process_with(lambda | Some function goes here |)
        pass

    ## With a format

    format = wm.AudioFileFormat("WAV", "PCM_32", 1, 144000)
    with wm.AudioFile(PATH, format) as wav_formatted_reader:
        wav_formatted_reader.frames().process_with(lambda | Some function goes here|)
        pass

    ## Chunked Reading

    with wm.AudioFile(PATH).as_chunked() as wav_chunker:
        wav_chunker.chunk().frames().process_with(lambda | Some Function Goes Here |)
        pass

    pass
