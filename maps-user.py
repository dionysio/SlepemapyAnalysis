# -*- coding: utf-8 -*-

from libs.map import Map
from libs.input_output import get_arguments

from os import path,makedirs


(items, frame, prior, codes, working_directory) = get_arguments(path.dirname(path.realpath(__file__)),True)

for item in items:
    m = Map(working_directory,frame, user=int(item), codes = codes, prior = prior)

    directory = working_directory+'/maps/user/'+item+'/'
    if not path.exists(directory):
        makedirs(directory)

    print 'Generating maps for user',item
    m.knowledge(directory=directory)
    m.success(directory=directory)
    m.number_of_answers(directory=directory)
    m.response_time(directory=directory)
