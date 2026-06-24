import shutil
from pathlib import Path
from utils.logger import LOGGER


def empty_temp_folder(folder_path="temp_data"):
    """
    Empties the specified folder by deleting all files and subdirectories.

    Args:
        folder_path (str, optional): Path to the folder to be emptied.
                                     Defaults to "temp_data".

    Behavior:
        - If the folder does not exist, it will be created.
        - All files and symbolic links in the folder will be deleted.
        - All subdirectories will be recursively removed using shutil.rmtree().

    Error Handling:
        - If any item cannot be deleted, a warning will be logged with the error.
    """
    temp_dir = Path(folder_path)

    if not temp_dir.exists():
        temp_dir.mkdir(parents=True, exist_ok=True)
        return

    for item in temp_dir.iterdir():
        try:
            if item.is_file() or item.is_symlink():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        except Exception as e:
            LOGGER.warning(f"Impossible de supprimer {item.name} : {e}")
