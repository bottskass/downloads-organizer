import os
import shutil
from datetime import datetime
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def organize_downloads(downloads_path=None):
    """
    Organizes files in the downloads folder into subdirectories based on file type.
    
    Args:
        downloads_path: Path to the downloads folder. If None, uses the default user Downloads folder.
    """
    # If no path is provided, use the default Downloads folder
    if downloads_path is None:
        downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
    
    downloads_path = Path(downloads_path)
    
    # Ensure the downloads path exists
    if not downloads_path.exists():
        logger.error(f"The path {downloads_path} does not exist!")
        return
    
    logger.info(f"Organizing files in {downloads_path}")
    
    # Define category mappings
    category_extensions = {
        'Documents': ['.pdf', '.docx', '.txt', '.doc', '.rtf', '.odt', '.xlsx', '.xls', '.pptx', '.ppt', '.csv'],
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp'],
        'Audio': ['.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a'],
        'Video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
        'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
        'Code': ['.py', '.java', '.html', '.css', '.js', '.php', '.c', '.cpp', '.h', '.rb', '.json', '.xml'],
        'Executables': ['.exe', '.msi', '.app', '.dmg', '.deb', '.rpm'],
    }
    
    # Create destination directories if they don't exist
    for category in category_extensions:
        category_path = downloads_path / category
        if not category_path.exists():
            category_path.mkdir()
            logger.info(f"Created directory: {category_path}")
    
    # Create an "Others" directory for uncategorized files
    others_path = downloads_path / "Others"
    if not others_path.exists():
        others_path.mkdir()
        logger.info(f"Created directory: {others_path}")
    
    # Create a directory for old files (older than 30 days)
    old_files_path = downloads_path / "Old Files"
    if not old_files_path.exists():
        old_files_path.mkdir()
        logger.info(f"Created directory: {old_files_path}")
    
    # Process each file in the downloads directory
    moved_count = 0
    skipped_count = 0
    today = datetime.now()
    
    for item in downloads_path.iterdir():
        # Skip directories and the script itself
        if item.is_dir() or item.name == os.path.basename(__file__):
            continue
        
        # Get file extension (lowercase)
        file_ext = item.suffix.lower()
        
        # Check if file is older than 30 days
        file_age_days = (today - datetime.fromtimestamp(item.stat().st_mtime)).days
        if file_age_days > 30:
            destination = old_files_path / item.name
            move_file(item, destination)
            moved_count += 1
            continue
        
        # Find the appropriate category for the file
        found_category = False
        for category, extensions in category_extensions.items():
            if file_ext in extensions:
                destination = downloads_path / category / item.name
                move_file(item, destination)
                moved_count += 1
                found_category = True
                break
        
        # If no category found, move to Others
        if not found_category:
            destination = others_path / item.name
            move_file(item, destination)
            moved_count += 1
    
    logger.info(f"Organization complete: {moved_count} files moved, {skipped_count} files skipped.")

def move_file(source, destination):
    """Safely move a file to the destination, handling duplicates."""
    # If the destination file already exists, append a number to the filename
    if destination.exists():
        base_name = destination.stem
        extension = destination.suffix
        parent_dir = destination.parent
        counter = 1
        
        while True:
            new_name = f"{base_name}_{counter}{extension}"
            new_destination = parent_dir / new_name
            if not new_destination.exists():
                destination = new_destination
                break
            counter += 1
    
    try:
        shutil.move(str(source), str(destination))
        logger.info(f"Moved {source.name} to {destination}")
    except Exception as e:
        logger.error(f"Error moving {source.name}: {e}")

if __name__ == "__main__":
    organize_downloads()
    print("Downloads folder has been organized!")