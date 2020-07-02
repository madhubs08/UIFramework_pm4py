import shutil

from django.shortcuts import render
from django.conf import settings
import os
from os import path
from datetime import datetime
from django.http import HttpResponseRedirect, HttpResponse
from wsgiref.util import FileWrapper



# Create your views here.

def filter(request):
    if request.method == 'POST':


        event_logs_path = os.path.join(settings.MEDIA_ROOT, "event_logs")
        temp_path = os.path.join(settings.MEDIA_ROOT, "temp")

        if settings.EVENT_LOG_NAME == ':notset:':
            return HttpResponseRedirect(request.path_info)

        values = setValues(request)
        event_log = os.path.join(event_logs_path, settings.EVENT_LOG_NAME)
        MinMax = [True, True]
        if values['LowerUpper'] == "LowerUpper":
            MinMax = [True, True]
        elif values['LowerUpper'] == "Lower":
            MinMax = [True, False]
        elif values['LowerUpper'] == "Upper":
            MinMax = [False, True]

        resource_aware = False
        hashedActivities = False

        if 'resourceAware' in values:
            resource_aware = True
        if 'hashedAct' in values:
            hashedActivities =True

        show_final_result = False

        event_log = os.path.join(event_logs_path, settings.EVENT_LOG_NAME)
        exportPrivacyAwareLog = True

        now =datetime.now()
        date_time = now.strftime(" %m-%d-%y %H-%M-%S ")
        new_file_name = values['RoleMining_Tech'] + date_time + settings.EVENT_LOG_NAME
        privacy_aware_log_path = os.path.join(temp_path, "role_mining", new_file_name)

        settings.ROLE_FILE = privacy_aware_log_path
        settings.ROLE_APPLIED = True

        if os.path.isfile(settings.ROLE_FILE):
            values['load'] = False
        else:
            values['load'] = True

        #outputs = get_output_list("role_mining")

        return render(request,'role_main.html', {'log_name': settings.EVENT_LOG_NAME, 'values':values})

    else:
        values = {}
        values['fixedValue'] = 2
        values['LowerUpper'] = 'LowerUpper'
        values['fixedValueFreq'] = 1
        values['resourceAware'] = 'resourceAware'
        values['hashedAct'] = 'hashedAct'

        if not (os.path.isfile(settings.ROLE_FILE)) and settings.ROLE_APPLIED:
            values['load'] = True
        else:
            settings.ROLE_APPLIED = False
            values['load'] = False

        #outputs = get_output_list("role_mining")
        outputs = {}

        return render(request, 'role_main.html',
                      {'log_name': settings.EVENT_LOG_NAME, 'values': values, 'outputs': outputs})

        #return render(request, 'upload.html')

def setValues(request):
    values = {}
    values['RoleMining_Tech'] = request.POST['RoleMining_Tech']
    values['fixedValue'] = request.POST['fixedValue']
    values['LowerUpper'] = request.POST['LowerUpper']
    values['fixedValueFreq'] = request.POST['fixedValueFreq']
    if 'resourceAware' in request.POST:
        values['resourceAware'] = request.POST['resourceAware']
    if 'hashedAct' in request.POST:
        values['hashedAct'] = request.POST['hashedAct']

    return values


def get_output_list(directoty):
    temp_path = os.path.join(settings.MEDIA_ROOT, "temp")
    output_path = os.path.join(temp_path, directoty)
    outputs = [f for f in os.listdir(output_path) if
                           os.path.isfile(os.path.join(output_path, f))]
    return outputs
