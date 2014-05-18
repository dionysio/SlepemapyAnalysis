# -*- coding: utf-8 -*-

from common import first_questions, get_session_length, add_place_type, add_session_numbers
from pandas import Series, concat, unique
from elo_rating_system import estimate_prior_knowledge


def lengths_of_sessions(frame,threshold=None):
    """Returns length of each session.
    """

    groups = frame.groupby('user')
    if len(groups)==1:
        groups = get_session_length(frame)
    else:
        groups = groups.apply(get_session_length)

    groups = groups.reset_index().groupby('session_number')
    if threshold is None:
        groups = concat([groups.session_number.apply(len), groups.apply(lambda x: x.inserted.sum()/float(len(x)))],axis=1)
    else:
        groups = concat([groups.session_number.apply(len), (groups.apply(lambda x: x.inserted.sum()/float(len(x)))).head(n=threshold)],axis=1)
    groups.columns = ['counts','result']
    return groups


def number_of_answers(frame,threshold=None):
    """Returns number of answers for each session.

    :param threshold: maximum number of sessions to return
    """

    groups = frame.groupby(['user','session_number'])
    groups = groups.apply(len)
    groups = groups.reset_index().groupby('session_number')
    if threshold is None:
        groups = concat([groups.session_number.apply(len),groups.sum()[0]/groups.session_number.apply(len)],axis=1)
    else:
        groups = concat([groups.session_number.apply(len),groups.sum()[0]/groups.session_number.apply(len).head(n=threshold)],axis=1)
    groups.columns = ['counts','result']
    return groups


def _success(frame):
    '''Returns success rate of one specific user for every session (only first questions in session count).
    '''
    first = first_questions(frame.groupby('session_number'))
    first = first.groupby('session_number')
    first = first.apply(lambda x: len(x[x.place_asked==x.place_answered])/float(len(x.place_asked)))
    return first


def success(frame, codes, reorder_sessions = False):
    """Returns progress of success rate over sessions groupped by 'session_number','place_map','place_type'.
    """

    data = frame
    data.place_map = data.place_map.fillna(225)
    data = add_place_type(data, codes)
    if reorder_sessions:
        data = data.groupby(['place_map','place_type'])
        data = data.apply(add_session_numbers)
    data = data.groupby(['session_number','place_map','place_type'])
    r = data.apply(_success)
    r = r.reset_index(level=[0,1,2])
    r = r.set_index(['session_number','place_map','place_type'])[0]
    data = concat([data.apply(len),r], axis=1)
    data.columns = ['counts','result']
    return data


def skill(frame, difficulties, codes, reorder_sessions = False):
    """Returns progress of prior skill over sessions for one user.
    """

    data = frame
    data.place_map = data.place_map.fillna(225)
    data = add_place_type(data, codes)
    if reorder_sessions:
        data = data.groupby(['place_map','place_type'])
        data = data.apply(add_session_numbers)
    data = data.groupby(['session_number','place_map','place_type'])
    data = concat([data.apply(len), data.apply(lambda x: estimate_prior_knowledge(x, difficulties)[0])], axis=1)
    data.columns = ['counts','result']
    return data


def average_success(frame, codes, threshold=None, grpby = ['session_number','place_map','place_type']):
    """Returns progress of mean success rate over sessions. Multi-user version of success method
    
    :param threshold: lower threshold for counts
    """

    data = first_questions(frame.groupby(['user','session_number']))
    data = data.groupby('user')
    data = data.apply(lambda x: success(x, codes, grpby==['session_number']))
    data = data.reset_index()
    data = data.groupby(grpby)
    data = concat([data.apply(len), data.apply(lambda x: x.result.mean())],axis=1)
    data.columns = ['counts','result']
    return data[data.counts>threshold]


def average_skill(frame, difficulties, codes, threshold=None, grpby = ['session_number','place_map','place_type']):
    """Returns progress of mean prior skill over sessions. Multi-user version of skill method
    
    :param threshold: lower threshold for counts
    """

    data = first_questions(frame.groupby(['user','session_number']))
    data = data.groupby('user')
    data = data.apply(lambda x: skill(x, difficulties, codes, grpby==['session_number']))
    data = data.reset_index()
    data = data.groupby(grpby)
    data = concat([data.apply(len), data.apply(lambda x: x.result.mean())],axis=1)
    data.columns = ['counts','result']
    return data[data.counts>threshold]


'''def average(frame, func, threshold=None, grpby=['session_number','place_map','place_type']):
    """General function to return averaged values of skill/success/response time...
    
    :param threshold: lower threshold for counts
    """

    data = frame.groupby('user')
    data = data.apply(func)
    data = data.reset_index()
    data = data.groupby(grpby)
    data = concat([data.apply(len), data.apply(lambda x: x.result.mean())],axis=1)
    data.columns = ['counts','result']
    return data[data.counts>threshold]'''


def number_of_users(frame):
    """Returns number of users that got to specific session.
    """

    return frame.groupby('session_number').apply(lambda x: len(unique(x.user)))


def response_time_start_end(frame, response_time_threshold=60000, sample = 5):
    data = frame[frame.response_time<response_time_threshold]
    data = data.groupby(['user','session_number'])
    data = concat([data.apply(lambda x: x[:sample].response_time.mean()), data.apply(lambda x: x[-sample:].response_time.mean())], axis=1)
    data = data.reset_index()
    data = data.groupby('session_number')
    data = data.apply(lambda x: x[0].mean())-data.apply(lambda x: x[1].mean())
    return data