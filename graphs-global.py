# -*- coding: utf-8 -*-

from libs.graph import Graph 
from libs.inputoutput import arguments

from os import path,makedirs


(items, frame, prior, codes, working_directory) = arguments(path.dirname(path.realpath(__file__)), False)

g = Graph(working_directory, frame, prior = prior)

<<<<<<< HEAD
=======
if args.file is None:
    working_directory = path.dirname(path.realpath(__file__))
else:
    working_directory = args.file
frame = inputoutput.load_geo_csv(working_directory+"/geography.answer.csv")
diff = inputoutput.load_difficulties(path=working_directory+'/difficulties.yaml')

g = Graph(path, difficulties = diff, df = frame)

>>>>>>> 101963544307ed1c158181f775020dd1a28a530e
directory = working_directory+'/graphs/global/'
if not path.exists(directory):
    makedirs(directory)

print 'Generating global graphs'
<<<<<<< HEAD
g.success(path=directory,threshold=15)
g.skill(path=directory,threshold=15)
g.lengths_of_sessions(path=directory,threshold=15)
g.number_of_answers(path=directory,threshold=15)
g.weekday_activity(path=directory)
g.hourly_activity(path=directory)
=======
g.success(path=directory)
g.skill(path=directory)
>>>>>>> 101963544307ed1c158181f775020dd1a28a530e
