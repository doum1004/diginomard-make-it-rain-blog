import os
import random
import re
import time
import moviepy.editor as mpy
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip

# output folder
outputDir = "C:/Workspace/Personal/video_photo/output/video/"
audioDir1 = "C:/Workspace/Personal/video_photo/audio/bgm/"
audioDir2 = "C:/Workspace/Personal/video_photo/audio/narration/1/"
fontPath = "C:/Workspace/Personal/video_photo/fonts/HakgyoansimJiugaeR.ttf"
#print(TextClip.list('font'))
limitVideoDuration = 5


def file_to_subtitles(filename):
    """ Converts a srt file into subtitles.

    The returned list is of the form ``[((ta,tb),'some text'),...]``
    and can be fed to SubtitlesClip.

    Only works for '.srt' format for the moment.
    """
    times_texts = []
    current_times = None
    current_text = ""
    with open(filename,'r',encoding="utf8") as f:
        for line in f:
            times = re.findall("([0-9]*:[0-9]*:[0-9]*,[0-9]*)", line)
            if times:
                current_times = [cvsecs(t) for t in times]
            elif line.strip() == '':
                times_texts.append((current_times, current_text.strip('\n')))
                current_times, current_text = None, ""
            elif current_times:
                current_text += line
    return times_texts

def addSubtitle2(videoFile, srtFilePath):
    video = VideoFileClip(videoFile)

    generator = lambda txt: TextClip(txt, font='Gulim-&-GulimChe-&-Dotum-&-DotumChe', fontsize=50, color='white', method='caption', size=(1920, 1080))
    subs = SubtitlesClip(getTimeTexts(srtFilePath), generator).set_position('center','bottom').set_duration(video.duration-5)

    result = CompositeVideoClip([video, subs])

    videoFileName = os.path.basename(videoFile)
    videoFileName = videoFileName.split(".")[0] + "_subtitle2.mp4"
    videoFile = outputDir + videoFileName
    result.write_videofile(videoFile)


def getTimeTexts(srtFilePath):
    lines = []
    with open(srtFilePath, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    times_texts = []
    for i in range(0, len(lines), 4):
        times = []
        startSec = lines[i+1].split(" --> ")[0].split(":")
        startSec = int(startSec[0])*3600 + int(startSec[1])*60 + float(startSec[2].replace(",", "."))
        times.append(startSec)

        endSec = lines[i+1].split(" --> ")[1].split(":")
        endSec = int(endSec[0])*3600 + int(endSec[1])*60 + float(endSec[2].replace(",", "."))
        times.append(endSec)

        subtitle = lines[i+2].strip()
        times_texts.append((times, subtitle))
    return times_texts


def addSubtitle(videoFile, srtFilePath):
    # read srt file
    timeTexts = getTimeTexts(srtFilePath)
    
    # get video clip        
    clip = mpy.VideoFileClip(videoFile)
    clipDuration = clip.duration
    for i in range(len(timeTexts)):
        if timeTexts[i][0][0] > clipDuration:
            break

        if timeTexts[i][0][1] > clipDuration:
            timeTexts[i][0][1] = clipDuration

        # get subtitle text
        txt = mpy.TextClip(timeTexts[i][1], fontsize=50, font='Batang-&-BatangChe-&-Gungsuh-&-GungsuhChe', color='white', method='caption', size=(1920, 1080))
        # set position and duration
        txt = txt.set_position(('center', 'bottom')).set_duration(timeTexts[i][0][1] - timeTexts[i][0][0])
        # add subtitle to video
        clip = mpy.CompositeVideoClip([clip, txt.set_start(timeTexts[i][0][0])])

    # save video
    # rename video file
    videoFileName = os.path.basename(videoFile)
    videoFileName = videoFileName.split(".")[0] + "_subtitle.mp4"
    videoFile = outputDir + videoFileName
    
    clip.write_videofile(videoFile, threads=32, fps=30, codec='libx264', preset='ultrafast', audio=True)

addSubtitle2("c:/Workspace/Personal/video_photo/output/video/231028_Longil_vlog_4.mp4", 'c:/Users/alexlee/Downloads/test.srt')