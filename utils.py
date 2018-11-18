import os


def create_folder(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        print("Tried to create a folder that already exists. Moving on without creating new folder.")
        print("Folder path:", path)
