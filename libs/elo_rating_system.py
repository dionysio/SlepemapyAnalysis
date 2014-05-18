# -*- coding: utf-8 -*-

from common import defaultdict_factory, first_questions, logis

from collections import defaultdict



def _elo(answer, prior_skill, user_number_of_answers, difficulty, place_number_of_answers):
    """Modified implementation of elo from https://github.com/proso/geography/blob/master/main/geography/models/prior.py

    ELO model that returns updated values of country's difficulty and user's skill

    :param answer: answer has columns place_asked,place_answered,number_of_options
    :param prior_skill: score of a user
    :param user_number_of_answers: number of answers user has for this country
    :param difficulty: score of a country
    :param place_number_of_answers: number of answers country has
    """

    if answer['number_of_options']:
        guess = 1.0/answer['number_of_options']
    else:
        guess = 0
    prediction = guess + (1-guess) * logis(prior_skill-difficulty)
    result = answer['place_asked'] == answer['place_answered']

    k_func = lambda x: 1.0/(1+0.05*x)
    k1 = k_func(user_number_of_answers)
    k2 = k_func(place_number_of_answers)

    return  (prior_skill + k1 * (result - prediction),
            difficulty- k2 * (result - prediction))


def estimate_prior_knowledge(frame, difficulties):
    """Estimates prior_knowledge of one user
    """

    first = first_questions(frame.groupby('session_number'))
    prior_skill= (0,0)

    for index, answer in first.iterrows():
        update = _elo(answer,
                    prior_skill[0], prior_skill[1],
                    difficulties[answer.place_asked][0], difficulties[answer.place_asked][1])

        prior_skill = (update[0], prior_skill[1]+1)

    return prior_skill


def calculate_difficulties(frame):
    """Calculates difficulty for every country
    """

    first = first_questions(frame.groupby('user'))
    
    difficulties = defaultdict(defaultdict_factory)
    prior_skill  = defaultdict(defaultdict_factory)

    for index, answer in first.iterrows():
        update = _elo(answer,
                    prior_skill[answer.user][0], prior_skill[answer.user][1],
                    difficulties[answer.place_asked][0], difficulties[answer.place_asked][1])

        prior_skill[answer.user] = (update[0], prior_skill[answer.user][1]+1)
        difficulties[answer.place_asked] = (update[1], difficulties[answer.place_asked][1]+1)

    return (difficulties, prior_skill)


def estimate_current_knowledge(frame, difficulties):
    """
    """

    prior_skill = estimate_prior_knowledge(frame,difficulties)
    current_skill  = defaultdict(lambda : (prior_skill[0],0))

    def func(x):
        current_skill[x.place_asked] = (_elo(x, 
            current_skill[x.place_asked][0], current_skill[x.place_asked][1],
            difficulties[x.place_asked][0], difficulties[x.place_asked][1])[0],
            current_skill[x.place_asked][1]+1)

    frame.apply(func, axis=1)
    return current_skill