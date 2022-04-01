# !pip install requests

# !pip install requests_ntlm

# Import required packages
import sys
import requests
from requests_ntlm import HttpNtlmAuth



# Read filename (relative path) from command line
fileName = 'eatLog.txt'

# Enter your SharePoint site and target library
sharePointUrl = 'https://usfedu.sharepoint.com/teams/EEDesign198GRP'
folderUrl = 'https://usfedu.sharepoint.com/:f:/t/EEDesign198GRP/EltzYZbFdiJIuyTANBVpGVABohiUDKWn4VUaCsv1KBkH2A?e=LJj1dN'

# Sets up the url for requesting a file upload
requestUrl = sharePointUrl + '/_api/web/getfolderbyserverrelativeurl(\'' + folderUrl + '\')/Files/add(url=\'' + fileName + '\',overwrite=true)'

# Read in the file that we are going to upload
file = open(fileName, 'rb')

# Setup the required headers for communicating with SharePoint
headers = {'Content-Type': 'application/json; odata=verbose', 'accept': 'application/json;odata=verbose'}

# Execute a request to get the FormDigestValue. This will be used to authenticate our upload request
r = requests.post(sharePointUrl + "/_api/contextinfo", auth=HttpNtlmAuth('FOREST\\hamiltonn', PW),
                  headers=headers)
formDigestValue = r.json()['d']['GetContextWebInformation']['FormDigestValue']

# Update headers to use the newly acquired FormDigestValue
headers = {'Content-Type': 'application/json; odata=verbose', 'accept': 'application/json;odata=verbose',
           'x-requestdigest': formDigestValue}

# Execute the request. If you run into issues, inspect the contents of uploadResult
uploadResult = requests.post(requestUrl, auth=HttpNtlmAuth('FOREST\\hamiltonn', PW), headers=headers,
                             data=file.read())
