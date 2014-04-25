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
    g.success_over_session(path=directory)
    g.success_over_time(path=directory,frequency='D')
    g.skill(path=directory)
    g.response_time(path=directory)
    g.lengths_of_sessions(path=directory)
    g.number_of_answers_over_time(path=directory, frequency='D')
    g.number_of_answers_over_session(path=directory)
    g.weekday_activity(path=directory)
    g.hourly_activity(path=directory)
