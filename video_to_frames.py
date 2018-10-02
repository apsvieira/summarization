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
from unidecode import unidecode

parser = argparse.ArgumentParser()
parser.add_argument('--num_frames',
                    metavar='N',
                    type=int,
                    help="Number of frames to extract from video")
parser.add_argument('--video',
                    metavar='video',
                    help="Source video")
parser.add_argument('--image_format',
                    choices=['.png', '.jpeg'],
                    help="Format of the output images")

if __name__ == '__main__':
    opts = parser.parse_args()
    num_frames = int(opts.num_frames)
    video_file = opts.video
    image_format = opts.image_format

    # Path to which extracted images will be saved
    # output_path = './images'
    # try:
    #     os.mkdir(output_path)
    # except FileExistsError:
    #     print("Tried to create a folder that already exists. Moving on without creating new folder.")
    #     print("Folder path:", output_path)

    # Open video file, read number of frames
    video = cv2.VideoCapture(video_file)
    video_name = unidecode(re.sub('\..*', '', video_file).replace(' ', '-'))
    total_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
    if num_frames >= total_frames:
        raise ValueError('Asked for a {} unique frames. Larger than the {} frames in the video {}.'.format(
            num_frames, total_frames, video_file
        ))

    # Generate array of random indices in semi-open range [0, total_frames)
    indices = np.random.randint(0, total_frames, num_frames)
    while not np.unique(indices).shape[0] == indices.shape[0]:
        indices = np.random.randint(0, total_frames, num_frames)

    # Move to image output directory
    # os.chdir(output_path)
    for i, index in enumerate(indices):
        # Set video frame pointer to frame 'index'
        video.set(cv2.CAP_PROP_POS_FRAMES, index)
        success, img = video.read()

        # This is a workaround for dealing with empty images.
        # This introduces a bias to get the first frames in a video.
        # TODO understand why some images are empty and how to avoid that
        count = 0
        while not success:
            video.set(cv2.CAP_PROP_POS_FRAMES, np.random.randint(0, indices.min(), 1))
            success, img = video.read()
            count += 1
            if count == 100:
                break

        out_img = 'image_' + video_name + "_" + str(i) + image_format
        cv2.imwrite(out_img, img)



