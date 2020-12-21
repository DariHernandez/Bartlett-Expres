#! python3
# Read email and access to IMAP

import sys, imapclient, pyzmail,  os, send2trash

class Imap_read (): 
    """Class for read and process emails with imap protocole"""

    def __init__ (self, imap, myEmail, password, folders, search): 
        """ Constructor fo the class"""

        # Class variables. Set variables that will be used in the module
        self.dic_emails = {}
        self.imap = imap
        self.myEmail = myEmail
        self.password = password
        self.folders = folders
        self.search = search 
    
    def loggin (self): 
        """Validate IMAP servides and loggin"""

        # Try to conect to IMAP service
        try: 
            # Try to conect to IMAP with ssl certificate
            self.imapObj = imapclient.IMAPClient(self.imap, ssl=True, use_uid=True)
        except: 
            # If ssl certificate failure, then conect without certificate
            self.imapObj = imapclient.IMAPClient(self.imap, ssl=False)
        
        
        # Try to login with user name and passwqord 
        try: 
            # Try to login with email credentials
            self.imapObj.login(self.myEmail, self.password)
        except: 
            # if login return an error, print message en exit of progra,
            print ('\nLogin error. Check your email and password.\n')
            sys.exit()
        else: 
            # If login did not return an error, print message
            print ("Correct loggin to {}".format(self.myEmail))


    def read_emails (self): 
        """ Get all emails from folder and search termns"""
    
        # User message
        print ("Reading emails...")

        # Empty dictionary where the final information will be saved
        dicReturn = {}

        # save a class variable to a local variable
        search = self.search

        # Read all emails from each fodlder
        for folder in self.folders: 
            
            
            try:
                # Try to read folder
                self.imapObj.select_folder(folder, readonly=True)
            except: 
                # If read folder return an error, print message en exit of the program
                print ('\nFolder %s doesnt exist or is empty. Try with other folder.\n' % (folder))
                sys.exit()

            # Filter emails. Get only the emails that have the "unseen" flag
            UIDs = self.imapObj.search([search])
            
            # If not new emails, return True to end the current loop
            if not UIDs: 
                print ("NO NEW EMAILS.\nThe program is waiting...")
                return True

            # Loop for each email after filtering them
            for uid in UIDs: 

                # Gat the body of the current email
                rawMessage = self.imapObj.fetch([uid],  ['BODY[]', 'FLAGS'])
                message = pyzmail.PyzMessage.factory(rawMessage[uid][b'BODY[]'])

                # Save the current message in "dicReturn" dictionary
                dicReturn[uid] = message

        # Set the dictionary as class variable    
        self.dic_emails = dicReturn

        return False


    def __mark_as_read  (self): 
        """Mark as reed all message processed"""

        print ("Set messages as read...")

        # Loop for each folder in folder list
        for folder in self.folders: 

            # Select specific folder
            self.imapObj.select_folder(folder, readonly=False)
            
            # empty list where all emails will be saved to place the "seen" flag
            UIDs = []

            # Loop for all emails (only the UIDs)
            for uid in self.dic_emails.keys(): 

                # Add all emails identifier to the list
                UIDs.append (uid)

            # Set as read,aell emails in the list: UIDs
            self.imapObj.add_flags (UIDs, "\\SEEN")

    def download_files (self, folder): 
        """ Download all files from emails"""

        # mark processed emails, as read emails
        self.__mark_as_read()

        print ("Downloading files...")

        # variable to count the number of files downloaded
        files = 0

        # Read emails from dic_emails dictionary
        for email in self.dic_emails.values(): 

            # check if mail has attachment file
            if len(email.get_payload()) > 1: 

                # Loop for each attachment file
                for index_file in range (1, len(email.get_payload())):

                    # read each parth of the email
                    for part in email.get_payload(index_file).walk():

                        # get fle name
                        fileName = part.get_filename()

                        # If file name is correct, continue
                        if fileName: 

                            # verify that the file to download is a pdf file
                            if fileName.lower().endswith(".pdf"):

                                # Incress counter of files
                                files += 1

                                # full file path
                                filePath = os.path.join(folder, fileName)

                                # Print message to user
                                if os.path.isfile(filePath):
                                    print ('File "{}" replaced.'.format(fileName))
                                else: 
                                    print ('New file "{}" saved.'.format(fileName))

                                # Write new file
                                fp = open(filePath, 'wb')
                                fp.write(part.get_payload(decode=True))
                                fp.close()

        # if no files downloaded, end the current loop
        if files == 0: 
            print ("THE NEW MAILS DO NOT HAVE ATTACHED PDF FILES.\nThe program is waiting...")
            return True
        else: 
            return False

    def close (self): 
        """sign out of IMAP"""
        self.imapObj.logout()

    def remove_files (self, folder): 
        """ Delete all files from specific folder"""

        # Logout of imap
        self.close()

        print ("Deleting files...")

        # Loop for each file inside the folder. Send last files to trash
        for file_name in os.listdir (folder): 

            # send to trash each file
            pdf_file = os.path.join (folder, file_name)
            send2trash.send2trash (pdf_file)
    


