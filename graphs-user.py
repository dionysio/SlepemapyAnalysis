# -*- coding: utf-8 -*-

from libs.graph import Graph 
from libs.inputoutput import arguments

from os import path,makedirs


(items, frame, prior, codes, working_directory) = arguments(path.dirname(path.realpath(__file__)), True)

for item in items:
    g = Graph(working_directory, frame, user=int(item), prior = prior)

    directory = working_directory+'/graphs/user/'+item+'/'
    if not path.exists(directory):
        makedirs(directory)

    print 'Generating graphs for user',item
    g.success(path=directory)
    g.skill(path=directory)
    g.lengths_of_sessions(path=directory)
    g.number_of_answers(path=directory)
    g.weekday_activity(path=directory)
    g.hourly_activity(path=directory)