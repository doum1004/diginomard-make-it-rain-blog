import os
import random
import time
import moviepy.editor as mpy
from moviepy.editor import *
from moviepy.audio.fx.all import audio_fadeout
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

# output folder
outputDir = "C:/Workspace/Personal/video_photo/output/video/"
audioDir = "C:/Workspace/Personal/video_photo/audio/"

def get_folder_paths(absolute_path):
    paths = []
    while True:
        parent_dir = os.path.dirname(absolute_path)
        if parent_dir == absolute_path:
            break
        baseName = os.path.basename(absolute_path)
        if baseName:
            paths.append(baseName)
        absolute_path = parent_dir
    paths.reverse()
    return paths

# add subtitle to video
def add_subtitle(video, subtitle, saveVideoPath):
    clip = mpy.VideoFileClip(video)
    txt = mpy.TextClip(subtitle, fontsize=24, color='white')
    txt = txt.set_position(('center', 'bottom')).set_duration(clip.duration)
    final_clip = mpy.CompositeVideoClip([clip, txt])
    final_clip.write_videofile(saveVideoPath, threads=4, fps=30, codec='libx264', preset='slow', audio=False)
    print(f"Video saved as {saveVideoPath}")
    return saveVideoPath

def check4K(videoPath):
    parser = createParser(videoPath)
    metadata = extractMetadata(parser)
    if 'resolution' in metadata and metadata.get('resolution') == '4K':
        return True
    if metadata.get('width') >= 3840 and metadata.get('height') >= 2160:
        return True
    # if metadata.get('height') >= 3840 and metadata.get('width') >= 2160:
    #     return True
    return False

def getDefaultSize(videos):
    for video in videos:
        if check4K(video):
            return [3840, 2160]
    return [1920, 1080]

