# Report Created by Team Syntera
Contact: 
Dimitri Bütikofer - dimitri@syntera.ch
Kail Kuhn - kail@syntera.ch
Dominic Schranz - dominic@syntera.ch

# Important:
## Preview Feature
Please make sure Field parameters is activated in File > Options and Settings > Options > Preview Features > Field parameters.
Otherwise much of the functionality of this report will not work!

## Data Refresh
For stability reasons some local excel files were used. The files are in the submission folder \Data. 
If you want to Refresh, change path in Power Query via the parameter "dirFolderPath" to the full path of the data directory to ensure data load. (Add a trailing Backslash to the full path)

# Data Sources Used
All Data Sources are openly available.

- Health Data provided by WHO loaded via GHO OData API: https://www.who.int/data/gho/info/gho-odata-api
- Prosperity Data provided by Legatum Institute Foundation. Source File: https://www.prosperity.com/download_file/view/4440/2025
- Population Data provided by UN. Source File: https://unstats.un.org/unsd/amaapi/api/file/30
- GDP Data provided by UN. Source File: https://unstats.un.org/unsd/amaapi/api/file/2
- Country Longitute Latitude Source File: https://gist.github.com/tadast/8827699
- Flags Source File: https://www.kaggle.com/datasets/zhongtr0n/country-flag-urls?resource=download

Downloaded exports are provided in \Data
