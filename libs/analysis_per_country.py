# -*- coding: utf-8 -*-

from elo_rating_system import estimate_current_knowledge
from common import logis
from pandas import Series, DataFrame


def prior_knowledge(difficulties):
    """Returns predicted probabilities of success for new user.
    """

    result = []
    for item in difficulties.iteritems():
        result += [logis(-item[1][0])]
    return Series(result,index=difficulties.keys())


def average_knowledge(frame,difficulties):
    """User-specific predicted probabilities of success.
    """
    
    skills = estimate_current_knowledge(frame,difficulties)
    result = []
    for item in skills.iteritems():
        result += [logis(item[1][0] - difficulties[item[0]][0])]
    return Series(result,index=skills.keys())


def average_knowledgeNEW(frame,difficulties):
    """User-specific predicted probabilities of success.
    """
    
    skills = frame.groupby('user').apply(lambda x: DataFrame.from_dict(estimate_current_knowledge(x,difficulties),orient='index'))
    skills = skills.reset_index()
    skills = skills.groupby('level_1').apply(lambda x: x[0].mean())
    skills = skills.reset_index()
    ind = skills.index
    skills = skills.apply(lambda x: logis(x[0] - difficulties[x["level_1"]][0]),axis=1)
    skills.index = ind
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


def mistaken_countries(frame, threshold=None):
    """Returns counts of countries that are most mistaken for this country.

    :param threshold: only return top counts -- default is None (which means return all)
    """

    wrong_answers = frame[frame.place_asked!=frame.place_answered]
    wrong_answers = wrong_answers['place_answered'].value_counts()
    return wrong_answers[:threshold]


def success(frame):
    """Returns mean success rate for each country.
    """

    groups = frame.groupby('place_asked')
    groups = groups.apply(lambda x: len(x[x.place_asked==x.place_answered])/float(len(x))*100)
    return groups.dropna()


def answer_portions(frame, threshold=None):
    """Returns portions of answers for specific country.
    
    :param threshold: limit of values to include as separate slice -- default is None
    """

    mistaken = mistaken_countries(frame)
    mistaken = mistaken.append(Series({frame.place_asked[0]: len(frame[frame.place_asked==frame.place_answered])}))
    mistaken = mistaken/float(mistaken.sum())
    if threshold is None:
        return mistaken
    else:
        return (mistaken[mistaken>=threshold]*100).append(Series({0:mistaken[mistaken<threshold].sum()*100}))


def difficulty_response_time(frame, difficulty):
    data = DataFrame(response_time(frame,right=True))
    data.columns = ['correct']
    data['incorrect'] = response_time(frame,right=False)
    d = Series(difficulty)
    d = d.apply(lambda x: logis(x[0]))
    d.name = 'difficulty'
    data = data.join(d)    
    data = data.dropna()
    data = data.sort(columns=['difficulty'])
    return data