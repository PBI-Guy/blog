#Run this Query as Admin in PowerShell!

#Set Parameters
$principalUser = "" #Replace the three dots with your Service Principal User
$csvPath = "" #Update the three dots with your path adding .csv at the end

#The first command sets the execution policy for Windows computers and allows scripts to run.
Set-ExecutionPolicy RemoteSigned

#The following command loads the Exchange Online management module.
Import-Module ExchangeOnlineManagement

#Next, you connect using your user principal name. A dialog will prompt you for your password and any multi-factor authentication requirements.
Connect-ExchangeOnline -UserPrincipalName $principalUser

#Now you can query for Power BI activity. In this example, the results are limited to 5,000, shown as a table, and export it to a CSV file for the last 90 days.
Search-UnifiedAuditLog -StartDate (Get-Date).AddDays(-90) -EndDate (Get-Date) -RecordType PowerBIAudit -ResultSize 5000 | Export-Csv -Path $csvPath

#Use this code if you wish to filter it on a specific day (in this case 07th March 2022) and limit the result to 1000. Lastly export the result as CSV.
#Search-UnifiedAuditLog -StartDate 03/07/2022 -EndDate 03/08/2022 -RecordType PowerBIAudit -ResultSize 1000 | Export-Csv -Path $csvPath

#Disconnect session
Disconnect-ExchangeOnline