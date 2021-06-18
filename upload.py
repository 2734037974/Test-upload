from __future__ import print_function

import pickle
import os
import shutil
from datetime import datetime

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient.http import MediaFileUpload, MediaIoBaseDownload
import io
from apiclient import errors
from apiclient import http
import logging

from apiclient import discovery

# If modifying these scopes, delete the file token.pickle.
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

SCOPES = ['https://www.googleapis.com/auth/drive']
gauth = GoogleAuth()
drive = GoogleDrive()

today = datetime.now()


def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)  # credentials.json download from drive API
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    # Call the Drive v3 API

# Enter The Uploadable folder ID From Shared Link
folder_name = today.strftime("%h-%d-%Y_%H-%M")
folder = drive.CreateFile({'title': folder_name, 'parents': [{'id': '1euKwLySt8DrG1-WLrSDcyUcYtiW4B2IH'}],
                    'mimeType': 'application/vnd.google-apps.folder'})

folder.Upload()

if os.path.exists(os.getcwd() + "/Folder/"):
        path = os.getcwd() + "/Folder/"
        del_list = os.listdir(path)
        for f in del_list:
            if not os.path.isfile(f):

                # upload list(path, f.title(), folder.get('id'))

                subfolderpath = path + f.title()
                # list2 = os.listdir(subfolderpath)
                if os.path.exists(subfolderpath):

                    # upload the folder
                    subfolder_name = f.title()
                    subfolder = drive.CreateFile(
                        {'title': subfolder_name, 'parents': [{'id': folder.get('id')}],
                         'mimeType': 'application/vnd.google-apps.folder'})
                    subfolder.Upload()
                    subfilelist = os.listdir(subfolderpath)
                    for file in subfilelist:

                        # if there is a file in the sub folder
                        if os.path.isfile(file):
                            filename = file.title()
                            # upload files in the subfolders
                            gfile = drive.CreateFile({'parents': [{'id': subfolder.get('id')}]})
                            # Read file and set it as the content of this instance.
                            gfile.SetContentFile(filename)
                            gfile.Upload()  # Upload the file.

                        # upload all the sub-sub folders (experiment etc.)
                        else:
                            subsubfolder_name = file.title()
                            subsubfolder = drive.CreateFile(
                                {'title': subsubfolder_name, 'parents': [{'id': subfolder.get('id')}],
                                 'mimeType': 'application/vnd.google-apps.folder'})
                            subsubfolder.Upload()
                            subsubfilelist = os.listdir(subfolderpath + "/" + file.title())

                            # if the folder is "positive" and is empty
                            # here, I have been trying to do this job, but the folder creating comes first

                            # get/upload every picture in the sub-sub files (experiment etc.)
                            for finalfile in subsubfilelist:


                                if not os.listdir(subfolderpath + "/" + file.title()) and file.title() == "positive":
                                    break

                                if os.path.isfile(subfolderpath + "/" + file.title()+"/"+finalfile):
                                    finalfilename = os.path.basename(finalfile)
                                    # upload files in the subfolders
                                    gfile = drive.CreateFile({'parents': [{'id': subsubfolder.get('id')}]})
                                    # Read file and set it as the content of this instance.
                                    gfile['title'] = finalfilename
                                    gfile.SetContentFile(subfolderpath + "/" + file.title()+"/"+finalfile)
                                    gfile.Upload()  # Upload the file.
                                # there are still folders in the sub-sub folder, must be wrong
                                else:
                                    print("wrong")

    # delete all the files (including folder) in the folder
# shutil.rmtree(os.getcwd() + "/Folder/")


if __name__ == '__main__':
    main()
