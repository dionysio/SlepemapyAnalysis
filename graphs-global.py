# -*- coding: utf-8 -*-

from libs.graph import Graph 
from libs.input_output import get_arguments

from os import path,makedirs


(items, frame, prior, codes, working_directory) = get_arguments(path.dirname(path.realpath(__file__)), False)

g = Graph(working_directory, frame, prior = prior, codes=codes)

directory = working_directory+'/graphs/global/'
if not path.exists(directory):
    makedirs(directory)

print 'Generating global graphs'
g.success_over_time(path=directory)
# g.lengths_of_sessions(path=directory,threshold=15) #slow as hell on global
g.number_of_answers_over_session(path=directory,threshold=15)
g.number_of_answers_over_time(path=directory)
g.number_of_users(path=directory)
g.weekday_activity(path=directory)
g.hourly_activity(path=directory)