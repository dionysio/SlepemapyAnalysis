# -*- coding: utf-8 -*-

from numpy import timedelta64
from common import first_questions, get_session_length
from pandas import Series, concat
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


def _prepare_places(frame, codes):
    '''Prepares frame for ['session_number','place_map','place_type'] groupings
    '''

    result = frame
    result.place_map = result.place_map.fillna(225)
    result['place_type'] = result.apply(lambda x: codes[codes.id==x.place_asked]['type'].values[0],axis=1)
    return result.groupby(['session_number','place_map','place_type'])


def _success(frame):
    '''Returns success rate of one specific user for every session (only first questions in session count).
    '''
    first = first_questions(frame.groupby('session_number'))
    first = first.groupby('session_number')
    first = first.apply(lambda x: len(x[x.place_asked==x.place_answered])/float(len(x.place_asked)))
    return first


def success(frame, codes):
    """Returns progress of success rate over sessions groupped by 'session_number','place_map','place_type'.
    """

    data = _prepare_places(frame, codes)
    r = data.apply(lambda x: _success(x))
    r = r.reset_index(level=[0,1,2])
    r = r.set_index(['session_number','place_map','place_type'])[0]
    data = concat([data.apply(len),r], axis=1)
    data.columns = ['counts','result']
    return data


def skill(frame, difficulties, codes):
    """Returns progress of prior skill over sessions, expects only one user.
    """

    data = _prepare_places(frame, codes)
    data = concat([data.apply(len), data.apply(lambda x: estimate_prior_knowledge(x, difficulties)[0])], axis=1)
    data.columns = ['counts','result']
    return data


def average_success(frame, codes):
    """Returns progress of mean success rate over sessions.
    """

    data = frame.groupby('user')
    data = data.apply(lambda x: success(x, codes))
    data = data.reset_index()
    data = data.groupby(['session_number','place_map','place_type'])
    data = concat([data.apply(lambda x: x.counts.sum()), data.apply(lambda x: x.result.mean())],axis=1)
    data.columns = ['counts','result']
    return data


def average_skill(frame, difficulties, codes):
    """Returns progress of mean prior skill over sessions.
    """

    data = frame.groupby('user')
    data = data.apply(lambda x: skill(x, difficulties, codes))
    data = data.reset_index()
    data = data.groupby(['session_number','place_map','place_type'])
    data = concat([data.apply(lambda x: x.counts.sum()), data.apply(lambda x: x.result.mean())],axis=1)
    data.columns = ['counts','result']
    return data
    