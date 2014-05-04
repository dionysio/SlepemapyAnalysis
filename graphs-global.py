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
g.success_over_time(directory=directory)
g.response_time(directory=directory)
g.difficulty_histogram(directory = directory)
g.prior_skill_histogram(directory=directory)
g.difficulty_response_time(directory=directory)
g.skill(directory=directory)
g.success_over_session(directory=directory)
g.lengths_of_sessions(directory=directory)
g.number_of_answers_over_session(directory=directory)
g.number_of_answers_over_time(directory=directory)
g.number_of_users_over_session(directory=directory)
g.number_of_users_over_time(directory=directory)
g.weekday_activity(directory=directory)
g.hourly_activity(directory=directory)