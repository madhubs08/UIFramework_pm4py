import shutil

from django.shortcuts import render
from django.conf import settings
import os
from os import path
from datetime import datetime
from django.http import HttpResponseRedirect, HttpResponse
from wsgiref.util import FileWrapper
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.objects.log.importer.xes import importer
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.algo.discovery.dfg import factory as dfg_factory
import json
import re




# Create your views here.

def filter(request):
    print(request.method)
    if request.method == 'POST':
        if "uploadButton" in request.POST:
            print("in request")
        event_logs_path = os.path.join(settings.MEDIA_ROOT, "event_logs")
        temp_path = os.path.join(settings.MEDIA_ROOT, "temp")

        if settings.EVENT_LOG_NAME == ':notset:':
            return HttpResponseRedirect(request.path_info)

        event_log = os.path.join(event_logs_path, settings.EVENT_LOG_NAME)

        event_log = os.path.join(event_logs_path, settings.EVENT_LOG_NAME)
        exportPrivacyAwareLog = True
        log = importer.apply(event_log)
        dfg = dfg_discovery.apply(log)
        print("dfg=" + dfg)
        dfg = dfg_factory.apply(log)
        print(dfg)
        this_data = dfg_to_g6(dfg)


        network = {}

        return render(request,'filter.html', {'log_name': settings.EVENT_LOG_NAME, 'data':this_data})

    else:
        if "groupButton" in request.GET:
            print("in request")
            groupname = request.GET["new_name"]
            activities = request.GET["groupButton"]

            print(groupname)
            print(activities)
        else:
            event_logs_path = os.path.join(settings.MEDIA_ROOT, "event_logs")
            temp_path = os.path.join(settings.MEDIA_ROOT, "temp")

            if settings.EVENT_LOG_NAME == ':notset:':
                return HttpResponseRedirect(request.path_info)

            event_log = os.path.join(event_logs_path, settings.EVENT_LOG_NAME)

            event_log = os.path.join(event_logs_path, settings.EVENT_LOG_NAME)
            exportPrivacyAwareLog = True
            log = importer.apply(event_log)
            dfg = dfg_discovery.apply(log)
            dfg = dfg_factory.apply(log)
            print(dfg)
            this_data,temp_file = dfg_to_g6(dfg)

            re.escape(temp_file)
            network = {}

            return render(request,'filter.html', {'log_name': settings.EVENT_LOG_NAME, 'json_file': temp_file, 'data':json.dumps(this_data)})

def dfg_to_g6(dfg):
    unique_nodes = []

    for i in dfg:
        unique_nodes.extend(i)
    unique_nodes = list(set(unique_nodes))

    unique_nodes_dict = {}

    for index, node in enumerate(unique_nodes):
        unique_nodes_dict[node] = "node_" + str(index)

    nodes = [{'id': unique_nodes_dict[i], 'label': i} for i in unique_nodes_dict]
    edges = [{'from': unique_nodes_dict[i[0]], 'to': unique_nodes_dict[i[1]], "data": {"freq": dfg[i]}} for i in
             dfg]
    data = {
        "nodes": nodes,
        "edges": edges,
    }
    temp_path = os.path.join(settings.MEDIA_ROOT, "temp")
    temp_file = os.path.join(temp_path, 'data.json')
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return data, temp_file