import subprocess
import sys
import json
from vosk import Model, KaldiRecognizer, SetLogLevel
import re
from datetime import timedelta
SAMPLE_RATE = 16000

SetLogLevel(-1)

model = Model("./vosk-model-small-en-us-0.15",lang="en-us")
rec = KaldiRecognizer(model, SAMPLE_RATE)
rec.SetWords(True)
def transcribe_to_srt(audio_file,srt_file):
    with subprocess.Popen(["ffmpeg", "-loglevel", "quiet", "-i",
                            audio_file,
                            "-ar", str(SAMPLE_RATE) , "-ac", "1", "-f", "s16le", "-"],
                            stdout=subprocess.PIPE).stdout as stream:

        result = str(rec.SrtResult(stream))
        with open(srt_file,'w') as f:
            f.write(result)
    offset_srt(srt_file)

# Convert SRT timestamp to timedelta
def srt_time_to_timedelta(srt_time):
    hours, minutes, seconds, milliseconds = map(int, re.split('[:,]', srt_time))
    return timedelta(hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)

# Convert timedelta back to SRT timestamp format
def timedelta_to_srt_time(td):
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    milliseconds = td.microseconds // 1000
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

# Offset SRT timestamps
def offset_srt(srt_file):
    with open(srt_file, 'r') as file:
        lines = file.readlines()

    offset = None
    new_lines = []

    for line in lines:
        match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', line)
        if match:
            start_time = match.group(1)
            end_time = match.group(2)

            # Set offset as the start time of the first line
            if offset is None:
                offset = srt_time_to_timedelta(start_time)

            # Calculate the new start and end times
            new_start_time = srt_time_to_timedelta(start_time) - offset
            new_end_time = srt_time_to_timedelta(end_time) - offset

            # Reformat and append the modified line
            new_lines.append(f"{timedelta_to_srt_time(new_start_time)} --> {timedelta_to_srt_time(new_end_time)}\n")
        else:
            new_lines.append(line)

    # Save the adjusted file
    with open(srt_file, 'w') as file:
        file.writelines(new_lines)
transcribe_to_srt("timeline6.mp3","timeline6.srt")


