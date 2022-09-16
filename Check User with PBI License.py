# ## Check User with PBI License
# Check through the Graph API which users have a PBI license and compare to activity log if it's still needed
 
#Import necessary libraries

import msal
import requests
import json
import pandas as pd
from pyspark.sql.functions import *
from datetime import date, timedelta

#Set parameters

client_id = '' #ID of Service Principal / App
client_secret = '' #Secret from Service Principal / App
scope = 'https://graph.microsoft.com/.default' #Defining Scope for Graph API
authority_url = "https://login.microsoftonline.com/..." #Defining authority / host

#Define all needed Power BI related SKUs
#All SKUs with the ID and friendly name of Microsoft can be found here: https://docs.microsoft.com/en-us/azure/active-directory/enterprise-users/licensing-service-plan-reference Check if new SKUs are available or have changed over time. The list below has been created on 15th September 2022
all_skus = pd.DataFrame ({
    'skuId': ['e97c048c-37a4-45fb-ab50-922fbf07a370', '46c119d4-0379-4a9d-85e4-97c66d3f909e', '06ebc4ee-1bb5-47dd-8120-11324bc54e06', 'c42b9cae-ea4f-4ab7-9717-81576235ccac', 'cd2925a3-5076-4233-8931-638a8c94f773', 'e2be619b-b125-455f-8660-fb503e431a5d', 'a4585165-0533-458a-97e3-c400570268c4', 'ee656612-49fa-43e5-b67e-cb1fdf7699df', 'c7df2760-2c81-4ef7-b578-5b5392b571df', 'e2767865-c3c9-4f09-9f99-6eee6eef861a', 'a403ebcc-fae0-4ca2-8c8c-7a907fd6c235', '7b26f5ab-a763-4c00-a1ac-f6c4b5506945', 'c1d032e0-5619-4761-9b5c-75b6831e1711', 'de376a03-6e5b-42ec-855f-093fb50b8ca5', 'f168a3fb-7bcf-4a27-98c3-c235ea4b78b4', 'f8a1db68-be16-40ed-86d5-cb42ce701560', '420af87e-8177-4146-a780-3786adaffbca', '3a6a908c-09c5-406a-8170-8ebb63c42882', 'f0612879-44ea-47fb-baf0-3d76d9235576'],
    'skuName': ['Microsoft 365 A5 for Faculty', 'Microsoft 365 A5 for Students', 'Microsoft 365 E5', 'Microsoft 365 E5 Developer (without Windows and Audio Conferencing)', 'Microsoft 365 E5 without Audio Conferencing', 'Microsoft 365 GCC G5', 'Office 365 A5 for Faculty', 'Office 365 A5 for Students', 'Office 365 E5', 'Power BI', 'Power BI (free)', 'Power BI Premium P1', 'Power BI Premium Per User', 'Power BI Premium Per User Add-On', 'Power BI Premium Per User Dept', 'Power BI Pro', 'Power BI Pro CE', 'Power BI Pro Dept', 'Power BI Pro for GCC']
})

app = msal.ConfidentialClientApplication(client_id, authority=authority_url, client_credential=client_secret)
result = app.acquire_token_for_client(scopes=scope)

url_get_all_users = 'https://graph.microsoft.com/v1.0/users' #URL to get all AAD users

