# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 08:46:32 2019

@author: AG37514
"""
import pandas as pd
import numpy as np
import sys
import ServiceProcessing as sp

print('Started*******************************')
filepath= 'C:\\Maheshk\\Anthem\\JIRA\\'


service ="medicalservices\\human organ\\"
ticket=''
col_names =[]
file_name =''
sheet_name=''
Sheetnumber=2
row_list=[]
#is_2002 =  df_actual['docID']=='srvcCtgry'

#df_actual["SNO"]=df_actual['extensions.docID'].str.index(".") #df_actual['extensions.docID'].str[0:df_actual['extensions.docID'].str.index(".")]
#df_actual["SNO"]= df_actual['extensions.docID'].str[0:df_actual["SNO"]]
def preprocess(infolder,infilename,insheetname):
    try:
        file_name =infilename #'ga.xlsx'
        sheet_name=insheetname #'Sheet5'
        df_actual = pd.read_excel(filepath  +infolder+"\\"  +infilename +'.xlsx' ,sheet_name=insheetname)
        print(df_actual.shape)
        df_actual.loc[df_actual['extensions.docID'].str.contains("data.0.medicalServices.") , 'TYPE'] = "medicalServices"
        df_actual['extensions.docID'] = df_actual['extensions.docID'].str.replace("data.0.medicalServices.",'') 
        
        df_actual.loc[df_actual['extensions.docID'].str.contains("data.0.notes.") , 'TYPE'] = "notes"
        df_actual['extensions.docID'] = df_actual['extensions.docID'].str.replace("data.0.notes.",'') 
        
        df_actual.loc[df_actual['extensions.docID'].str.contains("data.0.planFeatures.") , 'TYPE'] = "planFeatures"
        df_actual['extensions.docID'] = df_actual['extensions.docID'].str.replace("data.0.planFeatures.",'') 
        
        df_actual.loc[df_actual['extensions.docID'].str.contains("data.0.tableOfContents.") , 'TYPE'] = "tableOfContents"
        df_actual['extensions.docID'] = df_actual['extensions.docID'].str.replace("data.0.tableOfContents.",'') 
        
        df_actual.loc[df_actual['extensions.docID'].str.contains("data.0.exclusions.") , 'TYPE'] = "exclusions"
        df_actual['extensions.docID'] = df_actual['extensions.docID'].str.replace("data.0.exclusions.",'') 
        
        df_actual = df_actual[df_actual.TYPE=='medicalServices']
        
        
        df_actual.loc[df_actual['extensions.docID'].str.index(".")==1 , 'SNO'] = df_actual['extensions.docID'].str[0:1]
        df_actual.loc[df_actual['extensions.docID'].str.index(".")==2 , 'SNO'] = df_actual['extensions.docID'].str[0:2]
        df_actual.loc[df_actual['extensions.docID'].str.index(".")==3 , 'SNO'] = df_actual['extensions.docID'].str[0:3]
        df_actual["SENO"]=9
        df_actual["FNO"]= ''
        
        df_actual.loc[df_actual['extensions.docID'].str.contains(".srvcCtgry") , 'SENO'] = 1
        df_actual.loc[df_actual['extensions.docID'].str.contains(".srvcCtgryAddInfo") , 'SENO'] = 9
        df_actual.loc[df_actual['extensions.docID'].str.contains(".srvcText") , 'SENO'] = 2
        df_actual.loc[df_actual['extensions.docID'].str.contains(".0.srvcNtwrkLbl") , 'SENO'] = 3
        df_actual.loc[df_actual['extensions.docID'].str.contains("0.costShare") , 'SENO'] = 4
        df_actual.loc[df_actual['extensions.docID'].str.contains("0.srvcNtwrkAddInfo") , 'SENO'] = 5
        df_actual.loc[df_actual['extensions.docID'].str.contains(".1.srvcNtwrkLbl") , 'SENO'] = 6
        df_actual.loc[df_actual['extensions.docID'].str.contains("1.costShare") , 'SENO'] = 7
        df_actual.loc[df_actual['extensions.docID'].str.contains("1.srvcNtwrkAddInfo") , 'SENO'] = 8
        df_actual["FNO"] = df_actual["SNO"].map(str)+df_actual["SENO"].map(str)
        df_actual["FNO"]=df_actual["FNO"].map(float)
        df_actual.sort_values(["FNO"], inplace=True)
        df_actual.to_excel(filepath    +infolder +"\\"  +file_name + sheet_name +".xls") 
        return df_actual
    except Exception as ex:
        print('preprocess- error' + infilename+ insheetname )
        print(ex)



def writeoutput(infolder,infilename,listitem):
    try:
        #print(infilename)
        with open(filepath  + infolder+"\\"  +infilename +'.txt', 'a') as filehandle:
            filehandle.write('%s\n' % listitem.encode('utf-8').strip())
    except Exception as ex:
        print('writeoutput- error')
        print(ex)
        
        
def EvaluateCellValue(df_result,ID):
    result =''
    try:
        df_filtered = df_result[df_result.SENO==ID]
        result = df_filtered.iat[0,0]
        #print('EvaluateCellValue********')
        #print(result)
        if((result is np.nan or result != result)):
            result = ''
      
    except Exception as ex:
        result=''
        #print('EvaluateCellValue********************************* error')
        #print(ex)
    return result        

def ServiceProcessing(infolder,infilename,insheetname):
    try:
        
        df_actual= preprocess(infolder,infilename,insheetname)
        col_names = list(df_actual.columns.values)
        print(col_names)
        for A  in ["extensions.docID",'SNO','SENO','FNO','TYPE']:
            col_names.remove(A)
        #col_names=[A for col_names  not in["extensions.docID",'SNO','SENO','FNO']]
        
        #writeoutput(infilename + '_' +insheetname, "DocName^TAGNo^Service^SubService^InCostshare^InAddinfo^OutCostshare^OutAddinfo")
        df_filteredServices = df_actual['SENO'] == 1
        print('Filtershape**********')
        print(df_filteredServices.shape)
        for col in col_names:
            #print('column'+ str(col))
            for index, row in df_actual[df_filteredServices].iterrows():
                ##WI,NV,CO ['Prescription Drug Retail Pharmacy and Home Delivery (Mail Order) Benefits']): #
                if(row['SENO'] ==1):# and row[col] in  ['Human Organ and Tissue Transplant (Bone Marrow / Stem Cell) Services','Human Organ and Tissue Transplants','ORGAN TRANSPLANTS']): 
                    #print( 'First---'+ str(row["SNO"]) + str(row[col]))
                    filter_result= df_actual['SNO'] == row["SNO"]
                    #attribute_filter =df_actual['SENO'] == row["SNO"]
                    df_result=df_actual[filter_result]
                    #print(df_result)
                    
                    df_filtered = df_result.filter(items=[str(col),"SENO"])
                    #print(df_filtered)
                    ServiceName = EvaluateCellValue(df_filtered,1)
                    SubServiceName = EvaluateCellValue(df_filtered,2)
                    InCostshare = EvaluateCellValue(df_filtered,4)
                    InAddinfo = EvaluateCellValue(df_filtered,5)
                    OutCostshare = EvaluateCellValue(df_filtered,7)
                    OutAddinfo = EvaluateCellValue(df_filtered,8)
                    #temp_value = str(col) + "^"+row["SNO"]+ "^" + ServiceName + "^" + SubServiceName + "^" + InCostshare + "^" + InAddinfo + "^" + OutCostshare + "^" + OutAddinfo
                    #print(temp_value)
                    #row_list.append({'DocName': str(col), 'AnthemTag': row["SNO"], 'Service': ServiceName, 'SubService': SubServiceName, 'InCostshare': InCostshare,'InAddinfo': InAddinfo, 'OutCostshare': OutCostshare, 'OutAddinfo': OutAddinfo})
                    row_list.append({'DocName': str(col), 'AnthemTag': row["SNO"], 'Service': ServiceName, 'SubService': SubServiceName, 'InCostshare': InCostshare,'InAddinfo': InAddinfo, 'OutCostshare': OutCostshare, 'OutAddinfo': OutAddinfo})
                    #writeoutput(infilename ,temp_value)
        print(insheetname + 'Completed*******************************')
        
    except Exception as ex:
        exc_type,exc_obj,exc_tb=sys.exc_info()
        print('ServiceProcessing- error')
        print(exc_tb.tb_lineno)
        print(ex)


def FileProcessing(infolder,filename,sheetnumber):
    try:
       
        localfilename =filename #'mo_anthem'
        sheetnames=[] #["Sheet2" ,"Sheet8","Sheet9","Sheet10","Sheet11","Sheet12","Sheet13","Sheet14","Sheet15","Sheet16"]
        for i in range(1,sheetnumber):
            sheetnames.append("Sheet"+str(i))
        print(sheetnames)
        for sheet in sheetnames:
            file_name =localfilename
            ServiceProcessing(infolder,file_name,sheet)
        print("************************Completed***********************")
        ColNames=['DocName','AnthemTag','Service','SubService','InCostshare','InAddinfo','OutCostshare','OutAddinfo']
        df_export = pd.DataFrame(row_list, columns=ColNames)
        df_export.to_excel(filepath +infolder+"\\"  +filename  +"_SE.xlsx") 
        sp.callserviceProcessing(infolder,filename+"_SE",sheetnumber)
    except Exception as ex:
        print('FileProcessing- error')
        print(ex)

FileProcessing("SE-295708","SE-295708_2",3)
#FileProcessing("KY","KY",8)
