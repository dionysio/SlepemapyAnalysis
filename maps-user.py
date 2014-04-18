# -*- coding: utf-8 -*-

from libs.map import Map
from libs.inputoutput import arguments

from os import path,makedirs


(items, frame, prior, codes, working_directory) = arguments(path.dirname(path.realpath(__file__)),True)

for item in items:
    m = Map(working_directory,frame, user=int(item), codes = codes, prior = prior)

    directory = working_directory+'/maps/user/'+item+'/'
    if not path.exists(directory):
        makedirs(directory)

    print 'Generating maps for user',item
    m.skill(path=directory)
    m.success(path=directory)
    m.number_of_answers(path=directory)
    m.response_time(path=directory)
