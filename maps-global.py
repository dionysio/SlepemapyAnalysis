# -*- coding: utf-8 -*-

from libs.map import WorldMap
from libs.input_output import get_arguments

from os import path,makedirs


(items, frame, prior, codes, working_directory) = get_arguments(path.dirname(path.realpath(__file__)), False)

m = WorldMap(working_directory, frame, prior=prior, codes=codes)

directory = working_directory+'/maps/global/'
if not path.exists(directory):
    makedirs(directory)

print 'Generating global maps'

m.prior_knowledge(directory=directory)
m.success(directory=directory)
m.number_of_answers(directory=directory)
m.response_time(directory=directory)
m.average_current_knowledge(directory=directory)