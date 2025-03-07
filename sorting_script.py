import os
import shutil
from datetime import datetime
import logging
from pathlib import Path

# Constants
CATEGORY_EXTENSIONS = {
    'Documents': ['.pdf', '.docx', '.txt', '.doc', '.rtf', '.odt', '.xlsx', '.xls', '.pptx', '.ppt', '.csv'],
    'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp'],
    'Audio': ['.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a'],
    'Video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
    'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
    'Code': ['.py', '.java', '.html', '.css', '.js', '.php', '.c', '.cpp', '.h', '.rb', '.json', '.xml'],
    'Executables': ['.exe', '.msi', '.app', '.dmg', '.deb', '.rpm'],
}
OLD_FILES_AGE_DAYS = 30

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def create_directory(path):
    """Create directory if it doesn't exist."""
    if not path.exists():
        path.mkdir()
        logger.info(f"Created directory: {path}")

def move_file(source, destination):
    """Safely move a file to the destination, handling duplicates."""
    if destination.exists():
        destination = handle_duplicates(destination)
    
    try:
        shutil.move(str(source), str(destination))
        logger.info(f"Moved {source.name} to {destination}")
    except Exception as e:
        logger.error(f"Error moving {source.name}: {e}")

def handle_duplicates(destination):
    """Handle duplicate filenames by appending a counter."""
    base_name = destination.stem
    extension = destination.suffix
    parent_dir = destination.parent
    counter = 1
    
    while True:
        new_name = f"{base_name}_{counter}{extension}"
        new_destination = parent_dir / new_name
        if not new_destination.exists():
            return new_destination
        counter += 1

def organize_downloads(downloads_path=None):
    """
    Organizes files in the downloads folder into subdirectories based on file type.
    
    Args:
        downloads_path: Path to the downloads folder. If None, uses the default user Downloads folder.
    """
    downloads_path = get_downloads_path(downloads_path)
    
    if not downloads_path.exists():
        logger.error(f"The path {downloads_path} does not exist!")
        return

    logger.info(f"Organizing files in {downloads_path}")
    
    create_category_directories(downloads_path)
    
    moved_count, skipped_count = process_files(downloads_path)
    
    logger.info(f"Organization complete: {moved_count} files moved, {skipped_count} files skipped.")

def get_downloads_path(downloads_path):
    """Return the downloads path, using the default if None."""
    if downloads_path is None:
        downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
    return Path(downloads_path)

def create_category_directories(downloads_path):
    """Create necessary directories for file categorization."""
    for category in CATEGORY_EXTENSIONS:
        create_directory(downloads_path / category)
    create_directory(downloads_path / "Others")
    create_directory(downloads_path / "Old Files")

def process_files(downloads_path):
    """Process files in the downloads directory and move them to appropriate categories."""
    moved_count = 0
    skipped_count = 0
    today = datetime.now()
    
    for item in downloads_path.iterdir():
        if item.is_dir() or item.name == os.path.basename(__file__):
            skipped_count += 1
            continue
        
        if is_old_file(item, today):
            move_file(item, downloads_path / "Old Files" / item.name)
            moved_count += 1
            continue
        
        found_category = move_file_to_category(item, downloads_path)
        
        if not found_category:
            move_file(item, downloads_path / "Others" / item.name)
            moved_count += 1
    
    return moved_count, skipped_count

def is_old_file(item, today):
    """Check if the file is older than the defined threshold."""
    file_age_days = (today - datetime.fromtimestamp(item.stat().st_mtime)).days
    return file_age_days > OLD_FILES_AGE_DAYS

def move_file_to_category(item, downloads_path):
    """Move file to its appropriate category based on extension."""
    file_ext = item.suffix.lower()
    
    for category, extensions in CATEGORY_EXTENSIONS.items():
        if file_ext in extensions:
            move_file(item, downloads_path / category / item.name)
            return True
    return False

def main():
    """Main function to organize downloads folder."""
    organize_downloads()

if __name__ == "__main__":
    main()
    print("Downloads folder has been organized!")