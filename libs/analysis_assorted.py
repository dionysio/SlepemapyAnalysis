# -*- coding: utf-8 -*-

from common import add_item_numbers, first_questions, logis
from pandas import DataFrame, Series, concat
from analysis_per_place import response_time, mistaken_places
from elo_rating_system import estimate_current_knowledge


def response_time_over_items(frame, threshold=60000):
    '''Returns mean response_time over answers for specific country.
    
    :param threshold: upper threshold for response times
    '''
    data = frame[frame.response_time<threshold]
    data = first_questions(data.groupby(['user','session_number']))
    data = data.groupby('user')
    data = data.apply(add_item_numbers)
    data = data.groupby('item_number')
    data = concat([data.apply(lambda x: x.item_number.count()),data.apply(lambda x: x.response_time.mean())],axis=1)
    data.columns = ['counts','result']
    return data


def success_over_items(frame):
    '''Returns mean success rate over answers for specific country.
    '''
    data = first_questions(frame.groupby(['user','session_number']))
    data = data.groupby('user')
    data = data.apply(add_item_numbers)
    data = data.groupby('item_number')
    data = concat([data.apply(lambda x: x.item_number.count()),data.apply(lambda x: len(x[x.place_asked==x.place_answered])/float(len(x)))],axis=1)
    data.columns = ['counts','result']
    return data


def current_knowledge_over_items(frame, difficulties):
    data = frame.groupby('user')
    data = data.apply(add_item_numbers)
    data = data.groupby('item_number')
    data = data.apply(lambda x: DataFrame.from_dict(estimate_current_knowledge(x, difficulties),orient='index'))[0]
    data = data.reset_index()
    data = data.apply(lambda x: logis(x[0] - difficulties[x["level_1"]][0]),axis=1)
    data.name = 'result'
    data.index.name = 'item_number'
    return data.reset_index()


def average_over_items(frame, func):
    data = first_questions(frame.groupby(['session_number','user']))
    data = data.groupby('place_asked')
    data = data.apply(func)
    data = data.reset_index()[['item_number','result']].groupby('item_number')
    data = concat([data.apply(len), data.apply(lambda x: x['result'].mean())],axis=1)
    data.columns = ['counts','result']
    return data


def answer_portions(frame, threshold=None):
    """Returns portions of answers for specific country.
    
    :param threshold: limit of values to include as separate slice -- default is None
    """

    mistaken = mistaken_places(frame)[0]
    mistaken = mistaken.append(Series({frame.place_asked[0]: len(frame[frame.place_asked==frame.place_answered])}))
    mistaken = mistaken/float(mistaken.sum())
    if threshold is None:
        return mistaken
    else:
        return (mistaken[mistaken>=threshold]*100).append(Series({0:mistaken[mistaken<threshold].sum()*100}))


def difficulty_response_time(frame, difficulty):
    '''Returns mean response time for correct/incorrect answers for countries with different difficulties
    '''
    data = first_questions(frame.groupby(['user','session_number']))
    data = DataFrame(response_time(data,right=True))
    data.columns = ['correct']
    data['incorrect'] = response_time(frame,right=False)
    d = Series(difficulty)
    d = d.map(lambda x: logis(-x[0]))
    d.name = 'difficulty'
    data = data.join(d)    
    data = data.dropna()
    data = data.sort(columns=['difficulty'])
    return data