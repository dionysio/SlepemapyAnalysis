# -*- coding: utf-8 -*-

from pandas import DataFrame, Series, DatetimeIndex
from numpy import int32, timedelta64, arange

from math import exp
from collections import defaultdict


def add_session_numbers(frame,session_duration=timedelta64(30, 'm')):
    """Assignes session number to every answer.

    :param session_duration: duration of one session
    """

    result = frame.sort(['inserted'])
    result['session_number'] = (result['inserted'] - result['inserted'].shift(1) > session_duration).fillna(1).cumsum() #adds session numbers to every row
    return result


def get_session_lengths(frame):
    """Calculates session lengths in seconds.
    """

    group = frame.groupby('session_number')
    start = group.first()['inserted']
    end = group.last()['inserted']
    return (end-start)/timedelta64(1,'s')


def first_questions(frame):
    """Returns first questions for every session.
    """

    return frame.groupby('session_number').apply(lambda x: x.drop_duplicates(['place_asked']))


def _logis(value):
    return (1.0 / (1 + exp(-value)))


def elo(answer, prior_skill, user_number_of_answers, difficulty, place_number_of_answers):
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
    prediction = guess + (1-guess) * _logis(prior_skill-difficulty)
    result = answer['place_asked'] == answer['place_answered']

    k_func = lambda x: 1.0/(1+0.05*x)
    k1 = k_func(user_number_of_answers)
    k2 = k_func(place_number_of_answers)

    return  (prior_skill + k1 * (result - prediction),
            difficulty- k2 * (result - prediction))


def defaultdict_factory():
    return (0,0)


def estimate_prior_knowledge(frame, difficulties):
    """Estimates prior_knowledge of one user
    """
