# -*- coding: utf-8 -*-

from libs.map import Map
from libs.input_output import get_arguments

from os import path,makedirs


(items, frame, prior, codes, working_directory) = get_arguments(path.dirname(path.realpath(__file__)),True)

for item in items:
    m = Map(working_directory, frame, place_asked=int(item),codes=codes)


    directory = working_directory+'/maps/place/'+item+'/'
    if not path.exists(directory):
        makedirs(directory)

    print 'Generating maps for place',item
    m.mistaken_countries(path=directory)