# -*- coding: utf-8 -*-

from libs.graph import Graph 
from libs.inputoutput import arguments

from os import path,makedirs


(items, frame, prior, codes, working_directory) = arguments(path.dirname(path.realpath(__file__)), False)

g = Graph(working_directory, frame, prior = prior, codes=codes)

directory = working_directory+'/graphs/global/'
if not path.exists(directory):
    makedirs(directory)

print 'Generating global graphs'
g.success(path=directory,threshold=15)
g.number_of_users(path=directory)
g.mean_number_of_answers(path=directory)
g.mean_success_rate(path=directory)
g.lengths_of_sessions(path=directory,threshold=15)
g.number_of_answers(path=directory,threshold=15)
g.weekday_activity(path=directory)
g.hourly_activity(path=directory)