<<<<<<< HEAD:libs/analysis.py
    first = first_questions(frame)
    prior_skill= (0,0)

    for index, answer in first.iterrows():
        update = elo(answer,
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
        update = elo(answer,
                    prior_skill[answer.user][0], prior_skill[answer.user][1],
                    difficulties[answer.place_asked][0], difficulties[answer.place_asked][1])

        prior_skill[answer.user] = (update[0], prior_skill[answer.user][1]+1)
        difficulties[answer.place_asked] = (update[1], difficulties[answer.place_asked][1]+1)

    return difficulties


def estimate_current_knowledge(answers, skills, difficulties):
    for index,answer in answers.iterrows():
        update = elo(answer, 
            skills[answer.place_asked][0], skills[answer.place_asked][1],
            difficulties[answer.place_asked][0], difficulties[answer.place_asked][1])

        skills[answer.place_asked] = (update[0], skills[answer.place_asked][1]+1)
    return skills
=======

    first = first_questions(frame.groupby(['user','session_number']))
    first = first.set_index('user')

    places = defaultdict(inputoutput.defaultdict_factory)
    users  = defaultdict(inputoutput.defaultdict_factory)

    for row in first.iterrows():
        answer_user = row[0]
        answer_place = row[1]['place_asked']

        user = users[(answer_user,answer_place)]
        place = places[answer_place]
        update = elo(row[1],user[0],user[1],place[0],place[1])

        users[(answer_user,answer_place)] = [update[0],user[1]+1]
        places[answer_place] = [update[1],place[1]+1]

    if path:
        inputoutput.save_difficulties(places,path)
    return places
>>>>>>> 101963544307ed1c158181f775020dd1a28a530e:analysis.py


def difficulty_probabilities(difficulties):
    """Returns predicted probabilities of success for average user.
    """

    result = []
    for item in difficulties.iteritems():
        result += [_logis(-item[1][0])]
<<<<<<< HEAD:libs/analysis.py
    return Series(result,index=difficulties.keys())
=======
    return pd.Series(result,index=difficulties.keys())
>>>>>>> 101963544307ed1c158181f775020dd1a28a530e:analysis.py


def success_probabilities(skills,difficulties):
    """User-specific probabilities of success.
    """

    result = []
    for item in skills.iteritems():
        result += [_logis(item[1][0] - difficulties[item[0]][0])]
<<<<<<< HEAD:libs/analysis.py
    return Series(result,index=skills.keys())
=======
    result = pd.Series(result,index=skills.keys())
    return result
>>>>>>> 101963544307ed1c158181f775020dd1a28a530e:analysis.py


################################################################################


def weekdays(frame):
    """Returns counts of answers per weekdays (first value is Monday etc)
    """

    data = DataFrame()
    data['weekday'] = DatetimeIndex(frame.inserted).weekday
    counts = DataFrame(arange(7)*0)
    return (counts[0]+data.weekday.value_counts()).fillna(0)


def hours(frame):
    """Returns counts of answers per hour
    """

    data = DataFrame()
    data['hour'] = DatetimeIndex(frame.inserted).hour
    counts = DataFrame(arange(24)*0)
    return (counts[0]+data.hour.value_counts()).fillna(0)


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

    answers = frame
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


def mean_success(frame):
    """Returns mean_success_rate for each country.
    """

    groups = frame.groupby('place_asked')
    groups = groups.apply(lambda x: len(x[x.place_asked==x.place_answered])/float(len(x))*100)
    return groups.dropna()


def number_of_answers_session(frame,threshold=None):
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


def lengths_of_sessions(frame,threshold=None):
    """Returns length of each session.

    """
    groups = frame.groupby('user')
    if len(groups)==1:
        groups = get_session_lengths(frame)
    else:
        groups = groups.apply(get_session_lengths)
    groups = groups.reset_index()

    maximum = groups.session_number.value_counts().max()
    groups = groups.groupby('session_number')
    if threshold is None:
        groups = (groups.apply(lambda x: x.inserted.sum()/maximum))
    else:
        groups = (groups.apply(lambda x: x.inserted.sum()/maximum)).head(n=threshold)
    return groups


def mean_response_session(frame,threshold=None):
    """Returns progress of mean_success_rate and mean_response_time over sessions.

    :param threshold: consider only this many sessions
    """

    first = first_questions(frame.groupby('session_number'))
    times = [] #collects already calculated times
    if threshold is None:
        limit = first.session_number.max()+1
    else:
        limit = threshold

    for i in range(first.session_number.min(),limit):
        temp = first[first.session_number<=i] #calculate with i# of sessions
        times += [temp.response_time.mean()]

    return Series(times)


def mean_success_session(frame, threshold=None):
    """Returns progress of mean_success_rate and mean_response_time over sessions.

    :param threshold: consider only this many sessions
    """

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


def prior_skill_session(frame, difficulties, codes):
    """
    """
<<<<<<< HEAD:libs/analysis.py

    #first = first_questions(frame.groupby('session_number'))

    first = frame
    first.place_map = frame.place_map.fillna(225)
    first['place_type'] = first.apply(lambda x: codes[codes.id==x.place_asked]['type'].values[0],axis=1)
    first = first.groupby(['session_number','place_map','place_type'])

    return first.apply(lambda x: estimate_prior_knowledge(x, difficulties)[0])


def answers_percentages(frame, threshold=None):
    mistaken = mistaken_countries(frame)
    mistaken = mistaken.append(Series({frame.place_asked[0]: len(frame[frame.place_asked==frame.place_answered])}))
    mistaken = mistaken/float(mistaken.sum())
    if threshold is None:
        return mistaken
    else:
        return (mistaken[mistaken>=threshold]*100).append(Series({0:mistaken[mistaken<threshold].sum()*100}))
=======

    first = first_questions(frame.groupby(['session_number']))
    first = first.set_index('user')
    result = []
    skills = defaultdict(inputoutput.defaultdict_factory)

    if threshold is None:
        limit = first.session_number.max()+1
    else:
        limit = threshold

    for i in range(0,limit):
        temp = first[first.session_number==i]
        for row in temp.iterrows():
            answer_user = row[0]
            answer_place = row[1]['place_asked']
            user = skills[answer_place]
            place = difficulties[answer_place]

            update = elo(row[1],user[0],user[1],place[0],place[1])
            skills[answer_place] = (update[0],user[1]+1)

        result += [success_probabilities(skills,difficulties).mean()]
    return (pd.Series(result),skills)
>>>>>>> 101963544307ed1c158181f775020dd1a28a530e:analysis.py
