

# -*- coding: utf-8 -*-

import json ,sys,os
import configparser as cp
import Logger as Log
from datetime import datetime
import pandas as pd
from SQLConnector import SqlOperation
from flask import Flask , jsonify


class Navigation():
    def __init__(self,json_file="ProjectDynamic"):
        config = cp.RawConfigParser()
        config.read("Application.properties")
        self.json_file=config.get('SYMPHONY',json_file)
        self.log_time= str(datetime.strftime(datetime.now(),"%Y%m%d%H%M%S"))
        self.log_path= config.get("APPSETTINGS","LOG_PATH")
        self.app_name= config.get("APPSETTINGS","APP_NAME")
        self.json_result={}
        self.json_template={}
        self.json_substance=[]
        self.json_recursive={}
        self.df_recursive=None
        self.df_substances=None
#    def sql_json_iterator(self,table,columns,parent_col,where_values,json_):
#        try:
#                
#        except Exception as ex:
#        exc_type,exc_obj,exc_tb=sys.exc_info()
#        Log.write_output(self.log_path,self.app_name,"Error","{}^{}^{}^{}".format("read_sql",str(datetime.now()), exc_tb.tb_lineno ,ex))
#        print("Error in sql_json_mapping method at {}, Error Message---- {} ".format(exc_tb.tb_lineno,ex))
#        return None
        
    def extract_db(self,step_index,table_name,where_condition,parent_column,db_query):
        try:
            objSql = SqlOperation() 
            query =db_query
            if (query==None or query=="" ):
                if(parent_column ==None and where_condition==""):
                    query= "SELECT * FROM {0} ".format(table_name)
                else:
                    query= "SELECT * FROM {0} WHERE {1} IN ({2})".format(table_name,parent_column,where_condition) #",".join([str(x) for x in lst_where_columns])))  
            else:
                if (parent_column is not None ):
                    query=query.replace("#WHERECOL#",parent_column)
                if (where_condition is not None):
                    if (type(where_condition)==str):
                        query=query.replace("#WHEREVAL#","'{}'".format(str(where_condition)))
                    else:
                        query=query.replace("#WHEREVAL#",str(where_condition))
            #print("extract_db-1",query)
            df_result =objSql.read_sql_dataframe(query)
            return df_result
        except Exception as ex:
            exc_type,exc_obj,exc_tb=sys.exc_info()
            Log.write_output(self.log_path,self.app_name,"Error","{}^{}^{}^{}".format("read_sql",str(datetime.now()), exc_tb.tb_lineno ,ex))
            print("Error in sql_json_mapping method at {}, Error Message---- {} ".format(exc_tb.tb_lineno,ex))
            return None
        
    def iterate_steps(self,step_index,where_value,record_index,json_2_update):
        try:
            #'Table to proces '
            #print("json_template",len(self.json_template))
            if(step_index <len(self.json_template)):
                item=self.json_template[step_index]
                table_name=item["Table"]
                primary_column =item["PrimaryColumn"]
                table_alias=item["TableAlias"]
                lst_columns=item["Columns"]
                columns_alias=item["ColumnAlias"]
                parent_table=item["ParentTable"]
                parent_column=item["ParentColumn"]
                db_query=item["DBQuery"]
                recursive=item["Recursive"]

                #'Select  from Table with conditions'
                df_result=self.extract_db(step_index,table_name,where_value,parent_column,db_query)
                #'Post process Columns 
                df_filtered =df_result[lst_columns]
                if (len(columns_alias)>0):
                    dict_cols= dict(zip(lst_columns, columns_alias))
                    df_filtered.rename(columns=dict_cols, inplace=True)
                    
                
    #            lst_where_columns=df_filtered[primary_column].unique()
                #'update json values
                if (record_index==-1):
                    json_2_update={table_alias:json.loads(df_filtered.to_json(orient='records'))}
                else:
                    #json_inner= {table_alias:json.loads(df_filtered.to_json(orient='records'))}
                    json_2_update[table_alias] =json.loads(df_filtered.to_json(orient='records'))
                #print(json_2_update)
                #'loop through Records
                next_step=step_index+1
                if(next_step <len(self.json_template)):
                    for index,row in df_filtered.iterrows():
                        #print(next_step,"^",row[primary_column],"^",index,"^",json_2_update[table_alias][index])
                        self.iterate_steps(next_step,row[primary_column],index,json_2_update[table_alias][index])
                if (recursive==True):          
                    if self.df_substances is not None:
                        self.df_substances = self.df_substances.append(df_filtered , ignore_index=True)
                    else:
                        self.df_substances=pd.DataFrame(df_filtered)       
            return json_2_update
        except Exception as ex:
            exc_type,exc_obj,exc_tb=sys.exc_info()
            Log.write_output(self.log_path,self.app_name,"Error","{}^{}^{}^{}".format("read_sql",str(datetime.now()), exc_tb.tb_lineno ,ex))
            print("Error in sql_json_mapping method at {}, Error Message---- {} ".format(exc_tb.tb_lineno,ex))
            return None
    

    def substance_recursive(self,json_in):
        try:
            print("****************** Recursive Start***************************")
            self.df_substances=self.df_substances.drop_duplicates()
            projects= json_in["Projects"]
            for project in projects:
                for campaign in project["Campaign"]:
                    for synthesys in campaign["Synthesys"]:
                        self.json_substance=[]
                        subs = synthesys["Substance"]
                        synthesysId =synthesys["SynthesysId"]
                        #print("substance_recursive",synthesysId,subs)
                        self.json_recursive=subs
                        df_filtered= self.df_substances[self.df_substances["RefCol"]==synthesysId]
                        self.df_recursive=df_filtered
                        #print("df_filtered",df_filtered)
                        
                        df_temp= df_filtered[df_filtered["StepToSubstanceName"].isnull()]
                        
                        #print("substance_recursive-Before",self.json_recursive)
                        self.json_recursive=self.substance_iterate(df_temp)
                        #print("substance_recursive--After",self.json_recursive)
                        subs=self.json_recursive
                        del synthesys["Substance"]
                        synthesys["TargetSubstance"]=subs
                        #print("substance_recursive",subs)
            #print("substance_recursive_jsonin",json_in)
            print("****************** Recursive End***************************")
            return json_in   
        except Exception as ex:
            exc_type,exc_obj,exc_tb=sys.exc_info()
            Log.write_output(self.log_path,self.app_name,"Error","{}^{}^{}^{}".format("read_sql",str(datetime.now()), exc_tb.tb_lineno ,ex))
            print("Error in json_recursive method at {}, Error Message---- {} ".format(exc_tb.tb_lineno,ex))
            return None

    
    def json_tree_process(self,json_obj,element_to_search,new_tag,tag_value):
        try:
            #print("json_tree_process----",json_obj,element_to_search,new_tag,tag_value)
            if(type(json_obj) == list):
                for obj in json_obj:
                    #print("json_tree_process", obj)
                    obj=self.json_tree_process(obj,element_to_search,new_tag,tag_value)
                return json_obj
            elif(type(json_obj) == dict):
                for key in list(json_obj.keys()):
                    if(type(json_obj[key]) == list ):
                        if(key==new_tag):
                            #print("json_obj-new_tag",json_obj[key])
                            json_obj=self.json_tree_process(json_obj[key],element_to_search,new_tag,tag_value)
                            return json_obj
                    if(type(json_obj[key]) == str ):
                        if(json_obj[key]==element_to_search):
                            #print("json_obj-Key",json_obj)
                            if new_tag in json_obj:
                                json_obj[new_tag].append(tag_value)
                            else:
                                json_obj[new_tag]=[tag_value]
                            #print("json_obj-Key-2",json_obj)
                            return json_obj
                           
            return json_obj  
        except Exception as ex:
            exc_type,exc_obj,exc_tb=sys.exc_info()
            Log.write_output(self.log_path,self.app_name,"Error","{}^{}^{}^{}".format("read_sql",str(datetime.now()), exc_tb.tb_lineno ,ex))
            print("Error in json_tree_process method at {}, Error Message---- {} ".format(exc_tb.tb_lineno,ex))
            return None       
    
    def substance_iterate(self,df_temp):
        try:
            for index,row in df_temp.iterrows():
                substanceName=row["SubstanceName"]
                print("Recursive",index,row["StepToSubstanceName"] is None, substanceName,df_temp,self.json_recursive)
                if(row["StepToSubstanceName"] is None):
                    for i in range(len(self.json_recursive)):
                        print("Recursive-2",type(self.json_recursive),self.json_recursive[i]['SubstanceName'],self.json_recursive[i])
                        if (self.json_recursive[i]['SubstanceName'] == substanceName):
                            self.json_substance.append(self.json_recursive[i])
                            del self.json_recursive[i]
                            break
                else:
                    for i in range(len(self.json_recursive)):
                        print("Recursive-3",self.json_recursive[i]['SubstanceName'])
                        if (self.json_recursive[i]['SubstanceName'] == substanceName):
                            print("Recursive-3-1-",self.json_recursive[i])
                            subsitute_element= self.json_recursive[i]
                            del self.json_recursive[i]
                            self.json_substance=self.json_tree_process(self.json_substance,row["StepToSubstanceName"],"Substance",subsitute_element) 
                            break
                df_temp_filter= self.df_recursive[self.df_recursive["StepToSubstanceName"] ==substanceName]
                print("Recursive-4-DF-Size is empty", df_temp_filter.empty)
                if(df_temp_filter.empty==False):
                    self.substance_iterate(df_temp_filter)
            print("Recursive-FINAL",self.json_substance)
            return self.json_substance    
        except Exception as ex:
            exc_type,exc_obj,exc_tb=sys.exc_info()
            Log.write_output(self.log_path,self.app_name,"Error","{}^{}^{}^{}".format("read_sql",str(datetime.now()), exc_tb.tb_lineno ,ex))
            print("Error in substance_iterate , at {}, Error Message---- {} ".format(exc_tb.tb_lineno,ex))
            return None
      
    def sql_json_mapping(self):
        try:
            json_result = {}
            with open(self.json_file,"r") as file:
                self.json_template=json.load(file)
                
            json_result=self.iterate_steps(0,"",-1,json_result)
            #print("sql_json_mapping",self.df_substances.head())
            
            jon_result=self.substance_recursive(json_result)
            #print("sql_json_mapping-after",jon_result)            
            return json.dumps(json_result, indent = 4)

        except Exception as ex:
            exc_type,exc_obj,exc_tb=sys.exc_info()
            Log.write_output(self.log_path,self.app_name,"Error","{}^{}^{}^{}".format("read_sql",str(datetime.now()), exc_tb.tb_lineno ,ex))
            print("Error in sql_json_mapping method at {}, Error Message---- {} ".format(exc_tb.tb_lineno,ex))
            return None


if __name__ == '__main__':
    objNavi = Navigation(json_file="project_dynamic")
    json_result=objNavi.sql_json_mapping()
    with open(os.path.join("out_json","Navigation_1.5_1" + '.json'), 'w', encoding ='utf8') as json_file: 
        json.dump(json_result, json_file,indent = 4, ensure_ascii = True) 
    #print(json_result
   