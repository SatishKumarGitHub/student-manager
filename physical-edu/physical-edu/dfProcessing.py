# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 10:10:40 2019

@author: AG37514
"""
from __future__ import unicode_literals
import pandas as pd
import sys
import numpy as np
#reload(sys)
#sys.setdefaultencoding('utf8')
from nltk.tokenize import sent_tokenize

#working_dir= "C:\\Maheshk\\Anthem\\allservices\\medicalservices\\human organ\\"
working_dir= "C:\\Maheshk\\Anthem\\JIRA\\"


def Dataimport(ticket,filename,sheetname):
    try:
        #        file_name =infilename #'ga.xlsx'
        #        sheet_name=insheetname #'Sheet5'
        df_actual = pd.read_excel(working_dir+ ticket +"\\" +filename +'.xlsx' ,sheet_name=sheetname)
        print(df_actual.shape)
#        df_actual["incosharelen"] = df_actual["InCostshare"].map(str).encode('utf-8').strip().apply(len)
#        df_actual["inaddinfolen"] =df_actual["InAddinfo"].map(str).apply(len)
#        df_actual["outcosharelen"] =df_actual["OutCostshare"].map(str).apply(len)
#        df_actual["outaddinfolen"] =df_actual["OutAddInfo"].map(str).apply(len)
        df_actual["InModifiedCS"]=''
        df_actual["InModifiedAI"]=''
        df_actual["OutModifiedCS"]=''
        df_actual["OutModifiedAI"]=''
        df_actual["InChangeFlag"] =''
        df_actual["OutChangeFlag"] ='' 
#        df_actual["incoadd"] =df_actual["InCostshare"].map(str).encode('utf-8').strip() + ' ' + df_actual["InAddinfo"].str.encode('utf-8').strip()
#        df_actual["outcoadd"] =df_actual["OutCostshare"].map(str).encode('utf-8').strip() + ' ' + df_actual["OutAddInfo"].map(str).encode('utf-8').strip()
        #df_actual.to_excel(working_dir +filename  +"_temp.xlsx") 
        return df_actual
        
    except Exception as ex:
        exc_type,exc_obj,exc_tb=sys.exc_info()
        print("Dataimport.....Error")
        print(exc_tb.tb_lineno)
        print(ex)
        
        
def MLOperation(ticket,filename,sheetname):
    try:
        df_actual= Dataimport(ticket,filename,sheetname)
#        In_df_actual = df_actual[df_actual.InAddinfo!=''] 
#        Out_df_actual = df_actual[df_actual.OutAddinfo!=''] 
##        In_df_actual = df_actual[df_actual.InToProcess !='N'] 
##        Out_df_actual = df_actual[df_actual.OutToProcess!='N']
#        df_filteredServices = In_df_actual['InToProcess'] != 'N'
#        df_filteredServices_out = Out_df_actual['OutToProcess']  != 'N'
        df_filteredServices = df_actual.dropna(subset=['InCostshare','InAddinfo'])
        df_filteredServices_out = df_actual.dropna(subset=['OutCostshare','OutAddinfo'])
        for index, row in df_filteredServices.iterrows():
            #full_sent=row["InCostshare"].str.encode('utf-8').strip() + ' '+row["InAddinfo"].str.encode('utf-8').strip() 
            print(row["DocName"])
            incostshare =''
            full_sent =''
            inaddinfo=''
            incostshare =  row["InCostshare"]
            inaddinfo =  row["InAddinfo"] 
            
            if((inaddinfo is np.nan or inaddinfo != inaddinfo)):
                inaddinfo = ''
            if((incostshare is np.nan or incostshare != incostshare)):
                incostshare = '' 
                
                
            if isinstance(incostshare, int):
                incostshare =  str(incostshare)
                                
            if isinstance(inaddinfo, int):
                inaddinfo =  str(inaddinfo)
                
            
            
            full_sent = incostshare + ' ' + inaddinfo
#            print('***************')
#            print(full_sent)
            sentences_full = sent_tokenize(full_sent)
            sentences_partial = sent_tokenize(incostshare)
            print('***************')
            print( sentences_full)
            print('***************')
            print(sentences_partial)
            for sindex in range(0,len(sentences_partial)):
                if(sentences_full[sindex] != sentences_partial[sindex]):
                    if(inaddinfo[0].islower()):
                        df_actual.iloc[index,df_actual.columns.get_loc("InChangeFlag")] ="X"
                        df_actual.iloc[index,df_actual.columns.get_loc("InModifiedCS")] =full_sent
                    else:
                        df_actual.iloc[index,df_actual.columns.get_loc("InChangeFlag")] ="SB"
                        df_actual.iloc[index,df_actual.columns.get_loc("InModifiedCS")] =full_sent
                else: #(sentences_full[sindex] != sentences_partial[sindex]):
                    if (sentences_partial[sindex].find("%")>=0):
                        df_actual.iloc[index,df_actual.columns.get_loc("InChangeFlag")] ="P"
                        #df_actual.iloc[index,df_actual.columns.get_loc("Modified")] =incostshare
                    elif(sentences_partial[sindex].find("$") >=0):
                        df_actual.iloc[index,df_actual.columns.get_loc("InChangeFlag")] ="D"
                        #df_actual.iloc[index,df_actual.columns.get_loc("Modified")] =incostshare
                    elif(sentences_partial[sindex].lower().find("no coinsurance")>=0):
                        df_actual.iloc[index,df_actual.columns.get_loc("InChangeFlag")] ="C"
                        #df_actual.iloc[index,df_actual.columns.get_loc("Modified")] =incostshare
                    else:
                        df_actual.iloc[index,df_actual.columns.get_loc("InChangeFlag")] ="N"
        
        
        for index, row in df_filteredServices_out.iterrows():
            #full_sent=row["InCostshare"].str.encode('utf-8').strip() + ' '+row["InAddinfo"].str.encode('utf-8').strip() 
            print(row["DocName"])
            incostshare =''
            full_sent =''
            inaddinfo=''
            
            incostshare =  row["OutCostshare"]
            inaddinfo =  row["OutAddinfo"] 
#            if isinstance(row["OutCostshare"], str):
#                incostshare =   unicode(row["OutCostshare"], "utf-8")
#                print('OutCostshare******************************'+ incostshare)
#            else:
#                incostshare =  row["OutCostshare"]
#                
#            if isinstance(row["OutAddinfo"], str):
#                inaddinfo =   unicode(row["OutAddinfo"], "utf-8")
#                print('full_sent***************'+ full_sent)
#            else:
#                inaddinfo =  row["OutAddinfo"]           
#            print('***************')
#            print(full_sent)
            if((inaddinfo is np.nan or inaddinfo != inaddinfo)):
                inaddinfo = ''
            if((incostshare is np.nan or incostshare != incostshare)):
                incostshare = '' 
                
            if isinstance(incostshare, int):
                incostshare =  str(incostshare)                                
            if isinstance(inaddinfo, int):
                inaddinfo =  str(inaddinfo)
                
            full_sent = incostshare + ' '+  inaddinfo
            
            sentences_full = sent_tokenize(full_sent)
            sentences_partial = sent_tokenize(incostshare)
            print('***************')
            print( sentences_full)
            print('***************')
            print(sentences_partial)
            for sindex in range(0,len(sentences_partial)):
                if(sentences_full[sindex] != sentences_partial[sindex]):
                    if(inaddinfo[0].islower()):
                        df_actual.iloc[index,df_actual.columns.get_loc("OutChangeFlag")] ="X"
                        df_actual.iloc[index,df_actual.columns.get_loc("OutModifiedCS")] =full_sent
                    else:
                        df_actual.iloc[index,df_actual.columns.get_loc("OutChangeFlag")] ="SB"
                        df_actual.iloc[index,df_actual.columns.get_loc("OutModifiedCS")] =full_sent
                    
                else: #(sentences_full[sindex] != sentences_partial[sindex]):
                    if (sentences_partial[sindex].find("%")>=0):
                        df_actual.iloc[index,df_actual.columns.get_loc("OutChangeFlag")] ="P"
                        #df_actual.iloc[index,df_actual.columns.get_loc("ModifiedOut")] =incostshare
                    elif(sentences_partial[sindex].find("$") >=0):
                        df_actual.iloc[index,df_actual.columns.get_loc("OutChangeFlag")] ="D"
                        #df_actual.iloc[index,df_actual.columns.get_loc("ModifiedOut")] =incostshare
                    elif(sentences_partial[sindex].lower().find("no coinsurance")>=0):
                        df_actual.iloc[index,df_actual.columns.get_loc("OutChangeFlag")] ="C"
                        #df_actual.iloc[index,df_actual.columns.get_loc("ModifiedOut")] =incostshare
                    else:
                        df_actual.iloc[index,df_actual.columns.get_loc("OutChangeFlag")] ="N"
                                        
        print(df_actual.shape)            
        df_actual.to_excel(working_dir+ ticket +"\\" +filename  +"_NLP.xlsx")          
    except Exception as ex:
        exc_type,exc_obj,exc_tb=sys.exc_info()
        print("MLOperation.....Error")
        print(exc_tb.tb_lineno)
        print(ex)
    

def FileProcess(ticket,filename,sheetname):
    try:   
        file_name=filename  #'anthem_ky_services'
        Sheet_name= "Sheet1"
        MLOperation(ticket,file_name,Sheet_name)
    except Exception as ex:
        print("FileProcess.....Error")
        print(ex)

def callserviceProcessing(ticket,filename,sheetnumber):
    FileProcess(ticket,filename,sheetnumber)        

#FileProcess("SE-287305","SE-287305_SE","") 
