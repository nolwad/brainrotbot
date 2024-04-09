import praw
from Reddit import reddit
#from Graphics.screenshot import get_screenshots_of_reddit_posts
from Graphics.screenNEW import get_screenshots_of_reddit_posts_new
import config
from TextToSpeech.tts import create_tts, get_length
from TextToSpeech.textSplit import split_string
from pathlib import Path
from utils.clean_text import markdown_to_text
from utils.add_mp3_pause import add_pause
from utils.meshbody import singleTTL
from VideoEditor.videomaker import make_final_video
from VideoEditor.clipvid import split, shorten
import math
import subprocess
import time
import toml
import os, shutil
import random

def main():
    my_config = toml.load('./config.toml') #config.load_config()
    my_reddit = reddit.login()
    subredditList = [my_config['Reddit']['subreddita'],
                     my_config['Reddit']['subredditb'],
                     my_config['Reddit']['subredditc'],
                     my_config['Reddit']['subredditd'],
                     my_config['Reddit']['subreddite']]
    thread = reddit.get_thread(reddit=my_reddit, subreddit=random.choice(subredditList))
    print(my_reddit)
    print(thread)

    if thread is None:
        print('No thread found!')
        return
    else:
        print("Thread: ", thread)

    Path(f"./Assets/temp").mkdir(parents=True, exist_ok=True)
    thread_id_path = f"./Assets/temp/{thread.id}"

    # download screenshot of reddit post and its comments
    #get_screenshots_of_reddit_posts(reddit_thread=thread, reddit_comments=comments, screenshot_num=1)
    get_screenshots_of_reddit_posts_new(reddit_thread=thread, screenshot_num=1)

    # create a mp3 directory for the tts files
    Path(f"{thread_id_path}/mp3").mkdir(parents=True, exist_ok=True)
    Path(f"{thread_id_path}/mp3_clean").mkdir(parents=True, exist_ok=True)
    print("Getting mp3 files..")

    # download tts files
    thread_title = markdown_to_text(thread.title)
    title_audio_path = f'{thread_id_path}/mp3/title.mp3'
    title_audio_clean_path = f'{thread_id_path}/mp3_clean/title.mp3'
    create_tts(text=thread_title, path=title_audio_path)

    thread_text = markdown_to_text(thread.selftext)
    textArray = []
    if len(thread_text) > 2999:
        textArray = split_string(thread_text)
        for i in range(len(textArray)):
            body_audio_path = f'{thread_id_path}/mp3/body_{i}.mp3'
            body_audio_clean_path = f'{thread_id_path}/mp3_clean/body_{i}.mp3'
            create_tts(text=textArray[i], path=body_audio_path)
    else:
        create_tts(text=thread_text, path=f'{thread_id_path}/mp3_clean/body_0.mp3')

    if len(textArray) > 0:
        for i in range(len(textArray)):
            add_pause(f'{thread_id_path}/mp3/body_{i}.mp3', f'{thread_id_path}/mp3/body_clean_{i}.mp3', pause)
            ## FIND WAY TO ADD ALL BODY PARTS TO ONE THING
        for i in range(len(textArray)-1):
            singleTTL(f'{thread_id_path}/mp3_clean/body_0.mp3', f'{thread_id_path}/mp3_clean/body_0.mp3', f'{thread_id_path}/mp3/body_{i+1}.mp3')

    # for using comments
    #for idx, comment in enumerate(comments):
    #    path = f"{thread_id_path}/mp3/{idx}.mp3"
    #    comment_body = markdown_to_text(comment.body)
    #    create_tts(text=comment_body, path=path)

    # make sure the tts of the title and comments don't exceed the total duration
    total_video_duration = my_config['VideoSetup']['max_video_duration']
    pause = my_config['VideoSetup']['pause']
    current_video_duration = 0

    tts_title_path = f'{thread_id_path}/mp3/title.mp3'
    title_duration = get_length(path=tts_title_path)
    current_video_duration += title_duration + pause

    tts_body_path = f'{thread_id_path}/mp3_clean/body_0.mp3'
    body_duration = get_length(path=tts_body_path)
    current_video_duration += body_duration + pause
    print("MP3 Duration:", current_video_duration)

    #list_of_number_of_comments = list(range(len(comments)))

    #comments_audio_path = []
    #comments_audio_clean_path = []
    #comments_image_path = []
    #for i in list_of_number_of_comments:
    #    comment_audio_path = f'{thread_id_path}/mp3/{i}.mp3'
    #    comment_audio_clean_path = f'{thread_id_path}/mp3_clean/{i}.mp3'
    #    comment_image_path = f'{thread_id_path}/png/{i}.png'
    #    comment_duration = get_length(comment_audio_path)

    #    if current_video_duration + comment_duration + pause <= total_video_duration:
    #        comments_audio_path.append(comment_audio_path)
    #        comments_audio_clean_path.append(comment_audio_clean_path)
    #        comments_image_path.append(comment_image_path)
    #        current_video_duration += comment_duration + pause

    title_image_path = f'{thread_id_path}/png/title.png'
    body_image_path = f'{thread_id_path}/png/body.png'

    # convert the pause(in seconds) into milliseconds
    mp3_pause = pause * 1000
    add_pause(title_audio_path, title_audio_clean_path, mp3_pause)

    #comments_combined = list(zip(comments_audio_path, comments_audio_clean_path))
    #for input_path, output_path in comments_combined:
    #    add_pause(input_path, output_path, mp3_pause)

    # create final video
    Path("./Results").mkdir(parents=True, exist_ok=True)

    body_audio_clean_path = f'{thread_id_path}/mp3_clean/body_0.mp3'
    
    make_final_video(title_audio_path=title_audio_clean_path,
                     body_audio_path=body_audio_clean_path,
                     title_image_path=title_image_path,
                     body_image_path=body_image_path,
                     length=math.ceil(current_video_duration),
                     reddit_id=thread.id,
                     duration=current_video_duration
                     )
    
    print("Duration: ", current_video_duration)

    maxLength = my_config['VideoSetup']['max_video_duration']
    if current_video_duration < maxLength - 2:
        shorten(thread, current_video_duration)

    if current_video_duration > maxLength:
        split(thread, current_video_duration, maxLength)

    if my_config['App']['upload_to_youtube']:
        upload_file = f'./Results/{thread.id}.mp4'
        directory_path = my_config['Directory']['path']
        cmd = ['python', f'{directory_path}/Youtube/upload.py', '--file', upload_file, '--title',
               f'{thread_title}', '--description', f'{thread_title}']
        subprocess.run(cmd)

if __name__ == '__main__':
    my_config = config.load_config()
    while True:
        print('Starting ..........\n')
        main()

        if os.path.isdir("./Assets/Temp"):
            shutil.rmtree("./Assets/Temp")

        print('\n-------------------------------------------\n')
        break #remove this if wanting to continually run
        time.sleep(my_config['App']['run_every'])


