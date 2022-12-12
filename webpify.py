#!/usr/bin/env python3
import argparse
import threading
import itertools as it
import os
import sys
import glob
from PIL import Image

IMAGE_EXTENSIONS = ['*.jpg',  '*.jpeg', '*.png', '*.gif']
minor_version = sys.version_info.minor


def scan_directory(root, *patterns):
    if minor_version > 9:
        return it.chain.from_iterable(
            glob.iglob(f'**/{pattern}', root_dir=root, recursive=True)
            for pattern in patterns
        )
    else:
        return it.chain.from_iterable(
            glob.iglob(f'{root}/**/{pattern}', recursive=True)
            for pattern in patterns
        )


def compress_image(path, quality=40):
    image = Image.open(path)
    image = image.convert('RGB')
    image.save(f'{path}.webp', 'webp', optimize=True, quality=quality)

    sys.stdout.write('-')
    sys.stdout.flush()


def main(*, root, quality):
    threads = []
    images = list(scan_directory(root, *IMAGE_EXTENSIONS))
    images_len = len(images)

    if not images_len:
        print("Images couldn't be found.\nExiting...")
        return

    # Progress Bar
    sys.stdout.write("[%s]" % (" " * images_len))
    sys.stdout.flush()
    sys.stdout.write("\b" * (images_len+1))

    for image in images:
        thread = threading.Thread(target=compress_image, args=(image, quality))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    sys.stdout.write("]\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--dir', type=str,
        help="Directory to scan for image files. (Defaults os.getcwd())",
        default=os.getcwd())
    parser.add_argument(
        '--quality', type=int,
        help="Quality to use when optimizing the image. (Defaults 40)",
        default=40
    )

    args = parser.parse_args()
    main(root=args.dir, quality=args.quality)
