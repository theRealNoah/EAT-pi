from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import time

authAttempt = 0
while True:
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
latest_plant_image_folder_id = "1cmch7qs3WFkpS8GLzCbclByMP7uN3_dq"
archive_plant_image_folder_id = "1UBtqvBXPVuEiwwb6G7ogHJ5iie4RP3Nv"
plot_folder_id = "1PXfi9Ked4a14cCu0gaI6VATY_K6fNgld"

maxAttempts = 30
upload_file_list = ['C:\\Users\\idach\\Pictures\\0.jpg', 'C:\\Users\\idach\\Pictures\\DSC01948.jpg',
                    'C:\\Users\\idach\\Pictures\\0.jpg', 'C:\\Users\\idach\\Pictures\\0.jpg']

for upload_file in upload_file_list:
    attempt = 0
    while attempt < maxAttempts:
        try:
            print("Starting Image Upload for " + upload_file)
            str = "\'" + latest_plant_image_folder_id + "\'" + " in parents and trashed=false"
            file_list = drive.ListFile({'q': str}).GetList()
            # Move Latest Photo to Archive
            if file_list:
                #print(file_list[0])
                file = file_list[0]
                filename = file['title']
                file.GetContentFile(filename)
                gfile = drive.CreateFile({'parents': [{'id': archive_plant_image_folder_id}]})
                if gfile:
                    gfile.SetContentFile(filename)
                    gfile.Upload()
                else:
                    raise FileNotFoundError
                #print(file)
                file.Trash()
            # Upload latest photo
            gfile = drive.CreateFile({'parents': [{'id': latest_plant_image_folder_id}]})
            if gfile:
                # Read file and set it as the content of this instance.
                gfile.SetContentFile(upload_file)
                gfile.Upload()
                print('Finished Image Upload for ' + upload_file)
                break
            else:
                raise FileNotFoundError
        except BaseException as b:
            if attempt >= maxAttempts:
                # raise Exception('Unable to get updates after {} seconds of ConnectionErrors'.format(attempt))
                print('Image Upload FAILED after max attempts for ' + upload_file)
            else:
                attempt += 1
                print('Attempt: ', attempt)
                time.sleep(1)  # attempting once every second
                print(b)
