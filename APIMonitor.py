import pandas as pd
import requests
import urllib
import sqlalchemy as sa
import pyodbc
from datetime import datetime
import time
import pymsteams
import ast
file = open("C:/Users/olapadent/OneDrive - Sterling Bank Plc/Documents/PythonProjects/PKfile.txt", "r")
contents = file.read()
d = ast.literal_eval(contents)
file.close()
username = d["user"]
password = d["key"]
instance = d["MSSQLSERVER"]
connection_string = (
    'Driver={ODBC Driver 17 for SQL Server};'
    'SERVER='+instance+',1433;'
    'Database=API_Status_Check;'
    'UID=' +username+ ';'
    'PWD=' +password+ ';'
    'Trusted_Connection=no;'
)
connection_uri = f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(connection_string)}"
engine = sa.create_engine(connection_uri, fast_executemany=True)

value = True

while(value):
    urlMessage = []
    time.sleep(600)
    try:

        df= pd.read_csv('TestAPI.csv')
        # print(df)
        # for url in df['URLs']:   
        #     response= requests.head(url)   
        #     status= response.status_code 

        #     df2 = df['Status']=status
        #     print(df)
      
        for i in range(len(df)) :
            try: 
                response= requests.head(df.loc[i, "URLs"])
                status= response.status_code
                mTime =  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # print(mTime)
                message = list((df.loc[i, "APP",], df.loc[i, "URLs"],status,mTime))
                urlMessage.append(message)
                # print(urlMessage)
                #df2 = pd.DataFrame (urlMessage, columns = ['App', 'URL','Status','MessageTime'])
                #print(df2)
            except requests.ConnectionError:
                
                failureMessage = list((df.loc[i, "APP",], df.loc[i, "URLs"],'connection failed',mTime))
                urlMessage.append(failureMessage)
        df2 = pd.DataFrame (urlMessage, columns = ['App', 'URL','Status','MessageTime'])
        #print(df2)
        df2.to_sql("APIStatusCheck", engine, schema="dbo", if_exists="append", index=False)
        df_unavailable = df2.loc[df2['Status'] != 200]
        #df_unavail = '|'.join(df_unavailable["URL"] +  str(df_unavailable["Status"])) 
        df_unavail = ' | '.join(df_unavailable["URL"].tolist())
        df_unavailerror = ''.join(str(df_unavailable["Status"])) 
#         print(df_unavailable)
#         print(df_unavail,df_unavailerror)
        myTeamsMessage = pymsteams.connectorcard("https://sterlingbankng.webhook.office.com/webhookb2/c891340c-96b6-4fe0-9543-d9d129da311f@4c8a9f7a-11fc-4fc2-9099-0b68f72a197e/IncomingWebhook/7c620a17307544bf8443a2b39ca2c315/7e2d863b-0ede-4e75-b051-354fed630beb")
        myTeamsMessage.text("Dear Platform Support \n, please be informed that the following service(s) are currently unreacheable " + df_unavail + ' ' + df_unavailerror )
        myTeamsMessage.send()
    except Exception as e:
        print(str(e))
    