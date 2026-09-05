r"""
File Organizer
---------------
Automatically organizes files in a chosen folder into subfolders
based on file type (Images, Documents, Videos, Audio, Archives,
Code, Others).

HOW TO RUN THIS SCRIPT IN VS CODE:
1. Open this file in VS Code.
2. Click the "Run" (play button, ▶) icon in the top-right corner.
   OR right-click anywhere in the code and choose "Run Python File in Terminal".
3. When asked, type the full path of the folder you want to organize
   and press Enter. Example:
       D:\Downloads
4. The script will create folders like Images, Documents, Videos, etc.
   inside that folder and move the files into them.

SAFETY:
- This script never deletes files. It only moves them.
- If a file with the same name already exists in the destination,
  the new file is renamed automatically (e.g. "photo (1).jpg")
  so nothing gets overwritten or lost.
"""

import shutil
from pathlib import Path
from collections import defaultdict

# ---------------------------------------------------------------------------
# Which file extensions belong to which category.
# Feel free to add more extensions to any list below.
# ---------------------------------------------------------------------------
EXTENSION_MAP = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff", ".ico"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx",
                  ".ppt", ".pptx", ".csv", ".md"},
    "Videos": {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm", ".m4v"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"},
    "Code": {".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".json",
             ".xml", ".sh", ".ipynb"},
}

OTHERS_FOLDER = "Others"


def build_lookup():
    """Turn EXTENSION_MAP into a quick extension -> category dictionary."""
    lookup = {}
    for category, extensions in EXTENSION_MAP.items():
        for ext in extensions:
            lookup[ext] = category
    return lookup


def get_category(file_path, lookup):
    """Return the category folder name for a given file."""
    return lookup.get(file_path.suffix.lower(), OTHERS_FOLDER)


def get_safe_destination(dest_folder, filename):
    """
    Make sure we never overwrite an existing file.
    If 'photo.jpg' already exists, this returns 'photo (1).jpg', then
    'photo (2).jpg', and so on, until it finds a name that's free.
    """
    destination = dest_folder / filename
    if not destination.exists():
        return destination

    stem = destination.stem
    suffix = destination.suffix
    counter = 1
    while True:
        new_destination = dest_folder / f"{stem} ({counter}){suffix}"
        if not new_destination.exists():
            return new_destination
        counter += 1


def organize_folder(folder_path_text):
    """Main logic: look at every file in the folder and move it into place."""
    folder = Path(folder_path_text).expanduser().resolve()

    if not folder.exists():
        print(f"\nThat folder does not exist:\n  {folder}")
        return

    if not folder.is_dir():
        print(f"\nThat path is not a folder:\n  {folder}")
        return

    lookup = build_lookup()

    # Only look at files sitting directly in this folder (not subfolders).
    files = [f for f in folder.iterdir() if f.is_file()]

    if not files:
        print(f"\nNo files found in:\n  {folder}")
        return

    moved = defaultdict(list)
    skipped = []

    for file_path in files:
        try:
            category = get_category(file_path, lookup)
            dest_folder = folder / category
            dest_folder.mkdir(exist_ok=True)

            destination = get_safe_destination(dest_folder, file_path.name)
            shutil.move(str(file_path), str(destination))
            moved[category].append(destination.name)

        except Exception as error:
            # Whatever goes wrong with one file, just note it and keep going.
            skipped.append((file_path.name, str(error)))

    show_summary(moved, skipped)


def show_summary(moved, skipped):
    """Print a clear report of what happened."""
    print("\n" + "=" * 50)
    print("FILE ORGANIZATION SUMMARY")
    print("=" * 50)

    total = sum(len(files) for files in moved.values())

    if total == 0 and not skipped:
        print("Nothing was moved.")
        return

    for category in sorted(moved.keys()):
        file_list = moved[category]
        print(f"\n{category} ({len(file_list)} file(s)):")
        for name in file_list:
            print(f"  - {name}")

    if skipped:
        print(f"\nSkipped ({len(skipped)} file(s) - left untouched, not deleted):")
        for name, reason in skipped:
            print(f"  - {name}  ({reason})")

    print(f"\nTotal files moved: {total}")
    print("=" * 50)


def main():
    print("=== FILE ORGANIZER ===")
    folder_path_text = input("Enter the full path of the folder to organize: ").strip()

    if not folder_path_text:
        print("No folder path entered. Nothing to do.")
        return

    organize_folder(folder_path_text)
    input("\nDone. Press Enter to close...")


if __name__ == "__main__":
    main()
