import os


def normalize_path(path: str) -> str:
    return os.path.normpath(path).replace("\\", "/")


def get_file_ext(path: str) -> str:
    _, ext = os.path.splitext(path)
    return ext.lower()


def get_file_name(path: str) -> str:
    return os.path.basename(path)


def is_under_dir(file_path: str, dir_path: str) -> bool:
    file_path = normalize_path(os.path.abspath(file_path))
    dir_path = normalize_path(os.path.abspath(dir_path))
    return file_path.startswith(dir_path + "/")
