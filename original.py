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


# upload folders

# -------------------------------------------------------------------------------
# for future editing, this function is now wrong, and is not used in mian.
# please do some extra work in case we might want to change something in uploading
# -------------------------------------------------------------------------------
def uploadlist(path, name, des):
    subfolderpath = path + name
    if os.path.isdir(subfolderpath):
        subfolder_name = name
        subfolder = drive.CreateFile(
            {'title': subfolder_name, 'parents': [{'id': des}],
             'mimeType': 'application/vnd.google-apps.folder'})
        subfolder.Upload()
        uploadlist(subfolderpath, subfolder_name, subfolder.get('id'))
    else:
        # upload files in the subfolders
        gfile = drive.CreateFile({'parents': [{'id': des}]})
        # Read file and set it as the content of this instance.
        gfile.SetContentFile(name)
        gfile.Upload()  # Upload the file.


# -------------------------------------------------------------------------------------

# To list folders
def listfolders(service, filid, des):
    results = service.files().list(
        pageSize=1000, q="\'" + filid + "\'" + " in parents",
        fields="nextPageToken, files(id, name, mimeType)").execute()
    # logging.debug(folder)
    folder = results.get('files', [])
    for item in folder:
        if str(item['mimeType']) == str('application/vnd.google-apps.folder'):
            if not os.path.isdir(des + "/" + item['name']):
                os.mkdir(path=des + "/" + item['name'])
            print(item['name'])
            listfolders(service, item['id'], des + "/" + item['name'])  # LOOP un-till the files are found
        else:
            downloadfiles(service, item['id'], item['name'], des)
            print(item['name'])

    # create sub-sub folders
    if not os.path.exists(des + "/" + "experiment"):
        os.mkdir(path=des + "/" + "experiment")
    if not os.path.exists(des + "/" + "simulation"):
        os.mkdir(path=des + "/" + "simulation")
    if not os.path.exists(des + "/" + "negative"):
        os.mkdir(path=des + "/" + "negative")
    if not os.path.exists(des + "/" + "positive"):
        os.mkdir(path=des + "/" + "positive")

    return folder


# To Download Files
def downloadfiles(service, dowid, name, dfilespath):
    request = service.files().get_media(fileId=dowid)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    with io.open(dfilespath + "/" + name, 'wb') as f:
        fh.seek(0)
        f.write(fh.read())


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

    Folder_id = "'1_OXVxS1Clre-DeHCsPbbDiRQRoFlAH4d'"  # Enter The Downloadable folder ID From Shared Link

    results = service.files().list(
        pageSize=1000, q=Folder_id + " in parents", fields="nextPageToken, files(id, name, mimeType)").execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:

        # ------------------------------------------------------------------------------
        # here, I create a "big" folder in google drive to store everything uploaded from local
        # is written in "upload.py"
        # upload the folder
        folder_name = today.strftime("%h-%d-%Y_%H-%M")
        # Enter The Uploadable folder ID From Shared Link
        folder = drive.CreateFile({'title': folder_name, 'parents': [{'id': '1euKwLySt8DrG1-WLrSDcyUcYtiW4B2IH'}],
                                   'mimeType': 'application/vnd.google-apps.folder'})

        folder.Upload()
        # -----------------------------------------------------------------------------

        print('Files:')
        for item in items:
            print(item['name'])
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                # get all folders
                if not os.path.isdir("Folder"):
                    os.mkdir("Folder")
                bfolderpath = os.getcwd() + "/Folder/"
                if not os.path.isdir(bfolderpath + item['name']):
                    os.mkdir(bfolderpath + item['name'])

                folderpath = bfolderpath + item['name']
                listfolders(service, item['id'], folderpath)
            else:
                # get all files
                if not os.path.isdir("Folder"):
                    os.mkdir("Folder")
                bfolderpath = os.getcwd() + "/Folder/"

                filepath = bfolderpath
                downloadfiles(service, item['id'], item['name'], filepath)
        # ------------------------------------------------------------
        # the end of downloading part
        # -----------------------------------------------------

    # -------------------------------------------------------------
    # I recommend to put all the uploading here
    # it may go wrong, please check "upload.py" for tested code
    # -------------------------------------------------------

    if os.path.exists(os.getcwd() + "/Folder/"):
        path = os.getcwd() + "/Folder/"
        del_list = os.listdir(path)
        for f in del_list:
            if not os.path.isfile(f):

                subfolderpath = path + f.title()
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
                            # upload files in the subfolders\
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

                            # get/upload every picture in the sub-sub files (experiment etc.)
                            for finalfile in subsubfilelist:

                                # if the folder is "positive" and is empty
                                # here, I have been trying to do this job, but the folder creating comes first
                                # if not os.listdir(subfolderpath + "/" + file.title()) and file.title() == "positive":
                                # break

                                if os.path.isfile(subfolderpath + "/" + file.title() + "/" + finalfile):
                                    finalfilename = os.path.basename(finalfile)
                                    # upload files in the subfolders
                                    gfile = drive.CreateFile({'parents': [{'id': subsubfolder.get('id')}]})
                                    # Read file and set it as the content of this instance.
                                    gfile['title'] = finalfilename
                                    gfile.SetContentFile(subfolderpath + "/" + file.title() + "/" + finalfile)
                                    gfile.Upload()  # Upload the file.
                                # there are still folders in the sub-sub folder, must be wrong
                                else:
                                    print("wrong")
    # ----------------------------------------------------------
    # end of uploading
    # indeed, it is a messy code and not good at all
    # but it works
    # -----------------------------------------------

    # delete all the files (including folder) in the folder
    shutil.rmtree(os.getcwd() + "/Folder/")


if __name__ == '__main__':
    main()
