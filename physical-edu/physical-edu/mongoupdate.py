# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 05:46:53 2019

@author: Mahesh
"""

from pymongo import MongoClient
import sys
import pandas as pd
import numpy as np
# pprint library is used to make the output look more pretty
from pprint import pprint
#import HumanOrganPostProcessing

# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
#client = MongoClient("mongodb://nlpbimdbrw:xgzzrw@sefvl@va33dlvmdb321.wellpoint.com:37043/?ssl=true&serverSelectionTimeoutMS=5000&connectTimeoutMS=10000&authSource=nlpbimdb&authMechanism=SCRAM-SHA-1&3t.uriVersion=3&3t.connection.name=AnthemDev%28RW%29&3t.certificatePreference=RootCACert:from_file&3t.rootCAPath=C:\Maheshk\Anthem\Docs\root_chain.pem")

#working_dir= "C:\\Maheshk\\Sample\\Docs\\Code\\files\\final\\"
Collection='test'
working_dir= "C:\Maheshk\Sample\JIRA\\"
dictnwtype={"In":0,"Out":1}
ticket='SE-288954'
file_name='SE-288954_4_SE_NLP'
Sheet_name="KY"
working_dir = working_dir+ ticket +'\\'
def writeoutput(infilename,nwtype,listitem):
    try:
        #print(infilename)
        with open(working_dir +infilename + str(nwtype)+'_log.txt', 'a') as filehandle:
            filehandle.write('%s\n' % listitem.encode('utf-8').strip())
    except Exception as ex:
        print('writeoutput- error')
        print(ex)
def Dataimport(filename,sheetname):
    try:
        #        file_name =infilename #'ga.xlsx'
        #        sheet_name=insheetname #'Sheet5'
        #Sheet_name=sheetname
        df_actual = pd.read_excel(working_dir +filename +'.xlsx' ,sheet_name=sheetname)
        print(df_actual.shape)
#        df_actual["incosharelen"] = df_actual["InCostshare"].map(str).encode('utf-8').strip().apply(len)
#        df_actual["inaddinfolen"] =df_actual["InAddinfo"].map(str).apply(len)
#        df_actual["outcosharelen"] =df_actual["OutCostshare"].map(str).apply(len)
#        df_actual["outaddinfolen"] =df_actual["OutAddInfo"].map(str).apply(len)
        df_actual["Updated"]=''
       
#        df_actual["incoadd"] =df_actual["InCostshare"].map(str).encode('utf-8').strip() + ' ' + df_actual["InAddinfo"].str.encode('utf-8').strip()
#        df_actual["outcoadd"] =df_actual["OutCostshare"].map(str).encode('utf-8').strip() + ' ' + df_actual["OutAddInfo"].map(str).encode('utf-8').strip()
        
        return df_actual
        
    except Exception as ex:
        exc_type,exc_obj,exc_tb=sys.exc_info()
        print("Dataimport.....Error")
        print(exc_tb.tb_lineno)
        print(ex)

def DataUpdateMongo(collection,docid,mongofieldid,nwtype,mongocostshare,mongoaddinfo,nwlbl):
    try:
        client = MongoClient('mongodb://DBNAME:xgzzrw%40sefvl@hostname:37043/?ssl=true&serverSelectionTimeoutMS=5000&connectTimeoutMS=10000&authSource=nlpbimdb&authMechanism=SCRAM-SHA-1&3t.uriVersion=3&3t.connection.name=SampleDev%28RW%29&3t.certificatePreference=RootCACert:from_file&3t.rootCAPath=C:\Maheshk\Sample\Docs\root_chain.pem')
        db=client.nlpbimdb
        # Issue the serverStatus command and print the results
#        collectionName= 'nlp_benefits_rawJson_lg_wi_v2_0'
#        docID=''
        costsharefieldtoupdate= "data.0.medicalServices." + str(mongofieldid) +".srvcNtwrk."+ str(nwtype) +".costShare"
        addinfofieldtoupdate= "data.0.medicalServices." + str(mongofieldid) +".srvcNtwrk."+ str(nwtype) +".srvcNtwrkAddInfo"
        nwlbltoupdate= "data.0.medicalServices." + str(mongofieldid) +".srvcNtwrk."+ str(nwtype) +".srvcNtwrkLbl"
        #serverStatusResult= db[collection].find_one({'extensions.docID': 'O_Large_3XH1'})
        #pprint(serverStatusResult)
        
        result=db[collection].update_one({"extensions.docID": docid},{ '$set': { costsharefieldtoupdate : mongocostshare ,addinfofieldtoupdate:mongoaddinfo } })
       
        print(costsharefieldtoupdate)
        print(result.matched_count)
        temp_value =collection+"U" + "^"+ str(docid) + "^"+str(mongofieldid)+ "^"+ str(result.matched_count)+"^" +str(result.modified_count) +"^"+  mongocostshare  +"^"+  mongoaddinfo 
        writeoutput(collection,nwtype ,temp_value)
        if (nwlbl !=''):
            result=db[collection].update_one({"extensions.docID": docid},{ '$set': { nwlbltoupdate : nwlbl } })
            
        if(mongoaddinfo==''):
            result=db[collection].update_one({"extensions.docID": docid},{ '$unset': { addinfofieldtoupdate:mongoaddinfo } })
            temp_value =collection +"R" + "^"+ str(docid) + "^"+str(mongofieldid)+ "^"+ str(result.matched_count)+"^" +str(result.modified_count) +"^"+  mongocostshare  +"^"+  mongoaddinfo 
            writeoutput(collection+"R",nwtype ,temp_value)
            print(result.modified_count)
    except Exception as ex:
        print('DataUpdateMongo-Error')
        exc_type,exc_obj,exc_tb=sys.exc_info()
        print(exc_tb.tb_lineno)
        print(ex)
        
def DocumentLoader(nwtype):
    try:    
        

#        file_name='294686-294683_Update'
#        Sheet_name="17-10-2019"
        collectionName="nlp_benefits_rawJson_lg_XX_v2_0"
        df_actual =Dataimport(file_name,Sheet_name)
        df_actual.AnthemTag = df_actual.AnthemTag.astype(int)
        df_actual = df_actual[df_actual.AnthemTag!=999]
        df_filteredServices = df_actual[nwtype+'ChangeFlag'] =='X' #df_actual['State'] == 'KY'
        
        #df_filteredServices_out = df_actual['State'] == 'KY' and df_actual['ChangeFlag'] == 'X'
        print(df_actual[df_filteredServices].shape)
        for index, row in df_actual[df_filteredServices].iterrows():
            incolName= collectionName.replace("XX",Sheet_name.lower())
            indocID= row["DocName"]
            indTagNo= row["AnthemTag"]
#            inCostshare= row[nwtype+"Modified"]
#            inAddinfo=  row[nwtype+"Modified"]
            inCostshare= row[nwtype+"ModifiedCS"]
            inAddinfo=  row[nwtype+"ModifiedAI"]
            inNwLbl=  row[nwtype+"NwLbl"]
            if((inAddinfo is np.nan or inAddinfo != inAddinfo)):
                inAddinfo = ''
            if((inCostshare is np.nan or inCostshare != inCostshare)):
                inCostshare = ''               
            if((inNwLbl is np.nan or inNwLbl != inNwLbl)):
                inNwLbl = ''
            #inAddinfo=  row["InAddinfo"]
#            if((inAddinfo is np.nan or inAddinfo != inAddinfo)):
#                inAddinfo = ''
           
            
            
            
            print(incolName+ indocID ,str(indTagNo) ,inCostshare ,"^", inAddinfo, "^", inNwLbl , "^", str(dictnwtype[nwtype]))
            DataUpdateMongo(incolName,str(indocID),indTagNo,str(dictnwtype[nwtype]),inCostshare,inAddinfo,inNwLbl)
            #df_actual.iloc[index,df_actual.columns.get_loc("Updated")] ="Y"
            
        print('Completed**********')
        print(df_actual[df_filteredServices].shape)
        #print(df_actual.shape)            
        #df_actual.to_excel(working_dir +file_name  +"_Updated.xlsx")
    except Exception as ex:
        print("Documentoader.....Error")
        exc_type,exc_obj,exc_tb=sys.exc_info()
        print(exc_tb.tb_lineno)
        print(ex)
    
        
DocumentLoader("Out")       
    
