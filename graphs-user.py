# -*- coding: utf-8 -*-

from libs.graph import Graph 
from libs.input_output import get_arguments

from os import path,makedirs


(items, frame, prior, codes, working_directory) = get_arguments(path.dirname(path.realpath(__file__)), True)

for item in items:
    g = Graph(working_directory, frame, user=int(item), prior = prior, codes=codes)

    directory = working_directory+'/graphs/user/'+item+'/'
    if not path.exists(directory):
        makedirs(directory)

    print 'Generating graphs for user',item
    g.success_over_session(directory=directory)
    g.skill(directory=directory)
    g.lengths_of_sessions(directory=directory)
    g.number_of_answers_over_session(directory=directory)
    g.weekday_activity(directory=directory)
    g.hourly_activity(directory=directory)
