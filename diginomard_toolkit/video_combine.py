import os
import random
import time
from optparse import OptionParser
import moviepy.editor as mpy
from moviepy.editor import *
from moviepy.audio.fx.all import audio_fadeout
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from skimage.filters import gaussian # pip install scikit-image

# output folder
outputDir = "C:/Workspace/Personal/video_photo/output/video/"
audioDir1 = "C:/Workspace/Personal/video_photo/audio/bgm/"
audioDir2 = "C:/Workspace/Personal/video_photo/audio/narration/1/"

def getVideoFileClip(videoFilePath, defaultSize, loggings = []):
    fileNameWithoutExt = os.path.splitext(videoFilePath)[0]
    clip = mpy.VideoFileClip(videoFilePath)

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
        if options.fastFrom != 0 and clip.duration > options.fastFrom:
            fastX = 1.6
    else:
        # take it number from here in the name ex) _fastX2_...
        fastX = float(fileNameWithoutExt.split("_fastX")[1].split("_")[0])
    if fastX != 1:
        clip = clip.fx(vfx.speedx, fastX)
        option.append(f'{fastX}x faster.')

    if options.limitSec != 0 and "_nolimit" not in fileNameWithoutExt:
        limit = options.limitSec
        if clip.duration > limit:
            clip = clip.subclip(0, limit)
            option.append(f'limit by {limit} sec.')

    if "_mute" in fileNameWithoutExt:
        clip = clip.without_audio()
        option.append(f'mute.')

    log = f"{videoFilePath} {clip.size}. {clip.duration:.2f} sec (og: {originDuration:.2f}). {option}"
    print(log)
    loggings.append(log)
    return clip

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

def getOutputPathWithoutExt(folderPath):
    paths = []
    while True:
        parent_dir = os.path.dirname(folderPath)
        if parent_dir == folderPath:
            break
        baseName = os.path.basename(folderPath)
        if baseName:
            paths.append(baseName)
        folderPath = parent_dir
    paths.reverse()
    
    savetitle = paths[-2] + "_" + paths[-1]
    saveVideoPath = outputDir + savetitle + ".mp4"

    # if exist, stop
    i = 0
    overwriteAnswer = ""
    while os.path.exists(saveVideoPath):
        # if exist ask overwrite or not. if y break
        if overwriteAnswer == "":
            overwriteAnswer = input(f"File {saveVideoPath} already exist. Do you want to overwrite? (y/n): ")
            if overwriteAnswer.lower() == "y":
                break
        i += 1
        savetitle = paths[-2] + "_" + paths[-1] + f"_{i}"
        saveVideoPath = outputDir + savetitle + f".mp4"
    return savetitle

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

def blur(image):
    """ Returns a blurred (radius=2 pixels) version of the image """
    return gaussian(image.astype(float), sigma=2)

def pinkFilter(clip):
    # Create a pink color (alpha) clip with the same size and duration as the video 
    pink_clip  = ColorClip(size=clip.size, color=[250, 210, 225], duration=clip.duration)
    # Composite the pink color clip on top of the original video (alpha .3)
    return CompositeVideoClip([clip, pink_clip.set_duration(clip.duration).set_opacity(0.3)])

def cinematicRatio(clip: mpy.VideoFileClip): # 21:9
    return clip.crop(x1=0, x2=clip.w, y1=clip.h*0.125, y2=clip.h*0.875)    

# save video
def save_video(saveTitle, clip, loggings):
    saveVideoPath = outputDir + saveTitle + f".mp4"
    clip.write_videofile(saveVideoPath, threads=32, fps=30, codec='libx264', preset='ultrafast', audio=True)
    #final_clip.write_videofile(saveVideoPath, threads=32, fps=30, codec='libx264', preset='slow', audio=True)
    
    saveTextPath = outputDir + saveTitle + ".txt"

    # write which video and audios are used. And print loggings
    with open(saveTextPath, "w") as f:
        # write total duration
        f.write(f"Total length: {clip.duration} sec/n")
        for logging in loggings:
            f.write(f"{logging}/n")

    print(f"Video saved as {saveVideoPath} and text saved as {saveTextPath}")
    return saveVideoPath, saveTextPath

# combine videos and save
def combine_videos(saveTitle, videos):
    start_time = time.time()
    clips = []
    loggings = []
    defaultSize = getDefaultSize(videos)
    for video in videos:
        clips.append(getVideoFileClip(video, defaultSize, loggings))
    
    final_clip = mpy.concatenate_videoclips(clips)#, method='compose')
    final_clip = final_clip.resize(defaultSize)
    if options.applyFilter:
        print("Applying pink filter to the video.")
        final_clip = final_clip.fx(vfx.colorx, 0.7)
        final_clip = pinkFilter(final_clip)
    if options.cinemaRatio:
        print("Applying cinema ratio to the video.")
        final_clip = cinematicRatio(final_clip)

    print(f"Final Clip Size: {final_clip.size}, Duration: {final_clip.duration}")
    save_video(saveTitle, final_clip, loggings)
    end_time = time.time()
    print(f"Total time: {end_time - start_time:.2f} sec (begin: {start_time:.2f}, end: {end_time:.2f} sec)")


