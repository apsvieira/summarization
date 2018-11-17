"""Extract frames from each video in each subdirectory of current directory."""
import argparse
import logging
import os
from subprocess import Popen, PIPE
# TODO add multiprocessing support
# TODO add verifications to ensure passed number of frames is correctly extracted

parser = argparse.ArgumentParser()
parser.add_argument('--clips',
                    type=int,
                    help="Number of clips to extract from each video")
parser.add_argument('--frames',
                    type=int,
                    help="Number of frames each clip should contain")
parser.add_argument('--image_format',
                    choices=['.png', '.jpeg'],
                    help="Format of the output images")
parser.add_argument('--num_processes',
                    type=int,
                    default=10,
                    help="Maximum number of running parallel processes")


def create_folder(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        print("Tried to create a folder that already exists. Moving on without creating new folder.")
        print("Folder path:", path)


if __name__ == '__main__':
    opts = parser.parse_args()
    num_clips = opts.clips
    num_frames = opts.frames
    image_format = opts.image_format
    multiprocess_threshold = opts.num_processes

    root_path = os.path.abspath(os.curdir)
    data_path = os.path.abspath(os.path.join(root_path, 'data'))
    videos_path = os.path.abspath(os.path.join(data_path, 'videos'))
    images_path = os.path.abspath(os.path.join(data_path, 'images'))

    logger = logging.getLogger("framesFromVideos")
    logger.setLevel('DEBUG')

    create_folder(images_path)

    # Get list of directory names in current directory
    all_files = os.scandir(videos_path)
    # Here, the directory corresponds to the class label for the files in it
    directories = [file.name for file in all_files if file.is_dir() and not file.name.startswith('.')]

    for directory in directories:
        os.chdir(os.path.join(videos_path, directory))
        create_folder(os.path.join(images_path, directory))
        content = os.scandir()
        videos = [file.name for file in content if not file.is_dir() and not file.name.startswith('.')]

        child_processes = []
        for video in videos:
            output_path = os.path.join(images_path, directory, video)
            create_folder(output_path)
            logger.debug("-----------------\n" + output_path + "\n---------------------\n")

            logger.info("Running frame extraction for video {}".format(video))

            # TODO change to call video_to_clip.py script
            try:
                p = Popen(['python',
                           os.path.join(root_path, 'video_to_frames.py'),
                           '--num_clips={}'.format(num_clips),
                           '--num_frames={}'.format(num_frames),
                           '--image_format={}'.format(image_format),
                           '--video={}'.format(video),
                           '--output_path={}'.format(output_path)],
                          stdout=PIPE)
                child_processes.append(p)
            except ValueError as e:
                logger.error("Couldn't run frame extraction for video {}".format(video))
                logger.error("Error message: " + e)
                continue

            logger.info("Finished clip extraction for video {}".format(video))
            # TODO check how to better handle multiple subprocesses
            if len(child_processes) > multiprocess_threshold:
                for cp in child_processes:
                    cp.wait()
                    child_processes.remove(cp)

        for cp in child_processes:
            cp.wait()
