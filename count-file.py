import os

kf_folder = 'D:/CS/2023 HCM AI CHALLENGE/keyframes'
clip_folder = 'D:/CS/2023 HCM AI CHALLENGE/clip-features-vit-b32'

clips = []
for clip in os.listdir(clip_folder):
    clip = clip[:-4]
    clips.append(clip)


for kf in os.listdir(kf_folder):
    if kf not in clips:
        print(kf)