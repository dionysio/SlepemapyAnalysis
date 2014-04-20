# -*- coding: utf-8 -*-

from numpy import int32, timedelta64, log
from common import first_questions, get_session_length
from pandas import Series
from elo_rating_system import estimate_prior_knowledge

def lengths_of_sessions(frame,threshold=None):
    """Returns length of each session.

    """

    groups = frame.groupby('user')
    if len(groups)==1:
        groups = get_session_length(frame)
    else:
        groups = groups.apply(get_session_length)
    groups = groups.reset_index()

    maximum = groups.session_number.value_counts().max()
    groups = groups.groupby('session_number')
    if threshold is None:
        groups = (groups.apply(lambda x: x.inserted.sum()/maximum))
    else:
        groups = (groups.apply(lambda x: x.inserted.sum()/maximum)).head(n=threshold)
    return groups


def number_of_answers(frame,threshold=None):
    """Returns number of answers for each session.
    """

    """Returns length of each session.

    :param threshold: maximum number of sessions to return
    """
    groups = frame.groupby(['user','session_number'])
    groups = groups.apply(lambda x: len(x))
    groups = groups.reset_index().groupby('session_number')
    if threshold is None:
        groups = (groups.sum()/groups.count().session_number.max())[0]
    else:
        groups = (groups.sum()/groups.count().session_number.max()).head(n=threshold)[0]
    return groups.astype(int32)


def _prepare_places(frame, codes):
    result = frame
    result.place_map = result.place_map.fillna(225)
    result['place_type'] = result.apply(lambda x: codes[codes.id==x.place_asked]['type'].values[0],axis=1)
    return result.groupby(['session_number','place_map','place_type'])


def _success(frame, threshold=None):
    first = first_questions(frame.groupby('session_number'))
    rates = [] #collects already calculated rates
    if threshold is None:
        limit = first.session_number.max()+1
    else:
        limit = threshold

    for i in range(first.session_number.min(),limit):
        temp = first[first.session_number<=i] #calculate with i# of sessions
        rates += [len(temp[temp.place_asked==temp.place_answered])/float(len(temp.place_asked))]
    return Series(rates)


def success(frame, codes, threshold=None):
    """Returns progress of mean_success_rate over sessions.

    :param threshold: consider only this many sessions
    """

    result = _prepare_places(frame, codes)
    return result.apply(lambda x: _success(x,threshold))


def skill(frame, difficulties, codes):
    """
    """

    result = _prepare_places(frame, codes)
    return result.apply(lambda x: estimate_prior_knowledge(x, difficulties)[0])


def _response_time(frame,threshold=None):
    """Returns progress of mean_success_rate and mean_response_time over sessions.

    :param threshold: consider only this many sessions
    """

    first = frame[frame.response_time<60000]
    first = first_questions(first.groupby('session_number'))
    times = [] #collects already calculated times
    if threshold is None:
        limit = first.session_number.max()+1
    else:
        limit = threshold

    for i in range(first.session_number.min(),limit):
        temp = first[first.session_number<=i] #calculate with i# of sessions
        times += [temp.response_time.mean()]
    return Series(times)


def response_time(frame, codes, threshold=None):
    """Returns progress of mean_success_rate over sessions.

    :param threshold: consider only this many sessions
    """

    result = _prepare_places(frame, codes)
    return result.apply(lambda x: _response_time(x,threshold))