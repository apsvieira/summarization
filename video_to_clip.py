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

import utils

parser = argparse.ArgumentParser()
parser.add_argument('--num_frames',
                    metavar='N',
                    type=int,
                    help="Number of frames to extract from video per clip")
parser.add_argument('--num_clips',
                    metavar='C',
                    type=int,
                    help="Number of clips to extract from video")
parser.add_argument('--video',
                    metavar='video',
                    help="Source video")
parser.add_argument('--image_format',
                    choices=['.png', '.jpeg'],
                    help="Format of the output images")
parser.add_argument('--output_path',
                    type=os.path.abspath,
                    help="Path where output images will be saved")


class ClipReader:
    """Wrapper around OpenCV-based functions."""
    def __init__(self, original_video, first_frame, num_frames):
        self.video = original_video
        self.num_frames = num_frames
        self._update_boundaries(first_frame)
        self._get_valid_first_frame()

    def _get_valid_first_frame(self):
        """Find a valid first frame to start clip.

        This is a workaround for dealing with empty images.
        This introduces a bias to get the first frames in a video.
        """
        self.video.set(cv2.CAP_PROP_POS_FRAMES, self.first_frame)
        new_first_frame = self.first_frame
        success, img = self.video.read()

        while not success:
            new_first_frame = np.random.randint(0, self.first_frame, 1)
            video.set(cv2.CAP_PROP_POS_FRAMES, new_first_frame)
            success, img = self.video.read()

        self._update_boundaries(new_first_frame)

    def _update_boundaries(self, first_frame):
        self.first_frame = first_frame
        self.last_frame = self.first_frame + self.num_frames

    def get_frame(self):
        if self.video.get(cv2.CAP_PROP_POS_FRAMES) < self.last_frame:
            _, img = self.video.read()
            return img
        else:
            raise ValueError("Tried to access a frame that does not belong to this clip.")

    def get_clip(self):
        imgs = []
        self.video.set(cv2.CAP_PROP_POS_FRAMES, self.first_frame)
        for i in range(self.num_frames):
            img = self.get_frame()
            imgs.append(img)

        print(len(imgs))

        return imgs


if __name__ == '__main__':
    opts = parser.parse_args()
    num_clips = opts.num_clips
    num_frames = opts.num_frames
    video_file = opts.video
    image_format = opts.image_format
    output_path = opts.output_path

    # Open video file, read number of frames
    video = cv2.VideoCapture(video_file)
    video_name = unidecode(re.sub('\..*', '', video_file).replace(' ', '-'))
    total_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
    if num_frames >= total_frames:
        raise ValueError('Asked for {} unique frames. Larger than the {} frames in video {}.'.format(
            num_frames, total_frames, video_file
        ))

    # Generate array of random indices in semi-open range [0, total_frames - num_frames)
    indices = np.random.randint(0, total_frames - num_frames, num_clips)
    while not np.unique(indices).shape[0] == indices.shape[0]:
        indices = np.random.randint(0, total_frames, num_frames)

    # Save images output directory
    for i, index in enumerate(indices):
        clip_name = 'clip_' + str(i)
        utils.create_folder(os.path.join(output_path, clip_name))
        clip = ClipReader(video, index, num_frames)
        imgs = clip.get_clip()

        for j, img in enumerate(imgs):
            out_img = 'image_' + str(j) + image_format
            cv2.imwrite(os.path.join(output_path, clip_name, out_img), img)



