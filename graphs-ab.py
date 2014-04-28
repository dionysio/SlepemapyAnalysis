# -*- coding: utf-8 -*-

from libs.graph import Graph 
from libs.input_output import get_arguments, load_ab_csv
from libs.elo_rating_system import estimate_prior_knowledge

from os import path,makedirs

def generate_graphs(g, directory):
    g.success_over_time(directory=directory, frequency = 'W')
    g.number_of_answers_over_time(directory=directory, frequency='W')
    g.prior_skill_histogram(directory=directory)
    g.skill(directory=directory)
    g.success_over_session(directory=directory)
    g.lengths_of_sessions(directory=directory)
    g.number_of_answers_over_session(directory=directory)
    g.number_of_users(directory=directory)
    g.weekday_activity(directory=directory)
    g.hourly_activity(directory=directory)


(items, frame, prior, codes, working_directory) = get_arguments(path.dirname(path.realpath(__file__)), False)
ab = load_ab_csv(working_directory+'/data/geography.answer.ab_testing.csv')

a = Graph(working_directory, ab[0], codes=codes)

ab_prior = a.frame.groupby('user')
ab_prior = ab_prior.apply(lambda x: estimate_prior_knowledge(x, prior[0]))
a.set_prior((prior[0],ab_prior.to_dict()))

b = Graph(working_directory, ab[1], codes=codes)
ab_prior = b.frame.groupby('user')
ab_prior = ab_prior.apply(lambda x: estimate_prior_knowledge(x, prior[0]))
b.set_prior((prior[0],ab_prior.to_dict()))

directory = working_directory+'/graphs/ab/'
if not path.exists(directory):
    makedirs(directory)
if not path.exists(directory+'a/'):
    makedirs(directory+'a/')
if not path.exists(directory+'b/'):
    makedirs(directory+'b/')

print 'Generating graphs for the first group'
generate_graphs(a, directory+'a/')
print 'Generating graphs for the second group'
generate_graphs(b, directory+'b/')
