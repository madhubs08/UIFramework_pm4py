import os
from collections import defaultdict
from flask import Flask, render_template, request, url_for,redirect
import pandas as pd
from flask import send_file,make_response


cwd = os.getcwd()
mainapp = Flask(__name__)
mainapp.config['CACHE_TYPE']='null'
mainapp.config['UPLAOD_FOLDER']=os.path.join(str(cwd),"static","images")
mainapp.config["FILE_UPLOADS"] = os.path.join(str(cwd),"static","images")
ALLOWED_EXTENSIONS = set(['csv','txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
mainapp.config['SESSION_TYPE'] = 'filesystem'

@mainapp.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@mainapp.route('/')
def get_first_page():
   return render_template('bootstrapTemplate.html')

@mainapp.route('/upload.html', methods=['POST','GET'])
def get_pre_event_log():

    event_log_cols =[]
    event_log_cols_map= []
    el_info= ""
    download_file=''
    response=''
    if request.method == 'POST':
        el_info = "Post request received"

    return download_file, render_template('upload.html', el_cols=event_log_cols,el_info =el_info)

@mainapp.route('/upload.html')
def get_event_log():

    return render_template('upload.html')


if __name__ == '__main__':
   mainapp.run(debug = True,  threaded=True)
