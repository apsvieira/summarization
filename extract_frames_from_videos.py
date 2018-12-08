"""Extract frames from each video in each subdirectory of current directory."""
import argparse
import logging
import os
from subprocess import Popen, PIPE
# TODO add multiprocessing support
# TODO add verifications to ensure passed number of frames is correctly extracted

parser = argparse.ArgumentParser()
parser.add_argument('--frames',
                    type=int,
                    help="Number of frames to extract from each video")
parser.add_argument('--image_format',
                    choices=['.png', '.jpeg'],
                    help="Format of the output images")
parser.add_argument('--num_processes',
                    type=int,
                    default=10,
                    help="Maximum number of running parallel processes")

if __name__ == '__main__':
    opts = parser.parse_args()
    num_frames = opts.frames
    image_format = opts.image_format
    multiprocess_threshold = opts.num_processes

    root_path = os.path.abspath(os.curdir)
    os.chdir('./data')
    data_path = os.path.abspath(os.curdir)

    logger = logging.getLogger("framesFromVideos")
    logger.setLevel('DEBUG')

    # Get list of directory names in current directory
    all_files = os.scandir()
    directories = [file.name for file in all_files if file.is_dir() and not file.name.startswith('.')]

    for directory in directories:
        os.chdir(directory)
        all_files = os.scandir()
        files = [file.name for file in all_files if not file.is_dir() and not file.name.startswith('.')
                 and not file.name.endswith('.png') and not file.name.endswith('.jpeg')]

        child_processes = []
        for video in files:
            logger.info("Running frame extraction for video {}".format(video))
            try:
                p = Popen(['python',
                           os.path.join(root_path, 'video_to_frames.py'),
                           '--num_frames={}'.format(num_frames),
                           '--image_format={}'.format(image_format),
                           '--video={}'.format(video)],
                          stdout=PIPE)
                child_processes.append(p)
            except ValueError as e:
                logger.error("Couldn't run frame extraction for video {}".format(video))
                logger.error("Error message: " + e)
                continue

            logger.info("Finished frame extraction for video {}".format(video))
            # TODO check how to better handle multiple subprocesses
            if len(child_processes) > multiprocess_threshold:
                for cp in child_processes:
                    cp.wait()
                    child_processes.remove(cp)

        for cp in child_processes:
            cp.wait()
        os.chdir(data_path)
