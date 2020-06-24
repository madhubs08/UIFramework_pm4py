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


        return render(request,'filter.html')



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
