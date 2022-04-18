from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

gauth = GoogleAuth()

# Try to load saved client credentials
gauth.LoadCredentialsFile("google_creds.txt")
if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    print('token expired')
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()
# Save the current credentials to a file
gauth.SaveCredentialsFile("google_creds.txt")


drive = GoogleDrive(gauth)
latest_folder_id = "1jCBBI34RIAPvb0K4S-vrZavcQEx00wr-"
archive_folder_id = "1t95ioPnTDzyNo6dUaR7rql0ighCB24lO"

upload_file_list = ["C:\\Users\\idach\\Pictures\\Wallpaper 4k 1.jpg",
                    "C:\\Users\\idach\\Pictures\\me 4 problem 9.PNG",
                    ]
for upload_file in upload_file_list:
    str = "\'" + latest_folder_id + "\'" + " in parents and trashed=false"
    file_list = drive.ListFile({'q': str}).GetList()
    print(file_list)
    if file_list:
        file = file_list[0]
        filename = file['title']
        file.GetContentFile(filename)
        gfile = drive.CreateFile({'parents': [{'id': archive_folder_id}]})
        gfile.SetContentFile(filename)
        gfile.Upload()
        file.Trash()

    gfile = drive.CreateFile({'parents': [{'id': latest_folder_id}]})
    # Read file and set it as the content of this instance.
    gfile.SetContentFile(upload_file)
    gfile.Upload()
    print('Finished Upload')

