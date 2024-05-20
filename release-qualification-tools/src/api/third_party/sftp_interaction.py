import pysftp
from src.config.config import Config
from src.utils.waiters import wait
from src.utils.console_printing import done, error


def upload_via_sftp(
    config: Config, source_filename: str, source_filepath: str, remote_filename=None
) -> bool:
    """Uploads given file to rint sftp url location based on the passed in
    configuration object. Returns true if the file is successfully uploaded and
    transferred. Returns false if upload failed OR file was not able to be
    transferred to data folder.

    Args:
        config (Config): Config object
        source_filename (str): string filename
        source_filepath (str): string of path of the file

    Returns:
        bool: true if successful, false otherwise
    """
    hostname = f"rint-sftp-{config.url}"
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    success = True
    with pysftp.Connection(
        host=hostname,
        username=config.sftp_username,
        password=config.sftp_password,
        cnopts=cnopts,
    ) as sftp:
        # establishing connection to sftp server
        print(done("Connection successfully established ..."))

        local_file_path = f"{source_filepath}"
        if not remote_filename:
            remote_filename = source_filename
        remote_file_path = f"/inbound/transfer/{remote_filename}"

        try:
            # uploading PO file to transfer folder on remote sftp server
            sftp.put(local_file_path, remote_file_path)
            print(done("successfully uploaded to transfer folder"))
        except Exception as e:
            print(error(e))
            print(error(f"Error while uploading {remote_filename}"))
            success = False
        try:
            # moving needed file to data folder on the remote sftp server
            sftp.rename(
                f"/inbound/transfer/{remote_filename}",
                f"/inbound/data/{remote_filename}",
            )
            # show to the user that needed file moved to 'data' directory
            files = sftp.listdir_attr("/inbound/data")
            for f in files:
                print(f"Here is the content of folder /inbound/data: {f}")
            print(done(f"successfully moved {remote_filename} to data folder"))
        except:
            print(error(f"Error while moving {remote_filename} to data folder"))
            success = False
        return success


def is_sftp_file(config: Config, source_filename: str, target_filepath: str) -> bool:
    """Checks if the give file exists on the target filepath.
    The rint sftp url location based on the passed in configuration object.

    Args:
        config (Config): Config object
        source_filename (str): string filename
        target_filepath (str): location of path to look

    Returns:
        bool: true if exists, false otherwise
    """
    hostname = f"rint-sftp-{config.url}"
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    with pysftp.Connection(
        host=hostname,
        username=config.sftp_username,
        password=config.sftp_password,
        cnopts=cnopts,
    ) as sftp:
        # establishing connection to sftp server
        print(done("Connection successfully established ..."))
        remote_file_path = f"{target_filepath}/{source_filename}"
        try:
            print(done(f"Checking if file {remote_file_path} exists."))
            return sftp.exists(remote_file_path)
        except Exception as e:
            print(error(e))
            print(error(f"Error checking if file {remote_file_path} exists."))
            return False


def delete_sftp_file(
    config: Config, source_filename: str, target_filepath: str
) -> bool:
    """Checks if the give file exists on the target filepath.
    The rint sftp url location based on the passed in configuration object.

    Args:
        config (Config): Config object
        source_filename (str): string filename
        target_filepath (str): location of path to look

    Returns:
        bool: true if exists, false otherwise
    """
    hostname = f"rint-sftp-{config.url}"
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    success = False
    with pysftp.Connection(
        host=hostname,
        username=config.sftp_username,
        password=config.sftp_password,
        cnopts=cnopts,
    ) as sftp:
        # establishing connection to sftp server
        print(done("Connection successfully established ..."))
        remote_file_path = f"{target_filepath}/{source_filename}"
        try:
            print(done(f"Checking if file {remote_file_path} exists."))
            if sftp.exists(remote_file_path):
                print(done(f"Attempting to delete file {remote_file_path}."))
                sftp.remove(remote_file_path)
                success = True
        except Exception as e:
            print(error(e))
            print(error(f"Error checking if file {remote_file_path} exists."))
    return success


@wait
def check_is_sftp_file(
    config: Config, source_filename: str, target_filepath: str
) -> bool:
    history = is_sftp_file(config, source_filename, target_filepath)
    return False or history
