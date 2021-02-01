# -*- coding: utf-8 -*-
'''
Author: Mahesh Kanthasamy
'''
import json ,sys,os
import configparser as cp
import Logger as Log
from datetime import datetime
import pandas as pd
from SQLConnector import SqlOperation
from flask import Flask , jsonify
import secrets

class ComposerETL():
    def __init__(self,json_file="composer"):
        config = cp.RawConfigParser()
        config.read("Application.properties")
        self.json_file=config.get('SYMPHONY',json_file)
        self.log_time= str(datetime.strftime(datetime.now(),"%Y%m%d%H%M%S"))
        self.log_path= config.get("APPSETTINGS","LOG_PATH")
        self.app_name= config.get("APPSETTINGS","APP_NAME")
        self.sunburst_inculude_id= config.get("SYMPHONY","sunburst_inculude_id")
        self.sunburst_roles= config.get("SYMPHONY","sunburst_roles")
        self.sunburst_status= config.get("SYMPHONY","sunburst_status")
        self.sunburst_val_query= config.get("SYMPHONY","sunburst_val_query")
        self.json_result={}
        self.json_to_update={}
        self.json_template={}
        self.json_substance=[]
        self.json_recursive={}
        self.df_recursive=None
        self.df_substances=None
        self.dict_parent_index={}
        self.table_index=1
        self.primary_key_alias=config.get("SYMPHONY","primary_key_alias")
        self.table_alias=config.get("SYMPHONY","version") 
    def extract_db(self,step_index,table_name,where_condition,parent_column,db_query):
        try:
            objSql = SqlOperation() 
            query =db_query
            if (query==None or query=="" ):
                if(parent_column ==None and where_condition==""):
                    query= "SELECT * FROM {0} ".format(table_name)
                else:
                    if (type(where_condition)==list):
                        query= "SELECT * FROM {0} WHERE {1} IN ('{2}')".format(table_name,parent_column,"','".join([str(x) for x in where_condition]))  
                    else:
                        query= "SELECT * FROM {0} WHERE {1} IN ('{2}')".format(table_name,parent_column,where_condition)  
            else:
                if (parent_column is not None ):
                    query=query.replace("#WHERECOL#",parent_column)
                if (where_condition is not None):
                    if (type(where_condition)==list):
                        query=query.replace("#WHEREVAL#","','".join([str(x) for x in where_condition]))
                    else:
                        query=query.replace("#WHEREVAL#","'{}'".format(str(where_condition)))
                        
            #print("extract_db-1",query)
            df_result =objSql.read_sql_dataframe(query)
            return df_result
        except Exception as ex:
            exc_type,exc_obj,exc_tb=sys.exc_info()
            Log.write_output(self.log_path,self.app_name,"Error","{}^{}^{}^{}".format("read_sql",str(datetime.now()), exc_tb.tb_lineno ,ex))
            print("Error in Sunburst-extract_db method at {}, Error Message---- {} ".format(exc_tb.tb_lineno,ex))
            return None
            
    def prepare_ddl_sql(self,table_name,json_in,cols_to_process,modified_cols,primary_key,parent_column,parent_table):
        try:
            '''
            query="CREATE TABLE {0} ( ".format(table_name)
            query+=" {0} INT IDENTITY(1,1) NOT NULL, ".format(primary_key)
            for i in range(0,len(cols_to_process)):
                query+=" {0} nvarchar(500) NULL, ".format(modified_cols[i])
            query+=" {0} nvarchar(500) NULL, ".format("Content")
            query+=" {0} INT NOT NULL, ".format(parent_column)
            query+=" primary key({0}), ".format(primary_key)
            query+=" foreign key({0}) references {1}({0}) ) ".format(parent_column,parent_table)l
            '''
            query="CREATE TABLE dbo.{0} ( ".format(table_name)
            query+=" {0} INT IDENTITY(1,1) NOT NULL, ".format(primary_key)
            query+=" {0} nvarchar(50) NULL , ".format("_id")
            for i in range(0,len(cols_to_process)):
                query+=" {0} nvarchar(500) NULL, ".format(modified_cols[i])

            query+=" {0} nvarchar(500) NULL, ".format("Content")
            if (parent_column is not None):
                query+=" {0} INT NOT NULL, ".format(parent_column)
            query+=" CONSTRAINT [pk_{1}{0}] PRIMARY KEY CLUSTERED ([{0}] ASC )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]) ON [PRIMARY]".format(primary_key,self.table_alias)
            
            if (parent_column is not None):
                query+=" ALTER TABLE [dbo].[{0}]  WITH NOCHECK ADD  CONSTRAINT [fk_{0}{1}_1O5] FOREIGN KEY([{1}]) REFERENCES [dbo].[{2}] ([{1}])  ALTER TABLE [dbo].[{0}] CHECK CONSTRAINT [fk_{0}{1}_1O5]".format(table_name,parent_column,parent_table)
            print(query)
            Log.write_output(self.log_path,self.app_name,"Log","{}^{}^{}".format("prepare_ddl_sql",str(datetime.now()), query))
            
            return query
        except Exception as ex:
            exc_type,exc_obj,exc_tb=sys.exc_info()
            Log.write_output(self.log_path,self.app_name,"Error","{}^{}^{}^{}".format("prepare_sql",str(datetime.now()), exc_tb.tb_lineno ,ex))
            print("Error in Sunburst-prepare_sql method at {}, Error Message---- {} ".format(exc_tb.tb_lineno,ex))
            return None
        
    def prepare_dml_sql(self,table_name,json_in,cols_to_process,modified_cols,primary_key,parent_column,parent_table,parent_value,_id):
        try:
            checkifNone = lambda x: '' if(x is None)  else str(x)[0:450]

            lst_col_values=["'"+ checkifNone(json_in[col]) + "'"  for col in cols_to_process ]
            query="INSERT INTO  {0} ({1},{2})".format(table_name,",".join(modified_cols),parent_column,"_id")
            if (parent_column is not None and len(cols_to_process)>0):
                query="INSERT INTO  {0} ({1},{2},{3})".format(table_name,",".join(modified_cols),parent_column,"_id")
                query+=" Values ({0},'{1}','{2}')  ".format(",".join(lst_col_values),parent_value,_id)
            elif(parent_column is not None and len(cols_to_process)==0):
                query="INSERT INTO  {0} ({2},{3})".format(table_name,",".join(modified_cols),parent_column,"_id")
                query+=" Values ('{1}','{2}')  ".format(",".join(lst_col_values),parent_value,_id)
            elif(parent_column is  None and len(cols_to_process)>0):
                query="INSERT INTO  {0} ({1},{3})".format(table_name,",".join(modified_cols),parent_column,"_id")
                query+=" Values ({0},'{2}')  ".format(",".join(lst_col_values),parent_value,_id)
            else:
                query+=" Values ({0},'{1}','{2}') ".format(",".join(modified_cols),parent_value,_id)
            if (parent_table is None):
                parent_table="NoTable"
            Log.write_output(self.log_path,self.app_name,"Log","{}^{}^{}".format("prepare_dml_sql",str(datetime.now()), query))
            Log.write_output(self.log_path,self.app_name,"Log",'{0}^{5}^"Table":"{1}","ParentIndex":0,"TableAlias":"{2}","PrimaryColumn":"{3}","Columns":[{4}],"ColumnAlias":[ ],"ParentTable":"{5}","ParentColumn":"{6}","DBQuery":"","TagName":"data","ParentTag":"","Transpose":"Yes","AdditionalTage":null,"DummyElement":"Substance",'.format("InsertData",table_name,table_name[4:],primary_key, '","'.join(modified_cols),parent_table[4:],parent_column))
            print("prepare_dml_sql",query)
            return query
        except Exception as ex:
            exc_type,exc_obj,exc_tb=sys.exc_info()
            Log.write_output(self.log_path,self.app_name,"Error","{}^{}^{}^{}".format("prepare_sql",str(datetime.now()), exc_tb.tb_lineno ,ex))
            print("Error in Sunburst-prepare_dml_sql method at {}, Error Message---- {} ".format(exc_tb.tb_lineno,ex))
            return None
    def prepare_columns(self,col_names):
        try:
            modified_cols=[]
            for col_name in col_names:
                col_name=col_name.replace("-","_").replace(" ","_").replace("'","_").replace('"',"_").replace("-","_").replace("limit","limits")
                modified_cols.append(col_name)
                #print("prepare_columns","--", col_name,"--",len(col_name))
                Log.write_output(self.log_path,self.app_name,"Log","{}^{}^{}".format("prepare_columns",str(datetime.now()), str(modified_cols)))   
            return modified_cols
        except Exception as ex:
            exc_type,exc_obj,exc_tb=sys.exc_info()
            Log.write_output(self.log_path,self.app_name,"Error","{}^{}^{}^{}".format("read_sql",str(datetime.now()), exc_tb.tb_lineno ,ex))
            print("Error in Sunburst-extract_db method at {}, Error Message---- {} ".format(exc_tb.tb_lineno,ex))
            return col_name
    def create_db_object(self,table_name,json_in,cols_to_process,primary_key,parent_column,parent_table,parent_value,_id):
        try:
            where_val=""
            objSql = SqlOperation() 
                       
            modified_cols=self.prepare_columns(cols_to_process)
            print("create_db_object","--",table_name,"--",modified_cols,"--",primary_key,"--",parent_table,"--",parent_column,"--", parent_value)
            
            #Check if table exists:
            
            df_sql = self.extract_db(0,table_name,"",None,"SELECT Top 1 * from "+ table_name)
                
            if(df_sql is None ):
                query =self.prepare_ddl_sql(table_name,json_in,cols_to_process,modified_cols,primary_key,parent_column,parent_table)
                no_of_rows = objSql.dml_sql(query)
                

            #Columns validation:

            #Create Table:

            #Import data
            query =self.prepare_dml_sql(table_name,json_in,cols_to_process,modified_cols,primary_key,parent_column,parent_table,parent_value,_id)
            df_sql = objSql.dml_sql(query)
            #query= "SELECT * FROM {0} ORDER BY {1} desc LIMIT 1".format(table_alias,primary_key)
            query= "SELECT top 1 * FROM {0} ORDER BY {1} desc ".format(table_name,primary_key)
            df_sql = self.extract_db(0,table_name,"",None,query)
            if (df_sql.empty==False):
                where_val=df_sql.iloc[0].at[primary_key]

            
            return where_val
        except Exception as ex:
            exc_type,exc_obj,exc_tb=sys.exc_info()
            Log.write_output(self.log_path,self.app_name,"Error","{}^{}^{}^{}".format("update_panel_json",str(datetime.now()), exc_tb.tb_lineno ,ex))
            print("Error in Sunburst-create_db_object method at {}, Error Message---- {} ".format(exc_tb.tb_lineno,ex))
            return None
   
    def injsonprocess(self,json_in,parent_table,parent_column,parent_value):
        try:
            is_last_step= False
            if (json_in is not None):
                if (type(json_in)==list and json_in):
                    list_index=0
                    _id=secrets_id=secrets.token_hex(12)
                    for i in range(len(json_in)):
                        step=json_in[i]
                        if ("@Type" in step.keys()):
                            key_columns=step.keys()
                            table_name=step["@Type"]
                            table_name=table_name.replace("-","_")
                            primary_key=table_name+self.primary_key_alias
                            table_name=self.table_alias + table_name
                            roles=""
                            if ("@Views" in key_columns):
                                roles=str(step["@Views"])
                            if ("contributor" in key_columns):
                                contributor=str(json_in["contributor"])
                            Log.write_output(self.log_path,self.app_name,"Log_roles",'{0}^{1}^{2}^{3}^{4}^{5}^{6}'.format("TrackRoles",table_name,roles,table_name[4:],primary_key,parent_table,parent_column))
                            keys_table=[key for key in key_columns if key in ["@Type","@Views","contributor"] ]
                            keys_loop= [key for key in key_columns if isinstance(step[key],(list,dict)) and key not in keys_table]
                            cols_to_process= [key for key in key_columns if key not in keys_table+keys_loop]
                            where_val=self.create_db_object(table_name,step,cols_to_process,primary_key,parent_column,parent_table,parent_value,_id)

                            if(len(keys_loop)==0):
                                is_last_step=True
                            else:
                                for keycol in keys_loop:
                                    self.injsonprocess(step[keycol],table_name,primary_key,where_val)
                
                elif (type(json_in)==dict and json_in):  
                    if ("@Type" in json_in.keys()):
                        _id=secrets_id=secrets.token_hex(12)
                        key_columns=json_in.keys()
                        table_name=json_in["@Type"]
                        table_name=table_name.replace("-","_")
                        primary_key=table_name+self.primary_key_alias
                        table_name=self.table_alias + table_name
                        roles=""
                        if ("@Views" in key_columns):
                            roles=str(json_in["@Views"])
                        if ("contributor" in key_columns):
                            contributor=str(json_in["contributor"])
                        Log.write_output(self.log_path,self.app_name,"Log_roles",'{0}^{1}^{2}^{3}^{4}^{5}^{6}'.format("TrackRoles",table_name,roles,table_name[4:],primary_key,parent_table,parent_column))
                        keys_table=[key for key in key_columns if key in ["@Type","@Views","contributor"] ]
                        
                        keys_loop= [key for key in key_columns if isinstance(json_in[key],(list,dict)) and key not in keys_table]
                        cols_to_process= [key for key in key_columns if key not in keys_table+keys_loop]
                        where_val=self.create_db_object(table_name,json_in,cols_to_process,primary_key,parent_column,parent_table,parent_value,_id)
                        #self.injsonprocess(keys_loop,parent_column,where_val)
                        if(len(keys_loop)==0):
                            is_last_step=True
                        else:
                            for keycol in keys_loop:
                                self.injsonprocess(json_in[keycol],table_name,primary_key,where_val)

                '''
                if (is_last_step==False):
                    json_to_update=self.injsonprocess(dict_record,self.json_to_update,where_value,index)
                '''

        except Exception as ex:
            exc_type,exc_obj,exc_tb=sys.exc_info()
            Log.write_output(self.log_path,self.app_name,"Error","{}^{}^{}^{}".format("injsonprocess",str(datetime.now()), exc_tb.tb_lineno ,ex))
            print("Error in Sunburst -injsonprocess  at {}, Error Message---- {} ".format(exc_tb.tb_lineno,ex))
            return None
     
    
    def sql_sunburst_mapping(self,dic_args): # project,campaign,synthesys,substance
        try:
            json_in = None
            json_out=None
            arg_list=dic_args.keys()
            composer_file_name=dic_args["composer_file_name"]              
            with open(os.path.join("schema",composer_file_name),"r") as file:
                self.json_template=json.load(file)
            if(type(self.json_template)==list):
                self.json_template=self.json_template[0]
            json_result=self.injsonprocess(self.json_template,"",None,"")
            
                        
            return json.dumps(json_result, indent = 4)

        except Exception as ex:
            exc_type,exc_obj,exc_tb=sys.exc_info()
            Log.write_output(self.log_path,self.app_name,"Error","{}^{}^{}^{}".format("sql_sunburst_mapping",str(datetime.now()), exc_tb.tb_lineno ,ex))
            print("Error in Sunburst-sql_sunburst_mapping method at {}, Error Message---- {} ".format(exc_tb.tb_lineno,ex))
            return None

 
if __name__ == '__main__':
    
    objSunburst = ComposerETL(json_file="sunburst")
    dic_args={}
    dic_args["project"]=""
    dic_args["campaign"]=""
    dic_args["synthesys"]="Z"
    dic_args["composer_file_name"]="composer-eprint-99.json"
    json_result=objSunburst.sql_sunburst_mapping(dic_args)
    

