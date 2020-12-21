#! python3

import os, send2trash, time
from imap_read import Imap_read
from pdf_extractor import extract_pdfs
from google_ss import google_shets



# crdentials
email = "lbexpressinvoices@gmail.com"
password = "Superman2019"
imap = "imap.gmail.com"

# Options for read emails
folders = ["INBOX"] # Read emails from the INBOX folder
search = "UNSEEN" # Only read emails with the flag: "UNSEEN". It would be "SEEN" or "UNSEEN

# Varible of url of google sheet
sheet_url = "https://docs.google.com/spreadsheets/d/12nts1p_9lYn5GFQJNACtI3bwEqU3g0BPuBfvWxXJaiQ/edit#gid=0"

# The the time to wait between each main loop of the code
# Time in seconds
wait_time = 10




# Infinity main loop
while True: 

    print ("\nRunning program:")

    # Get current file path
    path = os.path.dirname (__file__)

    # Get download files path 
    download_files_path = os.path.join (path, "downloaded files")


        ## DOWNLOAD FILES FROM MAIL

    # Make and instance of imap_reader class
    my_imap = Imap_read (imap, email, password, folders, search)

    # login to gmail service
    my_imap.loggin()

    # Read all email from specific folder
    no_emails = my_imap.read_emails()

    # If no new emails, continue to the next loop
    if no_emails:
        time.sleep(wait_time)
        continue

    # Download all files from ell emails
    no_files = my_imap.download_files(download_files_path)

    # If no downloaded files, continue to the next loop
    if no_files:
        time.sleep(wait_time)
        continue


        ## EXTRACT DATA FROM FILES

    # Instance of the class "extract_pdfs"
    my_extractor = extract_pdfs(download_files_path)

    # get all information from psd file and save in a variable
    all_data_files = my_extractor.get_all_data_files()


        ## WRITE INFORMATION IN GOOGLE SHEETS 

    # Class of google sheet: open google sheet 
    my_gss = google_shets (sheet_url)

    # Write all information in sheet
    my_gss.write_data (all_data_files)


        ## REMOVE LAST FILES

    # remove all files from specific folder
    my_imap.remove_files (download_files_path)


        # WAIT TIME

    print ("The program is waiting...")

    # wait before executing the next program loop
    time.sleep(wait_time)