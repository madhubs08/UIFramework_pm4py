from django.shortcuts import render
from pm4py.objects.log.importer.xes import factory as xes_importer_factory
from pm4py.util import xes_constants
from pm4py.visualization.petrinet import factory as pn_vis_factory
from django.conf import settings
import os
import glob
from pathlib import Path

from io import BytesIO
import base64

from proved.artifacts.uncertain_log import uncertain_log
from proved import xes_keys
from proved.artifacts.behavior_net import behavior_net

# Create your views here.


def uncertainty_home(request):
    event_logs_path = os.path.join(settings.MEDIA_ROOT, "event_logs")
    event_log = os.path.join(event_logs_path, settings.EVENT_LOG_NAME)
    log = xes_importer_factory.apply(event_log)
    u_log = uncertain_log.UncertainLog(log)
    variants_table = tuple((id_var, size) for id_var, (size, _) in u_log.variants.items())
    log_len = 0
    for trace in log:
        log_len += len(trace)
    avg_trace_len = log_len / len(log)
    activities_map = dict()
    start_activities_map = dict()
    end_activities_map = dict()
    for _, (_, nodes_lists) in u_log.variants.items():
        for ((_, activities), _) in nodes_lists:
            for activity in activities:
                activities_map[activity] = [0, 0]
                start_activities_map[activity] = [0, 0]
                end_activities_map[activity] = [0, 0]
    for trace in log:
        for i, event in enumerate(trace):
            if xes_keys.DEFAULT_U_NAME_KEY in event:
                for activity in event[xes_keys.DEFAULT_U_NAME_KEY]['children']:
                    activities_map[activity][0] += 1
                    if i == 0:
                        start_activities_map[activity][0] += 1
                    if i == len(trace) - 1:
                        end_activities_map[activity][0] += 1
            else:
                activities_map[event[xes_constants.DEFAULT_NAME_KEY]][0] += 1
                activities_map[event[xes_constants.DEFAULT_NAME_KEY]][1] += 1
                if i == 0:
                    start_activities_map[event[xes_constants.DEFAULT_NAME_KEY]][0] += 1
                    start_activities_map[event[xes_constants.DEFAULT_NAME_KEY]][1] += 1
                if i == len(trace) - 1:
                    end_activities_map[event[xes_constants.DEFAULT_NAME_KEY]][0] += 1
                    end_activities_map[event[xes_constants.DEFAULT_NAME_KEY]][1] += 1
    activities_table_abs = sorted([(freq_min, freq_max, activity) for activity, [freq_min, freq_max] in activities_map.items()], reverse=True)
    start_activities_table_abs = sorted([(freq_min, freq_max, activity) for activity, [freq_min, freq_max] in start_activities_map.items()], reverse=True)
    end_activities_table_abs = sorted([(freq_min, freq_max, activity) for activity, [freq_min, freq_max] in end_activities_map.items()], reverse=True)
    activities_table = [(freq_min, freq_max, round(freq_min/log_len*100, 2), round(freq_max/log_len*100, 2), activity) for freq_min, freq_max, activity in activities_table_abs]
    start_activities_table = [(freq_min, freq_max, round(freq_min/log_len*100, 2), round(freq_max/log_len*100, 2), activity) for freq_min, freq_max, activity in start_activities_table_abs]
    end_activities_table = [(freq_min, freq_max, round(freq_min/log_len*100, 2), round(freq_max/log_len*100, 2), activity) for freq_min, freq_max, activity in end_activities_table_abs]
    request.session['uncertainty_summary'] = {'variants': variants_table, 'log_len': log_len, 'avg_trace_len': avg_trace_len, 'activities_table': activities_table, 'start_activities_table': start_activities_table, 'end_activities_table': end_activities_table}
    return render(request, 'uncertainty.html', {'variants': variants_table, 'log': log, 'log_len': log_len, 'avg_trace_len': avg_trace_len, 'activities_table': activities_table, 'start_activities_table': start_activities_table, 'end_activities_table': end_activities_table})
    # return render(request, 'uncertainty.html', request.session['uncertainty_summary'])


def uncertainty_variant(request, variant):
    event_logs_path = os.path.join(settings.MEDIA_ROOT, "event_logs")
    event_log = os.path.join(event_logs_path, settings.EVENT_LOG_NAME)
    log_name = settings.EVENT_LOG_NAME.split('.')[0]
    log = xes_importer_factory.apply(event_log)
    u_log = uncertain_log.UncertainLog(log)
    variants_table = request.session['uncertainty_summary']['variants']
    bg, traces_list = u_log.behavior_graphs_map[u_log.variants[variant][1]]
    traces_table = ((i, len(trace)) for i, trace in enumerate(traces_list))
    # Path(os.path.join(settings.STATIC_URL, 'uncertainty', 'variant', 'img_bn', log_name)).mkdir(parents=True, exist_ok=True)
    if not glob.glob(os.path.join(settings.STATIC_URL, 'uncertainty', 'variant', 'img_bn', log_name, 'bn' + str(variant) + '.png')):
        bn = behavior_net.BehaviorNet(bg)
        gviz = pn_vis_factory.apply(bn, bn.initial_marking, bn.final_marking, parameters={'format': 'png'})
        # pn_vis_factory.save(gviz, os.path.join('static', 'bn' + str(variant) + '.png'))
        pn_vis_factory.save(gviz, os.path.join('static', 'uncertainty', 'variant', 'img_bn', log_name, 'bn' + str(variant) + '.png'))
    image_bn = os.path.join('uncertainty', 'variant', 'img_bn', log_name, 'bn' + str(variant) + '.png')
    return render(request, 'uncertainty_variant.html', {'variant': variant, 'variants': variants_table, 'traces': traces_table, 'log_name': log_name, 'image_bn': image_bn})


def uncertainty_trace(request, trace):
    pass


