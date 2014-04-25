# -*- coding: utf-8 -*-

from elo_rating_system import estimate_current_knowledge, _logis
from pandas import Series


def average_knowledge(difficulties):
    """Returns predicted probabilities of success for average user.
    """

    result = []
    for item in difficulties.iteritems():
        result += [_logis(-item[1][0])]
    return Series(result,index=difficulties.keys())


def knowledge(frame,difficulties):
    """User-specific probabilities of success.
    """
    
    skills = estimate_current_knowledge(frame,difficulties)
    result = []
    for item in skills.iteritems():
        result += [_logis(item[1][0] - difficulties[item[0]][0])]
    return Series(result,index=skills.keys())


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


def response_time(frame, right=None):
    """Returns dataframe of mean response times per country.

    :param right: filter only right/wrong/both answers
    :type right: True/False/None -- default is None
    """

    answers = frame[frame.response_time<60000]
    if right:
        answers = answers[answers.place_asked==answers.place_answered]
    elif right == False:
        answers = answers[answers.place_asked!=answers.place_answered]
    answers = answers.groupby('place_asked')
    return answers['response_time'].mean()


def mistaken_countries(frame, threshold=None):
    """Returns counts of countries that are most mistaken for this country.

    :param threshold: only return top counts -- default is None (which means return all)
    """

    wrong_answers = frame[frame.place_asked!=frame.place_answered]
    wrong_answers = wrong_answers['place_answered'].value_counts()
    return wrong_answers[:threshold]


def success(frame):
    """Returns mean_success_rate for each country.
    """

    groups = frame.groupby('place_asked')
    groups = groups.apply(lambda x: len(x[x.place_asked==x.place_answered])/float(len(x))*100)
    return groups.dropna()


def answer_portions(frame, threshold=None):
    mistaken = mistaken_countries(frame)
    mistaken = mistaken.append(Series({frame.place_asked[0]: len(frame[frame.place_asked==frame.place_answered])}))
    mistaken = mistaken/float(mistaken.sum())
    if threshold is None:
        return mistaken
    else:
        return (mistaken[mistaken>=threshold]*100).append(Series({0:mistaken[mistaken<threshold].sum()*100}))   