#If access token is created and received, call the get all users url to receive licenses per user
if 'access_token' in result:
    access_token = result['access_token']
    header = {'Content-Type':'application/x-www-form-urlencoded', 'Authorization':f'Bearer {access_token}'}

    api_call = requests.get(url=url_get_all_users, headers=header) #Effective get all users from AAD URL call

    result = api_call.json()['value'] #Get only the necessary child
    df_all_users = pd.DataFrame(result) #Convert to DataFrame
    df_all_users = df_all_users[['displayName', 'mail', 'userPrincipalName', 'id']] #Get only needed columns

    df_all_user_licenses = pd.DataFrame() #Create empty DataFrame to store all users and assigned licenses

    for idx, row in df_all_users.iterrows(): #Iterate through each users from AAD
        user_id = row['id'] #Store the User ID in a separate variable
        userPrincipal = row['userPrincipalName']
        url_get_licenses = 'https://graph.microsoft.com/v1.0/users/' + user_id + '/licenseDetails' #Defining the URL to get licens per user

        api_call = requests.get(url=url_get_licenses, headers=header) #Effective get license per User URL call
        result = api_call.json()['value'] #Get only the necessary child

        df_user_licenses = pd.DataFrame(result) #convert to DataFrame
        df_user_licenses['userId'] = user_id #Add User ID to identify user
        df_user_licenses['userPrincipal'] = userPrincipal #Add User Principal to identify user
        
        #I'll use a try and except statement to handle empty requests --> if no license is assign nothing will be return and without try and except the script will run into an error. 
        #An if else statement would also work to check if the result is empty or not
        try:
            df_user_licenses = df_user_licenses[df_user_licenses['skuId'].isin(all_skus['skuId'])] #Get only PBI related SKUs
            df_user_licenses = df_user_licenses[['skuId', 'userId', 'userPrincipal']] #Get only needed columns
            df_user_licenses = all_skus.merge(df_user_licenses) #Using a join to retrieve only users with assigned PBI licenses
            df_all_user_licenses = pd.concat([df_all_user_licenses, df_user_licenses]) #Adding result to all user licenses DataFrame

        except:
            pass

#Read Activity Log folder with all files
df_activityLog = spark.read.load('abfss://powerbi@aiadadlgen2.dfs.core.windows.net/Activity Log/*', format='csv', header=True)

#Specify day varialbe for how many days you're looking back
daysBackToCheck = 90 #Configure this number based on need how many days you're looking for an inactive user. In this case 90 means 90 days going back from today on.
activityDays = date.today() - timedelta(days=daysBackToCheck)
activityDays = activityDays.strftime("%Y-%m-%d")

#Filter Activity logs to get last X days
df_activityLog = df_activityLog.filter(df_activityLog.CreationTime > activityDays)

#Aggregate to get the last activity day by user
df_activityLog = df_activityLog.groupBy('userId').agg(max('CreationTime').alias('Date'))
df_activityLog = df_activityLog.withColumnRenamed('userId', 'userPrincipal')

df_activityLog = df_activityLog.toPandas()

#Combine both DataFrames to check all users and their last login
df_combined = pd.merge(df_all_user_licenses, df_activityLog, how='left', on=['userPrincipal', 'userPrincipal'])

#Get all Users without login in last X days
df_combined_only_NaN = df_combined[pd.isna(df_combined['Date'])]

#Filter only to Power BI Free licenses for my demo use case
df_pbi_free = df_combined_only_NaN.loc[df_combined_only_NaN['skuId'] == 'a403ebcc-fae0-4ca2-8c8c-7a907fd6c235']

display(df_pbi_free)

#Overwrite header and reuse access token
header = {'Content-Type':'application/json', 'Authorization':f'Bearer {access_token}'}

for idx, row in df_pbi_free.iterrows(): #Iterate through each users with a PBI Free license
    user_id = row['userId'] #Store the User ID in a separate variable
    sku_id = row['skuId'] #Store the SKU ID in a separate variable
    userPrincipal = row['userPrincipal']

    #configure URL to call to remove license from user
    url = 'https://graph.microsoft.com/v1.0/users/' + user_id + '/assignLicense'

    #create body with SKU ID
    body = {
        "addLicenses": [],
        "removeLicenses": [
            sku_id
        ]
    }

    #Call API to remove license
    api_call = requests.post(url=url, headers=header, json=body)

    if api_call.status_code == 200:
        print('License has been successfully removed from user', userPrincipal)

    else:
        print('An error occured and license has NOT been removed')