#!/usr/bin/env python
# coding: utf-8

# ## Save Log Files
# 
# null
# 

# In[31]:


#Import necessary libraries
import msal
import requests
import json
import pandas as pd
from datetime import date, timedelta


# In[32]:


#Set parameters

#Get yesterdays date and convert to string
activityDate = date.today() - timedelta(days=1)
activityDate = activityDate.strftime("%Y-%m-%d")

#Set Client ID and Secret for Service Principal
client_id = ""
client_secret = ""
authority_url = ""
scope = ["https://analysis.windows.net/powerbi/api/.default"]

#Set Power BI REST API to get Activities for today
url = "https://api.powerbi.com/v1.0/myorg/admin/activityevents?startDateTime='" + activityDate + "T00:00:00'&endDateTime='" + activityDate + "T23:59:59'"

#Set CSV path
path = ''


# In[ ]:


#Use MSAL to grab token
app = msal.ConfidentialClientApplication(client_id, authority=authority_url, client_credential=client_secret)
result = app.acquire_token_for_client(scopes=scope)

#Get latest Power BI Activities
if 'access_token' in result:
    access_token = result['access_token']
    header = {'Content-Type':'application/json', 'Authorization':f'Bearer {access_token}'}
    api_call = requests.get(url=url, headers=header)

    #Specify empty Dataframe with all columns
    column_names = ['Id', 'RecordType', 'CreationTime', 'Operation', 'OrganizationId', 'UserType', 'UserKey', 'Workload', 'UserId', 'ClientIP', 'UserAgent', 'Activity', 'IsSuccess', 'RequestId', 'ActivityId', 'ItemName', 'WorkSpaceName', 'DatasetName', 'ReportName', 'WorkspaceId', 'ObjectId', 'DatasetId', 'ReportId', 'ReportType', 'DistributionMethod', 'ConsumptionMethod']
    df = pd.DataFrame(columns=column_names)

    #Set continuation URL
    contUrl = api_call.json()['continuationUri']
    
    #Get all Activities for first hour, save to dataframe (df1) and append to empty created df
    result = api_call.json()['activityEventEntities']
    df1 = pd.DataFrame(result)
    pd.concat([df, df1])

    #Call Continuation URL as long as results get one back to get all activities through the day
    while contUrl is not None:        
        api_call_cont = requests.get(url=contUrl, headers=header)
        contUrl = api_call_cont.json()['continuationUri']
        result = api_call_cont.json()['activityEventEntities']
        df2 = pd.DataFrame(result)
        df = pd.concat([df, df2])
    
    #Set ID as Index of df
    df = df.set_index('Id')

    #Save df as CSV
    df.to_csv(path + activityDate + '.csv')

