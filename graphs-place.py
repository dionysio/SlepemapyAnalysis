# -*- coding: utf-8 -*-

from libs.graph import Graph 
from libs.inputoutput import arguments

from os import path,makedirs


(items, frame, prior, codes, working_directory) = arguments(path.dirname(path.realpath(__file__)), True)

for item in items:
    g = Graph(working_directory, frame, place_asked=int(item), prior = prior, codes=codes)


for item in args.items:
    g = Graph(path, difficulties = diff, df = frame, place_asked=int(item))

    directory = working_directory+'/graphs/place/'+item+'/'
    if not path.exists(directory):
        makedirs(directory)

    print 'Generating graphs for place',item
    g.success(path=directory)
    g.skill(path=directory)