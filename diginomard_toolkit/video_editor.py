import moviepy.editor as mpy

vcodec =   "libx264"
videoquality = "24"
# slow, ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
compression = "slow"
loadtitle = "video" + '.mp4'

# modify these start and end times for your subclips
# cuts = [('00:00:02.949', '00:00:04.152'),
#         ('00:00:06.328', '00:00:13.077')]


def edit_video(loadtitle):
    # load file
    video = mpy.VideoFileClip(loadtitle)

    # get playtime
    duration = video.duration
    
    # create 3sec cuts (max 10 cuts) don't exceed duration, and well divide the time.
    sec = 3
    offsetSec = 1
    maxCuts = 10
    nbCuts = max(int((sec + offsetSec) / duration), maxCuts)

    cuts = []
    for i in range(nbCuts):
        start = i * (duration / nbCuts)
        end = start + sec
        if end > duration:
            end = duration
        cuts.append((start, end))
    
    # cut file
    for i in range(len(cuts)):
        clip = video.subclip(cuts[i][0], cuts[i][1])
        clips = []
        clips.append(clip)

        # remove sounds        
        final_clip = mpy.concatenate_videoclips(clips)
        final_clip = final_clip.without_audio()

        # # add text
        # txt = mpy.TextClip('Please Subscribe!', font='Courier',
        #                    fontsize=120, color='white', bg_color='gray35')
        # txt = txt.set_position(('center', 0.6), relative=True)
        # txt = txt.set_start((0, 3)) # (min, s)
        # txt = txt.set_duration(4)
        # txt = txt.crossfadein(0.5)
        # txt = txt.crossfadeout(0.5)

        # final_clip = mpy.CompositeVideoClip([final_clip, txt])

        # save file
        savetitle = f"{loadtitle.split('.')[0]}_{i}.mp4"
        final_clip.write_videofile(savetitle, threads=4, fps=24,
                                codec=vcodec,
                                preset=compression,
                                ffmpeg_params=["-crf",videoquality])

    video.close()


if __name__ == '__main__':
    edit_video(loadtitle)