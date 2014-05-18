# -*- coding: utf-8 -*-

from pandas import DatetimeIndex, DataFrame, DateOffset, Series
from numpy import arange

def weekday_activity(frame):
    """Returns counts of answers per weekdays (first value is Monday etc)
    """

    data = DataFrame()
    data['weekday'] = DatetimeIndex(frame.inserted).weekday
    counts = DataFrame(arange(7)*0)
    return (counts[0]+data.weekday.value_counts()).fillna(0)


def hourly_activity(frame):
    """Returns counts of answers per hour
    """

    data = DataFrame()
    data['hour'] = DatetimeIndex(frame.inserted).hour
    counts = DataFrame(arange(24)*0)
    return (counts[0]+data.hour.value_counts()).fillna(0)


def _success(frame, frequency='M'):
    """Returns success rate for specific time period
    """

    if frequency == 'M':
        result = frame[frame.inserted[0]:frame.inserted[0]+DateOffset(months=1)]
    elif frequency== 'W':
        result = frame[frame.inserted[0]:frame.inserted[0]+DateOffset(days=7)]
    else:
        result = frame[frame.inserted[0]:frame.inserted[0]+DateOffset(days=1)]
    return len(result[result.place_asked==result.place_answered])/float(len(result)) if len(result) else None


def success(frame, frequency = 'M'):
    """Returns success rate for every time period
    """

    result = frame.set_index(DatetimeIndex(frame.inserted))
    if frequency=='M':
        result = result.groupby(['user',lambda x: x.year,lambda x: x.month])
    elif frequency == 'W':
        result = result.groupby(['user',lambda x: x.year,lambda x: x.week])
    else:
        result = result.groupby(['user',lambda x: x.year,lambda x: x.day])
    result = result.apply(lambda x: Series({'success_rate':_success(x,frequency), 'date':x.inserted.values[0]}))
    result = result.set_index(DatetimeIndex(result['date']))
    result = result.resample(frequency, how='mean').success_rate
    result.index = result.index - DateOffset(days=1)
    return result


def number_of_users(frame, frequency = 'M'):
    """Returns number of users for every time period
    """

    times = frame.groupby('user').apply(lambda x: x.inserted.values[0])
    times = times.reset_index()
    times = times.set_index(DatetimeIndex(times[0]))
    return times.resample(frequency,how=len).user


def number_of_answers(frame, frequency= 'M'):
    """Returns number of answers for every time period
    """

    
    result = frame.set_index(DatetimeIndex(frame.inserted))
    if frequency=='M':
        result = result.groupby(['user',lambda x: x.year,lambda x: x.month])
    elif frequency == 'W':
        result = result.groupby(['user',lambda x: x.year,lambda x: x.week])
    else:
        result = result.groupby(['user',lambda x: x.year,lambda x: x.day])
    result = result.apply(lambda x: Series({'length': len(x) if len(x) else None, 'date':x.inserted.values[0]}))
    result = result.set_index(DatetimeIndex(result.date))
    return result.resample(frequency,how='mean').length