import os
from random import shuffle

from torchvision import datasets


def split_clips_dataset(dataset, val_split=0.2):
    """Split ImageClipDataset into training and validation, separating a number of videos for each.

    Parameters
    ----------
    dataset: ImageClipDataset. Dataset to be split. Should
    val_split: float in [0, 1], optional. Fraction of the dataset videos that will be reserved for validation.

    Returns
    -------
    train_set, val_set: ImageClipDatasets, constructed with the same parameters as the input dataset.
    """
    videos = dataset.videos_per_class
    _ = {k: shuffle(v) for k, v in videos.items()}

    num_videos_per_class = {k: int(val_split * len(v)) for k, v in videos.items()}
    val_videos = {k: v[:num_videos_per_class[k]] for k, v in videos.items()}
    train_videos = {k: v[num_videos_per_class[k]:] for k, v in videos.items()}

    val_set = ImageClipDataset(dataset.root, dataset.transform, dataset.target_transform,
                               dataset.extensions, dataset.loader, videos=val_videos)
    train_set = ImageClipDataset(dataset.root, dataset.transform, dataset.target_transform,
                                 dataset.extensions, dataset.loader, videos=train_videos)

    return train_set, val_set


class ImageClipDataset:
    """Dataset of sequences of images extracted from videos.

    Videos are sequences of images. Here, each sample is identified with the class
    and clip it belongs to within that class.
    """

    def __init__(self, path, transform=None, target_transform=None,
                 extensions=datasets.folder.IMG_EXTENSIONS,
                 loader=datasets.folder.default_loader,
                 videos=None):
        classes, class_to_idx = self._find_classes(path)
        videos, samples = self._make_dataset(path, class_to_idx, extensions, videos)

        self.root = os.path.abspath(path)
        self.loader = loader
        self.extensions = extensions

        self.classes = classes
        self.class_to_idx = class_to_idx
        self.samples = samples
        self.targets = [s[1] for s in samples]

        self.transform = transform
        self.target_transform = target_transform

        self.videos_per_class = videos
        self.total_num_videos = sum(map(lambda l: len(l), videos.values()))
        self.idx_to_class = {v: k for k, v in self.class_to_idx.items()}
        self.path_to_class = {class_name: os.path.join(self.root, class_name) for class_name in self.classes}

    @staticmethod
    def _find_classes(path):
        classes = [d.name for d in os.scandir(path) if d.is_dir()]
        classes.sort()
        class_to_idx = {class_name: idx for idx, class_name in enumerate(classes)}
        return classes, class_to_idx

    @staticmethod
    def _make_dataset(path, class_to_idx, extensions, videos=None):
        samples = []
        if videos is None:
            videos = {class_name: [x.name for x in os.scandir(os.path.join(path, class_name)) if x.is_dir()]
                      for class_name in class_to_idx.keys()}
        # Verify if user passed a dict, if not None
        assert isinstance(videos, dict), "Invalid data type for index of videos by class. Should be dict."

        for class_name, class_videos in videos.items():
            for video in class_videos:
                clips = [d.name for d in os.scandir(os.path.join(path, class_name, video)) if d.is_dir()]
                for clip in clips:
                    for file in os.scandir(os.path.join(path, class_name, video, clip)):
                        if datasets.folder.has_file_allowed_extension(file.name, extensions):
                            filepath = os.path.join(path, class_name, video, clip, file.name)
                            item = (filepath, class_to_idx[class_name])
                            samples.append(item)

        return videos, samples

    def __getitem__(self, index):
        """
        Args:
            index (int): Index
        Returns:
            tuple: (sample, target, video_id, clip_number) where target is class_index of the target class.
        """
        path, target = self.samples[index]
        sample = self.loader(path)

        # Addition: get the clip number from the sample's system path
        file_path = os.path.relpath(path, self.path_to_class[self.idx_to_class[target]])
        video_id, clip_id, _ = file_path.split(os.sep)
        clip_number = int(clip_id.split('_')[-1])

        if self.transform is not None:
            sample = self.transform(sample)
        if self.target_transform is not None:
            target = self.target_transform(target)

        return sample, target, video_id, clip_number

    def __len__(self):
        return len(self.samples)

    def __repr__(self):
        fmt_str = 'Dataset ' + self.__class__.__name__ + '\n'
        fmt_str += '    Number of classes: {}\n'.format(len(self.classes))
        fmt_str += '    Number of videos: {}\n'.format(self.total_num_videos)
        fmt_str += '    Number of datapoints: {}\n'.format(self.__len__())
        fmt_str += '    Root Location: {}\n'.format(self.root)
        tmp = '    Transforms (if any): '
        fmt_str += '{0}{1}\n'.format(tmp, self.transform.__repr__().replace('\n', '\n' + ' ' * len(tmp)))
        tmp = '    Target Transforms (if any): '
        fmt_str += '{0}{1}'.format(tmp, self.target_transform.__repr__().replace('\n', '\n' + ' ' * len(tmp)))

        return fmt_str
