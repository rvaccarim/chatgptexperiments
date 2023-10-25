import os
import json
import zipfile
import datetime
import glob
import logging
import sys


def setup_logging(log_file):
    # Configure logging to save program activity to log.txt and print to console
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s: %(message)s",
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
    console_handler.setFormatter(formatter)
    logging.getLogger("").addHandler(console_handler)


def create_zip(source_directory, destination_directory):
    # Create a zip file
    current_datetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    zip_file_name = current_datetime + ".zip"
    zip_file_path = os.path.join(destination_directory, zip_file_name)

    try:
        with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(source_directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, source_directory)
                    zipf.write(file_path, relative_path)

    except Exception as e:
        logging.error(f"Error creating zip file: {e}")
        exit(1)

    return zip_file_name


def main():
    # Setup logging
    log_file = "log.txt"
    setup_logging(log_file)

    # Log the start of the copy process
    logging.info("Copy process started.")

    # Read the JSON configuration file
    config_file = "backup.json"

    if not os.path.exists(config_file):
        logging.error(f"Config file not found: {config_file}")
        exit(1)

    try:
        with open(config_file, "r") as json_file:
            config = json.load(json_file)
    except Exception as e:
        logging.error(f"Error reading JSON file: {e}")
        exit(1)

    source_directory = config.get("sourceDirectory", "")
    destination_directory = config.get("destinationDirectory", "")
    backups_to_keep = config.get("backupsToKeep", 5)

    # Validate source and destination directories
    if not os.path.exists(source_directory):
        logging.error("Source directory not found")
        exit(1)

    if not os.path.exists(destination_directory):
        logging.error("Destination directory not found")
        exit(1)

    # Check if source and destination directories are the same
    if os.path.abspath(source_directory) == os.path.abspath(destination_directory):
        logging.error("Source and destination directories are the same")
        exit(1)

    zip_file_name = create_zip(source_directory, destination_directory)

    # Delete old zip files, keeping the newest zip files based on backups_to_keep
    zip_files = glob.glob(os.path.join(destination_directory, "*.zip"))
    zip_files.sort(key=os.path.getctime)
    for old_zip_file in zip_files[:-backups_to_keep]:
        os.remove(old_zip_file)

    # Log program activity and print to console
    logging.info(f"Source directory: {source_directory}")
    logging.info(f"Destination directory: {destination_directory}")
    logging.info(f"Zip file created: {zip_file_name}")
    logging.info(f"Backups to keep: {backups_to_keep}")

    # Log the end of the copy process
    logging.info("Copy process finished.")


if __name__ == "__main__":
    main()
