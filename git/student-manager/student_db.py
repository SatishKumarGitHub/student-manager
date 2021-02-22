
import sqlite3
import hashlib
import datetime
import pandas as pd

student_db_file_location = "database_file/student.db"
def create_student_table(query):
    _conn = sqlite3.connect(student_db_file_location)
    _c = _conn.cursor()

    _c.execute(query)
    
    _conn.commit()
    _conn.close()
    

def add_student(table_name,df_students):
    try:
        _conn = sqlite3.connect(student_db_file_location)
        _c = _conn.cursor()
        columns =",".join(df_students.columns.tolist())
        print(columns)
        df_students['DOB'] = df_students['DOB'].astype(str)
        df_students['Weight'] = df_students['Weight'].astype(str)
        df_students['Age'] = df_students['Age'].astype(str)
        df_students['Height'] = df_students['Height'].astype(str)
        #text_to_write = request.form.get("text_note_to_take")
        for index,row in df_students.iterrows():
            print('lst_row',row.tolist())
            lst_row ="','".join(row.tolist())
            query="insert into " + table_name + "(" + columns + ")  values('" + lst_row + "')"
            print(query)
            _c.execute(query)
            
        _conn.commit()
        _conn.close()
    except Exception as e:
        print(e)


	
if __name__ == "__main__":
    df_students=pd.read_excel('database_file/Book2.xlsx')
    QUERY="CREATE TABLE Student (	RollNo	TEXT	,	Name	TEXT,	Department	TEXT	,DOB	TEXT	,	Age	TEXT	,	Weight	TEXT,	Height	TEXT	,	Game	TEXT	);"
    columns =",".join(df_students.columns.tolist())
    #print(columns)
    # create_student_table(QUERY)
    add_student("Student",df_students)
