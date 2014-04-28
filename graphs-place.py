# -*- coding: utf-8 -*-

from libs.graph import Graph 
from libs.input_output import get_arguments

from os import path,makedirs


(items, frame, prior, codes, working_directory) = get_arguments(path.dirname(path.realpath(__file__)), True)

for item in items:
    g = Graph(working_directory, frame, place_asked=int(item), prior = prior, codes=codes)

    directory = working_directory+'/graphs/place/'+item+'/'
    if not path.exists(directory):
        makedirs(directory)

    print 'Generating graphs for place',item
    g.success_over_time(directory=directory)
    g.answer_portions(directory=directory)