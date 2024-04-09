from pydub import AudioSegment
import os


def singleTTL(input_path, output_path, next_path):

    original_file = AudioSegment.from_mp3(input_path)
    next_file = AudioSegment.from_mp3(next_path)
    combined_file = original_file + next_file
    os.remove(output_path)

    combined_file.export(output_path, format="mp3")