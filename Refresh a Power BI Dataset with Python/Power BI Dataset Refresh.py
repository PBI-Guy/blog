#!/usr/bin/env python
# coding: utf-8

# In[28]:


#Import necessary libraries

import msal
import requests
import json
import pandas as pd


# In[29]:


#Set parameters

client_id = "" #Add your Client ID here
client_secret = "" #Add your Client Secret here
tenant_name = "" #Add your tenant name here
workspace_id = "" #Add your Workspace ID here
dataset_id = "" #Add your Dataset ID here

authority_url = "https://login.microsoftonline.com/" + tenant_name 
scope = ["https://analysis.windows.net/powerbi/api/.default"]
url = "https://api.powerbi.com/v1.0/myorg/groups/" + workspace_id +"/datasets/"+ dataset_id +"/refreshes?$top=1"


# In[30]:


#Use MSAL to grab token

app = msal.ConfidentialClientApplication(client_id, authority=authority_url, client_credential=client_secret)
result = app.acquire_token_for_client(scopes=scope)

#Get latest Power BI Dataset Refresh
if 'access_token' in result:
    access_token = result['access_token']
    header = {'Content-Type':'application/json', 'Authorization':f'Bearer {access_token}'}
    api_call = requests.get(url=url, headers=header)

    result = api_call.json()['value']
    
    df = pd.DataFrame(result, columns=['requestId', 'id', 'refreshType', 'startTime', 'endTime', 'status'])
    df.set_index('id')


# In[31]:


if df.status[0] == "Unknown":
    print("Dataset is refreshing right now. Please wait until this refresh has finished to trigger a new one.")
elif df.status[0] == "Disabled":
    print("Dataset refresh is disabled. Please enable it.")
elif df.status[0] == "Failed":
    print("Last Dataset refresh failed. Please check error message.")
elif df.status[0] == "Completed":
    api_call = requests.post(url=url, headers=header)
    print("We triggered a Dataset refresh.")
else:
    print("Not familiar with status, please check documentatino for status: '" + df.status[0] + "'")