# combine videos and save
def combine_videos(videos, audios, saveTitle, logoImgPath = '', titleString = '', fadeoutTime = 4):
    clips = []
    loggings = []
    defaultSize = getDefaultSize(videos)
    for video in videos:
        fileNameWithoutExt = os.path.splitext(video)[0]

        clip = mpy.VideoFileClip(video)
        # read metadata and print all
        #print(video, clip.reader.infos)
        applyMargin = False
        if clip.rotation in (90, 270):
            #clip = clip.resize(clip.reader.infos['video_size'][::-1])
            clip = clip.resize(clip.size[::-1])
            clip.rotation = 0
            applyMargin = True
        elif clip.size[1] > defaultSize[1]:
            applyMargin = True
        clip = clip.resize(height=defaultSize[1])
        # using margin left to make it center (it is on the left side)
        if applyMargin:
            clip = clip.margin(left=(defaultSize[0] - clip.size[0]) // 2)

        originDuration = clip.duration
        option = []

        # option cut
        if "_cut" in fileNameWithoutExt:
            cutStart = 0
            cutEnd = clip.duration
            if "_cutStart" in fileNameWithoutExt:
                cutStart = int(fileNameWithoutExt.split("_cutStart")[1].split("_")[0])
            if "_cutEnd" in fileNameWithoutExt:
                cutEnd = int(fileNameWithoutExt.split("_cutEnd")[1].split("_")[0])
            clip = clip.subclip(cutStart, cutEnd)
            option.append(f'cut ({cutStart}-{cutEnd}) sec.')

        # option fastX
        fastX = 1
        if "_fastX" not in fileNameWithoutExt:
            if clip.duration > 30:
                fastX = 1.6
        else:
            # take it number from here in the name ex) _fastX2_...
            fastX = float(fileNameWithoutExt.split("_fastX")[1].split("_")[0])
        if fastX != 1:
            clip = clip.fx(vfx.speedx, fastX)
            option.append(f'{fastX}x faster.')

        if "_nolimit" not in fileNameWithoutExt:
            limit = 25
            if clip.duration > limit:
                clip = clip.subclip(0, limit)
                option.append(f'limit by {limit} sec.')

        if "_mute" in fileNameWithoutExt:
            clip = clip.without_audio()
            option.append(f'mute.')

        log = f"{video} {clip.size}. {clip.duration:.2f} sec (og: {originDuration:.2f}). {option}"
        print(log)
        loggings.append(log)

        clips.append(clip)

    final_clip = mpy.concatenate_videoclips(clips)#, method='compose')
    #final_clip = final_clip.resize(defaultSize)
    final_clip = final_clip.volumex(0.5)
    print(f"Final Clip Size: {final_clip.size}, Duration: {final_clip.duration}")
    #totalLength = sum([clip.duration for clip in clips])

    acceptedAudios = []
    if audios:
        # set audio clip from audios (till exceed totalLength)
        audioLength = 0
        audio_clips = []
        for audio in audios:
            acceptedAudios.append(audio)
            audio_clip = mpy.AudioFileClip(audio)
            audio_clips.append(audio_clip)
            audioLength += audio_clip.duration
            if audioLength > final_clip.duration:
                break        
        audio_clip = mpy.concatenate_audioclips(audio_clips)
        audio_clip = audio_clip.audio_loop(duration=final_clip.duration)
        audio_clip = audio_clip.volumex(0.5)
        audio_clip = audio_clip.fx(audio_fadeout, duration=fadeoutTime)
        # Combine original video audio with external audio
        final_audio = mpy.CompositeAudioClip([audio for audio in [final_clip.audio, audio_clip] if audio is not None])
        # Set the mixed audio to the final video
        final_clip = final_clip.set_audio(final_audio)

    # save logo position and margin to reuse title position        
        
    textMargin = [25, 75]
    if logoImgPath:
        logo = (mpy.ImageClip(logoImgPath)
                .set_duration(final_clip.duration)
                .set_position(('left', 'top'))
                .resize(height=95) # if you need to resize...
                .margin(left=80, top=50, opacity=0)) # (optional) logo-border padding
        # get logo size and position to reuse title position
        textMargin[0] = logo.size[0] + 10
        final_clip = mpy.CompositeVideoClip([final_clip, logo])
        
    if titleString: # title on next to logo. give width 40% of the screen. Stroke color black and width 2
        #txt_clip = mpy.TextClip(titleString, fontsize=36, color='white', font='Arial-Bold')
        txt_clip = mpy.TextClip(titleString, fontsize=36, color='white', font='Arial-Bold')
        txt_clip = txt_clip.set_position(('left', 'top')).set_duration(final_clip.duration)
        txt_clip = txt_clip.margin(left=textMargin[0], top=textMargin[1], opacity=0)
        final_clip = mpy.CompositeVideoClip([final_clip, txt_clip])
        
    #fade out video screen at the end (3sec)
    final_clip = final_clip.fx(vfx.fadeout, fadeoutTime)
    final_clip = final_clip.fx(audio_fadeout, duration=fadeoutTime)
    ## if input video is 4k or more, write it in 4k resolution. Otherwise, use 2k resolution.
    saveVideoPath = outputDir + saveTitle + f".mp4"
    #final_clip.write_videofile(saveVideoPath, threads=32, fps=30, codec='libx264', preset='slow', audio=True)
    final_clip.write_videofile(saveVideoPath, threads=32, fps=30, codec='libx264', preset='ultrafast', audio=True)
    
    saveTextPath = outputDir + saveTitle + ".txt"

    # write which video and audios are used. And print loggings
    with open(saveTextPath, "w") as f:
        # write total duration
        f.write(f"Total length: {final_clip.duration} sec\n")
        f.write(f"Videos used in the clip:\n")
        for logging in loggings:
            f.write(f"{logging}\n")
        f.write(f"Audios used in the clip:\n")
        for audio in acceptedAudios:
            f.write(f"{audio}\n")        

    print(f"Video saved as {saveVideoPath} and text saved as {saveTextPath}")
    return saveVideoPath, saveTextPath

def mediaCreatedTime(videoPath):
    parser = createParser(videoPath)
    metadata = extractMetadata(parser)
    return metadata.get('creation_date')

def gereateVideo(dirPath, title, overwriteForce=False):
    # get current time
    start_time = time.time()
    
    # get all mp4 from the directory case insensitive (lower and upper) and ignore file starts with ".". And make a order by date    
    videos = [dirPath + '/' + video for video in os.listdir(dirPath) if video.lower().endswith(".mp4") and not os.path.splitext(video)[0].endswith("__") and not video.lower().startswith(".")]
    # sort by "Media Created" date (not file creation date)
    videos.sort(key=lambda x: mediaCreatedTime(x))
        
    if len(videos) == 0:
        print("No videos found in the directory.")
        exit()

    # use os to get dir name (last and second last)
    dirNames = get_folder_paths(dirPath)
    savetitle = dirNames[-2] + "_" + dirNames[-1]
    saveVideoPath = outputDir + savetitle + ".mp4"
    print(saveVideoPath)

    # if exist, stop
    i = 0
    while not overwriteForce and os.path.exists(saveVideoPath):
        # if exist ask overwrite or not. if y break
        overwrite = input("File already exist. Do you want to overwrite? (y/n): ")
        if overwrite.lower() == "y":
            break
        i += 1
        savetitle = dirNames[-2] + "_" + dirNames[-1] + f"_{i}"
        saveVideoPath = outputDir + savetitle + f".mp4"

    # get list of mp3 files from audioDir (absolute path)
    audios = [audioDir + audio for audio in os.listdir(audioDir) if (audio.lower().endswith(".mp3") or audio.lower().endswith(".mov")) and not audio.lower().startswith(".")]
    random.shuffle(audios)

    combine_videos(videos, audios, savetitle, 'C:/Workspace/Personal/video_photo/logo/logo12.png', '| ' + title)
    end_time = time.time()
    print(f"Total time: {end_time - start_time:.2f} sec")
    
# Idea sharing (mono cam)
# 1. Combine videos with audio (If clip exceeds 30 sec, speed up 1.5x. And if clip exceeds 25 sec, cut it to 25 sec.)
# 2. Output_1 to Mac final cut pro
# 3. Get transcription from video audio with timestamps
# 4. Add subtitle to video
# 5. Output_2 to Mac final cut pro
# 6. 
    
    
# if __name__ == '__main__':
#     dataList = [("D:/Photo_Video/230429_Boucherville_Ikea/vlog", "Boucherville Ikea"),
#             ("D:/Photo_Video/230507_Montreal_Daily/vlog", "Montreal Daily"),
#             ("D:/Photo_Video/230514_St Helen's Island/vlog", "Montreal St Helen's Island"),
#             ("D:/Photo_Video/230805_VanisEnQuebec/vlog", "Vanis En Quebec"),
#             ("D:/Photo_Video/230812_Chambly/vlog", "Chambly"),
#             ("D:/Photo_Video/230826_Oka/vlog", "Oka Park")]
#     for values in dataList:
#         try:
#             gereateVideo(values[0], values[1], True)
#         except Exception as e:
#             print(f"Error occured in {dir}\n{e}")
#             continue

if __name__ == '__main__':
    # arg 1 for path arg 2 for title
    args = sys.argv
    if len(args) < 3:
        print("Please provide directory path and title")
        exit()
    dirPath = args[1]
    title = args[2]
    gereateVideo(dirPath, title)