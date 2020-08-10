from pm4py.objects.log.log import EventLog

from proved.artifacts.behavior_graph import behavior_graph


class UncertainLog(EventLog):

    def __init__(self, log=None):
        self.__variants = dict()
        self.__behavior_graphs_map = dict()
        if log is not None:
            EventLog.__init__(self, log)
            self.create_behavior_graphs()
        else:
            EventLog.__init__(self)

    def __get_variants(self):
        return self.__variants

    def __get_behavior_graphs_map(self):
        return self.__behavior_graphs_map

    # TODO: method that given an uncertain log creates the behavior graphs and a mapping between uncertain traces and behavior graphs
    def create_behavior_graphs(self):
        # TODO: this still suffers from the bug of the behavior graph creation: timestamps must not coincide
        for trace in self:
            nodes_tuple = behavior_graph.create_nodes_tuples(trace)
            if nodes_tuple not in self.behavior_graphs_map:
                self.behavior_graphs_map[nodes_tuple] = (behavior_graph.BehaviorGraph(trace), [])
            self.behavior_graphs_map[nodes_tuple][1].append(trace)
        if self.behavior_graphs_map is not {}:
            variant_list = [(len(traces_list), nodes_list) for nodes_list, (_, traces_list) in self.behavior_graphs_map.items()]
            variant_list.sort(reverse=True)
            self.__variants = {i: (variant_length, nodes_tuple) for i, (variant_length, nodes_tuple) in enumerate(variant_list)}

    def get_behavior_graph(self, trace):
        return self.behavior_graphs_map[behavior_graph.create_nodes_tuples(trace)]

    variants = property(__get_variants)
    behavior_graphs_map = property(__get_behavior_graphs_map)

import pm4py.objects.log.log as log_instance
from pm4py.objects.petri import semantics
from copy import copy
from random import choice
import datetime
from pm4py.objects.log.util import xes as xes_key
def apply_playout(net, initial_marking, final_marking, no_traces=100, max_trace_length=100, trace_key=xes_key.DEFAULT_TRACEID_KEY, activity_key=xes_key.DEFAULT_NAME_KEY, timestamp_key=xes_key.DEFAULT_TIMESTAMP_KEY):
    """
    Do the playout of a Petrinet generating a log

    Parameters
    ----------
    net
        Petri net to play-out
    initial_marking
        Initial marking of the Petri net
    final_marking
        Final marking of the Petri net
    no_traces
        Number of traces to generate
    max_trace_length
        Maximum number of events per trace (do break)
    """
    # assigns to each event an increased timestamp from 1970
    curr_timestamp = 10000000
    log = log_instance.EventLog()
    for i in range(no_traces):
        trace = log_instance.Trace()
        trace.attributes[trace_key] = str(i)
        marking = copy(initial_marking)
        while len(trace) < max_trace_length:
            if not semantics.enabled_transitions(net, marking):  # supports nets with possible deadlocks
                break
            all_enabled_trans = semantics.enabled_transitions(net, marking)
            if marking == final_marking:
                trans = choice(tuple(all_enabled_trans.union({None})))
            else:
                trans = choice(tuple(all_enabled_trans))
            if trans is None:
                break
            if trans.label is not None:
                event = log_instance.Event()
                event[activity_key] = trans.label
                event[timestamp_key] = datetime.datetime.fromtimestamp(curr_timestamp)
                trace.append(event)
                # increases by 1 second
                curr_timestamp += 1
            marking = semantics.execute(trans, net, marking)
        log.append(trace)
    return log

