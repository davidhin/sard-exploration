"""Set up project paths."""
import inspect
import subprocess
from datetime import datetime
from pathlib import Path


def project_dir() -> Path:
    """Get project path."""
    return Path(__file__).parent.parent


def storage_dir() -> Path:
    """Get storage path."""
    return Path(__file__).parent.parent / "storage"


def external_dir() -> Path:
    """Get storage external path."""
    path = storage_dir() / "external"
    Path(path).mkdir(exist_ok=True, parents=True)
    return path


def interim_dir() -> Path:
    """Get storage interim path."""
    path = storage_dir() / "interim"
    Path(path).mkdir(exist_ok=True, parents=True)
    return path


def processed_dir() -> Path:
    """Get storage processed path."""
    path = storage_dir() / "processed"
    Path(path).mkdir(exist_ok=True, parents=True)
    return path


def outputs_dir() -> Path:
    """Get output path."""
    path = storage_dir() / "outputs"
    Path(path).mkdir(exist_ok=True, parents=True)
    return path


def get_dir(path) -> Path:
    """Get path, if exists. If not, create it."""
    Path(path).mkdir(exist_ok=True, parents=True)
    return path


def debug(msg, sep="\t"):
    """Print to console with debug information."""
    caller = inspect.stack()[1]
    file_name = caller.filename
    ln = caller.lineno
    now = datetime.now()
    time = now.strftime("%m/%d/%Y - %H:%M:%S")
    print(
        '\x1b[40m[{}] File "{}", line {}\x1b[0m\n\t\x1b[94m{}\x1b[0m'.format(
            time, file_name, ln, msg
        )
    )


def gitsha():
    """Get current git commit sha for reproducibility."""
    return (
        subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
        .strip()
        .decode()
    )


def subprocess_cmd(command: str, verbose: int = 0):
    """Run command line process.

    Example:
    subprocess_cmd('echo a; echo b', verbose=1)
    >>> a
    >>> b
    """
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    output = process.communicate()
    if verbose > 1:
        debug(output[0].decode())
        debug(output[1].decode())
    return output
