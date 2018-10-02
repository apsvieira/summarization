"""Extract random frames from video files using OpenCV.

Generate list of frame indices from 0 to num_frames.
Get each frame from list of indices and save that frame to disk as an
image. All frames for a video are saved in the same folder.
"""
import os
import re
import argparse

import cv2
import numpy as np
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument('--num_frames',
                    metavar='N',
                    help="Number of frames to extract from video")
parser.add_argument('--video',
                    metavar='video',
                    help="Source video")

if __name__ == '__main__':
    opts = parser.parse_args()
    num_frames = int(opts.num_frames)
    video_file = opts.video

    # Path to which extracted images will be saved
    output_path = './images_' + re.sub('\..*', '', video_file)
    try:
        os.mkdir(output_path)
    except FileExistsError:
        print("Tried to create a folder that already exists. Moving on without creating new folder.")
        print("Folder path:", output_path)

    # Open video file, read number of frames
    video = cv2.VideoCapture(video_file)
    total_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)

    # Generate array of random indices in semi-open range [0, total_frames)
    indices = np.random.randint(0, total_frames, num_frames)
    while not np.unique(indices).shape[0] == indices.shape[0]:
        indices = np.random.randint(0, total_frames, num_frames)

    os.chdir(output_path)
    for i, index in enumerate(tqdm(indices)):
        video.set(cv2.CAP_PROP_POS_FRAMES, index)
        success, img = video.read()
        out_img = 'image_' + str(i) + '.png'
        cv2.imwrite(out_img, img)


