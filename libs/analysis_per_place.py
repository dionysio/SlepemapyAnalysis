# -*- coding: utf-8 -*-

from elo_rating_system import estimate_current_knowledge
from common import logis, first_questions
from pandas import Series, DataFrame


def prior_knowledge(difficulties):
    """Returns predicted probabilities of success for avg user.
    """

    result = [logis(-item) for item in difficulties.itervalues()]
    return Series(result,index=difficulties.keys())


def average_current_knowledge(frame,difficulties):
    """Predicted probabilities of success.
    """

    skills = first_questions(frame.groupby(['session_number','user']))
    skills = skills.groupby('user').apply(lambda x: DataFrame.from_dict(estimate_current_knowledge(x,difficulties),orient='index'))
    skills = skills.reset_index()
    skills = skills.groupby('level_1').apply(lambda x: x[0].mean())
    skills = skills.reset_index()
    index = skills['level_1']
    skills = Series(skills.apply(lambda x: logis(x[0] - difficulties[x["level_1"]][0]),axis=1))
    skills.index = index
    return skills.dropna()


def number_of_answers(frame,right=None):
    """Returns numbers of answers per country.

    :param right: filter only right/wrong/both answers
    :type right: True/False/None -- default is None
    """

    answers = frame
    if right:
        answers = frame[frame.place_asked==frame.place_answered]
    elif right==False:
        answers = frame[frame.place_asked!=frame.place_answered]
    return answers['place_asked'].value_counts()


def response_time(frame, right=None, threshold=60000):
    """Returns dataframe of mean response times per country.

    :param right: filter only right/wrong/both answers
    :type right: True/False/None -- default is None
    """

    answers = frame[frame.response_time<threshold]
    if right:
        answers = answers[answers.place_asked==answers.place_answered]
    elif right == False:
        answers = answers[answers.place_asked!=answers.place_answered]
    answers = answers.groupby('place_asked')
    return answers['response_time'].mean()


def mistaken_places(frame, threshold=None):
    """Returns counts of countries that are most mistaken for this country.

    :param threshold: only return top counts -- default is None (which means return all)
    """

    wrong_answers = first_questions(frame.groupby(['user','session_number']))
    first_len = len(wrong_answers)
    wrong_answers = wrong_answers[wrong_answers.place_asked!=wrong_answers.place_answered]
    wrong_answers = wrong_answers['place_answered'].value_counts()
    wrong_answers = wrong_answers[:threshold]
    wrong_answers.index.name = 'code'
    return (wrong_answers, first_len)


def success(frame):
    """Returns mean success rate for each country.
    """

    groups = first_questions(frame.groupby(['user','session_number']))
    groups = groups.groupby('place_asked')
    groups = groups.apply(lambda x: len(x[x.place_asked==x.place_answered])/float(len(x)))
    return groups.dropna()