# combine videos and save
def combine_videos2(saveTitle, videos, audios, logoImgPath = '', titleString = '', fadeoutTime = 4):
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
            limit = limitVideoDuration
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
    final_clip = final_clip.fx(vfx.colorx, 0.7)
    final_clip = pinkFilter(final_clip)
    final_clip = cinematicRatio(final_clip)
    
    #final_clip = final_clip.resize(defaultSize)
    #final_clip = final_clip.volumex(0.5)
    final_clip = final_clip.without_audio()
    print(f"Final Clip Size: {final_clip.size}, Duration: {final_clip.duration}")
    #totalLength = sum([clip.duration for clip in clips])

    if audios:
        # set audio clip from audios (till exceed totalLength)
        audioLength = 0
        audio_clips = []
        for audio in audios:
            audio_clip = mpy.AudioFileClip(audio)
            loggings.append(f"{audio} {audio_clip.duration:.2f} sec")
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
        f.write(f"Total length: {final_clip.duration} sec/n")
        f.write(f"Videos used in the clip:/n")
        for logging in loggings:
            f.write(f"{logging}/n")
        f.write(f"Audios used in the clip:/n")
        for audio in acceptedAudios:
            f.write(f"{audio}/n")        

    print(f"Video saved as {saveVideoPath} and text saved as {saveTextPath}")
    return saveVideoPath, saveTextPath

def mediaCreatedTime(videoPath):
    parser = createParser(videoPath)
    metadata = extractMetadata(parser)
    return metadata.get('creation_date')

def gereateVideo(dirPath, title, overwriteForce=False):
    videos = getVideoFiles(dirPath)
    audios = getAudioFiles(audioDir2)
    savetitle = getOutputPathWithoutExt(dirPath)
    #combine_videos(savetitle, videos, audios, 'C:/Workspace/Personal/video_photo/logo/logo12.png', '| ' + title)
    combine_videos(savetitle, videos, audios)#, 'C:/Workspace/Personal/video_photo/logo/logo12.png', '| ' + title)

def isVideoFile(videoPath):
    videoPath = videoPath.lower()
    if not videoPath.endswith(".mp4") and not videoPath.endswith(".mov"):
        return False
    if os.path.splitext(videoPath)[0].endswith("__") or videoPath.startswith("."):
        return False
    return True

def getVideoFiles(dirPath):
    videos = [dirPath + '/' + video for video in os.listdir(dirPath) if isVideoFile(video)]
    videos.sort(key=lambda x: mediaCreatedTime(x))
    if len(videos) == 0:
        print("No videos found in the directory.")
        exit()
    return videos

def isAudioFile(audioPath):
    audioPath = audioPath.lower()
    if not audioPath.endswith(".mp3"):
        return False
    if os.path.splitext(audioPath)[0].endswith("__") or audioPath.startswith("."):
        return False
    return True
    
def getAudioFiles(dirPath):
    # get list of mp3 files from audioDir (absolute path)
    audios = [audioDir2 + audio for audio in os.listdir(audioDir2) if isAudioFile(audio)]
    random.shuffle(audios)
    return audios

def runCombineVideosFromDir(dirPath):
    videoFiles = getVideoFiles(dirPath)
    savetitle = getOutputPathWithoutExt(dirPath)
    combine_videos(savetitle, videoFiles)

def runCombineVideosFromFiles(videoFiles):
    if len(videoFiles) == 0:
        print("No video files found.")
        exit()
    for video in videoFiles:
        if not isVideoFile(video):
            print(f"{video} is not a video file.")
            exit()
    savetitle = getOutputPathWithoutExt(videoFiles[0].split(".")[0])
    combine_videos(savetitle, videoFiles)

parser = OptionParser()
if __name__ == '__main__':
    # ex) python video_combine.py -l 5 "c:/Users/alexlee/Desktop/240303_HouseViewing/DJI_0013.MP4" "c:/Users/alexlee/Desktop/240303_HouseViewing/DJI_0014.MP4"
    # arg 1 for path(could be dir or file)
    # options like --limitSec 5 --fastFrom 30
    parser.add_option("-l", "--limitSec", dest="limitSec", action="store", default=20, type=float, help="limit video duration")
    parser.add_option("-f", "--fastFrom", dest="fastFrom", action="store", default=30, type=float, help="fast from this duration")
    parser.add_option("-a", "--applyFilter", dest="applyFilter", action="store_true", default=False, help="Apply filter to the video.")    
    parser.add_option("-c", "--cinemaRatio", dest="cinemaRatio", action="store_true", default=False, help="Apply cinema ratio to the video.")

    (options, args) = parser.parse_args()

    dirPath = args[0]
    if os.path.isdir(dirPath):
        runCombineVideosFromDir(dirPath)
    else:
        runCombineVideosFromFiles(args[:])
