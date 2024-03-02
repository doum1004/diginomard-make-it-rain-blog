from moviepy.editor import VideoFileClip

# Define the input video file and output audio file
mp4_file = "c:/Users/alexlee/Desktop/DCIM/100MEDIA/DJI_0007.MP4"
mp3_file = "c:/Users/alexlee/Desktop/DCIM/100MEDIA/DJI_0007"

curTime = 0
cutTimeSec = 15
video_clip = VideoFileClip(mp4_file)
cnt = int(video_clip.duration / cutTimeSec)
video_clip.close()

# cut by 1/4 of the video and do the rest of the process
for i in range(cnt):
    # Load the video clip
    video_clip = VideoFileClip(mp4_file)
    # Extract the audio from the video clip
    audio_clip = video_clip.audio
    
    audio_clip = audio_clip.subclip(curTime, curTime + cutTimeSec)
    curTime += cutTimeSec

    # 44.1khz / 16 bit / mono channel / wav file
    #audio_clip.write_audiofile(f"{mp3_file}_{i}.mp3")
    audio_clip.write_audiofile(f"{mp3_file}_{i}.wav", fps=44100, nbytes=2, buffersize=2000, codec="pcm_s16le", ffmpeg_params=["-ac", "1"])

    # Close the video and audio clips
    audio_clip.close()
    video_clip.close()

print("Audio extraction successful!")