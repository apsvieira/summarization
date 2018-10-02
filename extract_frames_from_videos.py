"""Extract frames from each video in each subdirectory of current directory."""
import argparse
import logging
import os
from subprocess import Popen, PIPE
# TODO add multiprocessing support

parser = argparse.ArgumentParser()
parser.add_argument('--frames',
                    type=int,
                    help="Number of frames to extract from each video")
parser.add_argument('--image_format',
                    choices=['.png', '.jpeg'],
                    help="Format of the output images")

if __name__ == '__main__':
    opts = parser.parse_args()
    num_frames = opts.frames
    image_format = opts.image_format

    root_path = os.path.abspath(os.curdir)
    logger = logging.getLogger("Extract Frames from Videos")
    logger.setLevel('INFO')

    # Get list of directory names in current directory
    all_files = os.scandir()
    directories = [file.name for file in all_files if file.is_dir() and not file.name.startswith('.')]

    for dir in directories:
        os.chdir(dir)
        all_files = os.scandir()
        files = [file.name for file in all_files if not file.is_dir() and not file.name.startswith('.')]

        for video in files:
            logger.info("Running frame extraction for video {}".format(video))
            try:
                p = Popen(['python',
                           os.path.join(root_path, 'video_to_frames.py'),
                           '--num_frames={}'.format(num_frames),
                           '--image_format={}'.format(image_format),
                           '--video={}'.format(video)],
                          stdout=PIPE)
                print(p.stdout.read())
                p.terminate()
            except ValueError as e:
                logger.error("Couldn't run frame extraction for video {}".format(video))
                logger.error("Error message: " + e)
                continue

            logger.info("Finished frame extraction for video {}".format(video))
        os.chdir(root_path)
