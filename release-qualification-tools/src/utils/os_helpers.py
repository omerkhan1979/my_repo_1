import os


def get_cwd():
    return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def delete_file(path):
    os.remove(path)


def give_file_body(path):
    with open(path, "r") as file:
        body = file.read()

    return body
