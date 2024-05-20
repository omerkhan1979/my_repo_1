import os
import shutil
from git import Repo

from src.utils.console_printing import error_print


def copy_file_from_repo(
    repo_url: str, file_path: str, branch="master", output_folder="src/copy_config"
) -> str:
    """
    Copies a file from a remote Git repository to the specified output folder.

    Args:
        repo_url (str): The URL of the remote Git repository.
        file_path (str): The path to the file in the repository.
        branch (str, optional): The branch name to checkout from the repository. Defaults to 'master'.
        output_folder (str, optional): The folder in which to save the copied file. Defaults to 'src/copy_config'.

    Returns:
        str: The output path of the copied file.

    Raises:
        RuntimeError: If there is an error while reading or copying the file.
    """
    try:
        # Clone the remote repository
        repo_dir = "temp_repo"
        repo = Repo.clone_from(repo_url, repo_dir)

        # Checkout the specified branch
        repo.git.checkout(branch)

        # Get the file from the repository
        source_file_path = os.path.join(repo_dir, file_path)
        # Copy the file to the output path
        output_path = os.path.join(output_folder, os.path.dirname(file_path))
        os.makedirs(output_path, exist_ok=True)
        out = shutil.copy(source_file_path, output_path)
    except Exception as e:
        error_print(e)
        raise RuntimeError(f"Unable to read config file {file_path} from {repo_url}")
    finally:
        # Remove the cloned repository
        shutil.rmtree(repo_dir)

    return out


class GitRepository:
    """
    A representation of a git repository.

    This class contains a context manager for cloning a git repository and checking out a given branch.
    When the context is left, the cloned repository is deleted.

    Attributes:
    -----------
    repo_url : str
        A string containing the url for accessing the desired git repository.
        e.g. "https://github.com/takeoff-com/environment-configs.git"
    output_folder : str
        A string containing the path to clone the repository to. If the directory already exists,
        the repository will be cloned into a new directory inside of the existing directory.
    branch : str
        A string containing the branch name to checkout once the repository has been cloned.
    """

    def __init__(self, repo_url: str, output_folder: str, branch="master"):
        self.repo_url = repo_url
        self.output_folder = output_folder
        self.branch = branch

    def __enter__(self):
        """
        Context manager for cloning a git repository.

        Returns:
            str: The local path to the cloned repository.
        """
        if os.path.isfile(self.output_folder):
            raise ValueError("Argument output_folder must not be a file.")
        try:
            if os.path.isdir(self.output_folder):
                import random
                import string

                r_name = "".join(
                    random.choices(string.ascii_lowercase + string.digits, k=10)
                )
                self.output_folder = os.path.join(self.output_folder, r_name)
            self.repo = Repo.clone_from(
                self.repo_url, self.output_folder, branch=self.branch
            )
            return self.output_folder
        except Exception as err:
            shutil.rmtree(self.output_folder, ignore_errors=True)
            raise (err)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            info = (exc_type, exc_val, exc_tb)
            error_print(info)
        shutil.rmtree(self.output_folder, ignore_errors=True)
