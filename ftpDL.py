import os
from ftplib import FTP
import time
from threading import Thread

import configparser
Config = configparser.ConfigParser()

def write_default_config():
    Config['FTP'] = {'ip': '192.168.1.1', 'port': '21', 'username': 'anonymous', 'password': 'anonymous', 'timeout_connection': '5', 'timeout_fetch': '5'}
    with open('config.ini', 'w') as configfile:
        Config.write(configfile)
    return Config

if not os.path.isfile('config.ini'):
    write_default_config()
else:
    Config.read('config.ini')
while True:
    try:
        ip = Config['FTP']['ip']
        port = Config['FTP']['port']
        username = Config['FTP']['username']
        password = Config['FTP']['password']
        timeout_connection = Config['FTP']['timeout_connection']
        timeout_fetch = Config['FTP']['timeout_fetch']
        break
    except:
        write_default_config()


def connect_to_ftp(ip, port, username, password, timeout_connection):
    while True:
        try:
            ftp = FTP()
            ftp.connect(ip, port)
            ftp.login(username, password)
            print("Successfully connected to FTP server", ip)
            return ftp
        except:
            print(f"Failed to connect to FTP server {ip}, retrying in {timeout_connection} seconds")
            time.sleep(timeout_connection)

def fetch_directory_listing(ftp):
    ftp.cwd("/")
    files = ftp.nlst()[:-50]
    print("Fetched", len(files), "files")
    return files
def download_file(files, ftp_connector, ip, port, username, password, timeout_connection):
    import threading, os
    ftp = ftp_connector(ip, port, username, password, timeout_connection)
    for filename in files:
        with open(filename, "wb") as file:
            ftp.retrbinary(f"RETR {filename}", file.write)
        print(threading.get_native_id(), "Downloaded", os.path.join(os.getcwd(), filename))
    ftp.quit()
    print(threading.get_native_id(), "FTP connection closed")

def main(IP, PORT, USERNAME, PASSWORD, TIMEOUT_CONNECTION, TIMEOUT_FETCH):
    ftp = connect_to_ftp(IP, PORT, USERNAME, PASSWORD, TIMEOUT_CONNECTION)
    initial_listing = fetch_directory_listing(ftp)
    while True:
        current_listing = fetch_directory_listing(ftp)
        new_files = [file for file in current_listing if file not in initial_listing and ".jpg" in file]
        #print(new_files)
        if new_files:
            print("Now downloading", new_files)
            t = Thread(target=download_file, args=(new_files, connect_to_ftp, IP, PORT, USERNAME, PASSWORD, TIMEOUT_CONNECTION))
            t.start()
        initial_listing = current_listing
        time.sleep(TIMEOUT_FETCH)
main(ip, int(port), username, password, float(timeout_connection), float(timeout_fetch))
