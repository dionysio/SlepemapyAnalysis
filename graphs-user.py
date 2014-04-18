# -*- coding: utf-8 -*-

from libs.graph import Graph 
from libs.inputoutput import arguments

from os import path,makedirs


(items, frame, prior, codes, working_directory) = arguments(path.dirname(path.realpath(__file__)), True)

for item in items:
    g = Graph(working_directory, frame, user=int(item), prior = prior)

<<<<<<< HEAD
=======
if args.file is None:
    working_directory = path.dirname(path.realpath(__file__))
else:
    working_directory = args.file
frame = inputoutput.load_geo_csv(working_directory+"/geography.answer.csv")
diff = inputoutput.load_difficulties(path=working_directory+'/difficulties.yaml')

for item in args.items:
    g = Graph(path, difficulties = diff, df = frame, user=int(item))

>>>>>>> 101963544307ed1c158181f775020dd1a28a530e
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
