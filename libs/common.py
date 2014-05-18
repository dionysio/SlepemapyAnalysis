# -*- coding: utf-8 -*-

from colorsys import hsv_to_rgb
from numpy import timedelta64
from math import exp
from random import shuffle

"""Assorted methods used in different modules
"""

def colour_range(length,hue_limit=1.0):
    """Generates shuffled range of colours.

    :param length: how many colours to generate
    :param hue_limit: limits the hue value -- default is 1.0 (no limit)
    """
    colors = [hsv_to_rgb((hue_limit*x)/length,1,1) for x in range(length)]
    shuffle(colors)
    return colors


def logis(value):
    """Logistic function
    """
    return (1.0 / (1 + exp(-value)))


def add_place_type(frame, codes):
    c = codes.type
    c.name = 'place_type'
    return frame.join(c, on=['place_asked'], how='right')


def add_session_numbers(frame,session_duration=timedelta64(30, 'm')):
    """Assignes session number to every answer.

    :param session_duration: duration of one session
    """

    result = frame.sort(['inserted'])
    result['session_number'] = (result['inserted'] - result['inserted'].shift(1) > session_duration).fillna(1).cumsum() #adds session numbers to every row
    return result


def add_item_numbers(frame):
    """Assignes number to each answer.
    """
    data = frame
    data['item_number'] = range(len(data))
    return data


def defaultdict_factory():
    return (0,0)


def first_questions(frame):
    """Returns first questions for every session.
    """

    return frame.apply(lambda x: x.drop_duplicates(['place_asked']))


def get_session_length(frame):
    """Calculates session lengths in seconds.
    """

    group = frame.groupby('session_number')
    start = group.first()['inserted']
    end = group.last()['inserted']
    return (end-start)/timedelta64(1,'s')