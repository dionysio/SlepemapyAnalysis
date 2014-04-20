# -*- coding: utf-8 -*-

from libs.map import Map
from libs.input_output import get_arguments

from os import path,makedirs


(items, frame, prior, codes, working_directory) = get_arguments(path.dirname(path.realpath(__file__)), False)

m = Map(working_directory, frame, prior=prior, codes=codes)

directory = working_directory+'/maps/global/'
if not path.exists(directory):
    makedirs(directory)

print 'Generating global maps'
m.average_knowledge(path=directory)
m.success(path=directory)
m.number_of_answers(path=directory)
m.response_time(path=directory)