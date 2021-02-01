import os
def write_output(log_path="",app_name="Generic",infile_name="",logs=""):
    try:
        with open(os.path.join(log_path+"_"+infile_name+".txt"),'a') as file:
            file.write('%s\n' % logs.encode('utf-8').strip())
        
    except Exception as ex:
        print(ex)