from lxml import etree
import time
from pm4py.objects import petri
from pm4py.objects.petri.common import final_marking
from pm4py.objects.random_variables.random_variable import RandomVariable
def import_net(input_file_path, return_stochastic_information=False, parameters=None):
    """
    Import a Petri net from a PNML file

    Parameters
    ----------
    input_file_path
        Input file path
    return_stochastic_information
        Enables return of stochastic information if found in the PNML
    parameters
        Other parameters of the algorithm
    """
    if parameters is None:
        parameters = {}

    tree = etree.parse(input_file_path)
    root = tree.getroot()

    net = petri.petrinet.PetriNet('imported_' + str(time.time()))
    marking = petri.petrinet.Marking()
    fmarking = petri.petrinet.Marking()

    nett = None
    page = None
    finalmarkings = None

    stochastic_information = {}

    for child in root:
        nett = child

    places_dict = {}
    trans_dict = {}

    if nett is not None:
        for child in nett:
            if "page" in child.tag:
                page = child
            if "finalmarkings" in child.tag:
                finalmarkings = child

    if page is None:
        page = nett

    if page is not None:
        for child in page:
            if "place" in child.tag:
                place_id = child.get("id")
                place_name = place_id
                number = 0
                for child2 in child:
                    if "name" in child2.tag:
                        for child3 in child2:
                            if child3.text:
                                place_name = child3.text
                    if "initialMarking" in child2.tag:
                        for child3 in child2:
                            if "text" in child3.tag:
                                number = int(child3.text)
                places_dict[place_id] = petri.petrinet.PetriNet.Place(place_id)
                net.places.add(places_dict[place_id])
                if number > 0:
                    marking[places_dict[place_id]] = number
                del place_name

    if page is not None:
        for child in page:
            if "transition" in child.tag:
                trans_name = child.get("id")
                trans_label = trans_name
                trans_visible = True

                random_variable = None

                for child2 in child:
                    if "name" in child2.tag:
                        for child3 in child2:
                            if child3.text:
                                if trans_label == trans_name:
                                    trans_label = child3.text
                    if "toolspecific" in child2.tag:
                        tool = child2.get("tool")
                        if "ProM" in tool:
                            activity = child2.get("activity")
                            if "invisible" in activity:
                                trans_visible = False
                        elif "StochasticPetriNet" in tool:
                            distribution_type = None
                            distribution_parameters = None
                            priority = None
                            weight = None

                            for child3 in child2:
                                key = child3.get("key")
                                value = child3.text

                                if key == "distributionType":
                                    distribution_type = value
                                elif key == "distributionParameters":
                                    distribution_parameters = value
                                elif key == "priority":
                                    priority = int(value)
                                elif key == "weight":
                                    weight = float(value)

                            if return_stochastic_information:
                                random_variable = RandomVariable()
                                random_variable.read_from_string(distribution_type, distribution_parameters)
                                random_variable.set_priority(priority)
                                random_variable.set_weight(weight)
                if not trans_visible:
                    trans_label = None
                #if "INVISIBLE" in trans_label:
                #    trans_label = None

                trans_dict[trans_name] = petri.petrinet.PetriNet.Transition(trans_name, trans_label)
                net.transitions.add(trans_dict[trans_name])

                if random_variable is not None:
                    stochastic_information[trans_dict[trans_name]] = random_variable

    if page is not None:
        for child in page:
            if "arc" in child.tag:
                arc_source = child.get("source")
                arc_target = child.get("target")

                if arc_source in places_dict and arc_target in trans_dict:
                    petri.utils.add_arc_from_to(places_dict[arc_source], trans_dict[arc_target], net)
                elif arc_target in places_dict and arc_source in trans_dict:
                    petri.utils.add_arc_from_to(trans_dict[arc_source], places_dict[arc_target], net)

    if finalmarkings is not None:
        for child in finalmarkings:
            for child2 in child:
                place_id = child2.get("idref")
                for child3 in child2:
                    if "text" in child3.tag:
                        number = int(child3.text)
                        if number > 0:
                            fmarking[places_dict[place_id]] = number

    # generate the final marking in the case has not been found
    if len(fmarking) == 0:
        fmarking = final_marking.discover_final_marking(net)

    if return_stochastic_information and len(list(stochastic_information.keys())) > 0:
        return net, marking, fmarking, stochastic_information

    return net, marking, fmarking


if __name__ == '__main__':
    import pprint
    import glob
    import os
    from copy import deepcopy
    from proved.simulation.bewilderer.add_activities import add_uncertain_activities_to_log
    from proved.simulation.bewilderer.add_timestamps import add_uncertain_timestamp_to_log
    from proved.artifacts.behavior_net import behavior_net as behavior_net_builder
    from pm4py.visualization.petrinet import factory as pt_vis

    net_file = glob.glob('net10_1.pnml')
    print(net_file)
    net, im, fm = import_net(net_file[0])
    log = apply_playout(net, im, fm, no_traces=2)

    # TRACE (NO UNCERTAINTY)
    print('TRACE (NO UNCERTAINTY)')
    for trace in log:
        print('Trace:')
        for event in trace:
            pprint.pprint(event)
    p_u = .5


    # TRACE (UNCERTAINTY ON TIMESTAMPS)
    add_uncertain_timestamp_to_log(p_u, log)
    trace_u_time = deepcopy(log[0])
    log.append(deepcopy(trace_u_time))
    trace_2 = deepcopy(trace_u_time)
    from datetime import timedelta
    for event in trace_2:
        if 'u:timestamp:min' in event:
            event['u:time:timestamp_min'] += timedelta(milliseconds=30)
            event['u:time:timestamp_max'] += timedelta(milliseconds=30)
        else:
            event['time:timestamp'] += timedelta(milliseconds=30)
    log.append(trace_2)
    trace_3 = deepcopy(trace_2)
    for event in trace_3:
        if 'u:timestamp:min' in event:
            event['u:time:timestamp_min'] += timedelta(milliseconds=10)
            event['u:time:timestamp_max'] += timedelta(milliseconds=10)
        else:
            event['time:timestamp'] += timedelta(milliseconds=10)
    log.append(trace_3)
    print('TRACE (UNCERTAINTY ON TIMESTAMPS)')
    for trace in log:
        print('Trace:')
        for event in trace:
            pprint.pprint(event)
    log_object = UncertainLog(log)
    print('Variants:')
    for variant in log_object.variants:
        print(variant)
    for key, value in log_object.behavior_graphs_map.items():
        print(key)
        print(value[1])
        print(len(value[1]))
