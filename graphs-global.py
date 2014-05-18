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
g.difficulty_histogram(directory=directory)
g.prior_skill_histogram(directory=directory)
g.difficulty_response_time(directory=directory)
g.lengths_of_sessions(directory=directory)
g.number_of_answers_per_session(directory=directory)
g.number_of_answers_over_time(directory=directory)
g.number_of_users_per_session(directory=directory)
g.number_of_users_over_time(directory=directory)
g.response_time_start_end(directory=directory)

g.weekday_activity(directory=directory)
g.hourly_activity(directory=directory)
g.separated_success(directory=directory)
g.average_success(directory=directory)
g.separated_skill(directory=directory)
g.average_skill(directory=directory)
g.success_over_time(directory=directory)
