import math
import os

from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

def shorten(thread, duration):
    ffmpeg_extract_subclip(f'./Results/{thread}.mp4', 0, duration + 2, targetname=f'./Results/{thread}_short.mp4')
    os.remove(f'./Results/{thread}.mp4')

def split(thread, duration, maxLength):
    num_videos = math.ceil(duration / maxLength)
    splitLength = duration / num_videos
    for i in range(num_videos):
        clip_start = i * splitLength
        clip_end = (i +1) * splitLength
        ffmpeg_extract_subclip(f'./Results/{thread}.mp4', clip_start, clip_end, targetname=f'./Results/{thread}_{i}.mp4')
    os.remove(f'./Results/{thread}.mp4')
    #finalLength = length % 60
    #f_clip_start = num_videos * 60
    #shorten(finalLength, thread, f_clip_start)