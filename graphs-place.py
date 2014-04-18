# -*- coding: utf-8 -*-

from libs.graph import Graph 
from libs.inputoutput import arguments

from os import path,makedirs


(items, frame, prior, codes, working_directory) = arguments(path.dirname(path.realpath(__file__)), True)

for item in items:
    g = Graph(working_directory, frame, place_asked=int(item), prior = prior, codes=codes)

<<<<<<< HEAD
=======
if args.file is None:
    working_directory = path.dirname(path.realpath(__file__))
else:
    working_directory = args.file
frame = inputoutput.load_geo_csv(working_directory+"/geography.answer.csv")
diff = inputoutput.load_difficulties(path=working_directory+'/difficulties.yaml')

for item in args.items:
    g = Graph(path, difficulties = diff, df = frame, place_asked=int(item))

>>>>>>> 101963544307ed1c158181f775020dd1a28a530e
    directory = working_directory+'/graphs/place/'+item+'/'
    if not path.exists(directory):
        makedirs(directory)

    print 'Generating graphs for place',item
    g.success(path=directory)
    g.skill(path=directory)
<<<<<<< HEAD
    g.answers_percentages(path=directory)
=======
>>>>>>> 101963544307ed1c158181f775020dd1a28a530e
