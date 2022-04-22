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
latest_plant_image_folder_id = "1cmch7qs3WFkpS8GLzCbclByMP7uN3_dq"
archive_plant_image_folder_id = "1UBtqvBXPVuEiwwb6G7ogHJ5iie4RP3Nv"
plot_folder_id = "1PXfi9Ked4a14cCu0gaI6VATY_K6fNgld"

upload_file_list = ['"C:\\Users\\idach\\Pictures\\0.jpg"']
for upload_file in upload_file_list:
    str = "\'" + latest_plant_image_folder_id + "\'" + " in parents and trashed=false"
    file_list = drive.ListFile({'q': str}).GetList()
    # Move Latest Photo to Archive
    if file_list:
        file = file_list[0]
        filename = file['title']
        file.GetContentFile(filename)
        gfile = drive.CreateFile({'parents': [{'id': archive_plant_image_folder_id}]})
        gfile.SetContentFile(filename)
        gfile.Upload()
        file.Trash()
    # Upload latest photo
    gfile = drive.CreateFile({'parents': [{'id': latest_plant_image_folder_id}]})
    # Read file and set it as the content of this instance.
    gfile.SetContentFile(upload_file)
    gfile.Upload()
    print('Finished Image Upload')

plot_files = []
for plot_file in plot_files:
    # Upload the Plot
    gfile = drive.CreateFile({'parents': [{'id': plot_folder_id}]})
    # Read file and set it as the content of this instance.
    gfile.SetContentFile(plot_file)
    gfile.Upload()
    print('Finished Plot File Upload')