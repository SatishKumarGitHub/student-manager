# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 18:01:32 2020

@author: Mahesh_Kanthaswamy
"""

from SQLConnector import SqlOperation
from flask import Flask , jsonify,request,send_from_directory,render_template
objSql = SqlOperation() 
import pandas as pd
from Navigation import Navigation
from Sunburst import Sunburst
app = Flask(__name__)


@app.route('/')
def load_home():
    
    return render_template("sample.html")

@app.route('/projectsummary')
def get_summary():
    with open("Scripts/ProjectSummary.Sql",'r') as sql:
        query=sql.read()
    sqlResult =objSql.read_sql(query)
    return sqlResult

@app.route('/getprojecttree')
def get_projecttree():
    with open("Scripts/ProjectTree.Sql",'r') as sql:
        query=sql.read()
    sqlResult =objSql.read_sql(query)
    return sqlResult

@app.route('/getnavigationtree')
def get_navigation_tree():
    with open("Scripts/ProjectDynamicSample.Sql",'r') as sql:
        query=sql.read()
    df_result =objSql.read_sql_dataframe(query)
    print(df_result.head())
    objNavi = Navigation(json_file="project_dynamic")
    json_result=objNavi.sql_json_mapping()
    return json_result

@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    return send_from_directory(directory="out_json", filename=filename)

@app.route('/getsunburstree')
def get_sunburn_tree():
    substance=request.args["substance"]
    print("get_sunburn_tree-In-Arg",substance)
    objSunburst = Sunburst(json_file="sunburst")
    json_result=objSunburst.sql_sunburst_mapping(request.args)
    return str(json_result)

if __name__ == '__main__':
    app.run(debug=True)
