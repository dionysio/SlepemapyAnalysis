# -*- coding: utf-8 -*-

from elo_rating_system import calculate_difficulties
from common import add_session_numbers, defaultdict_factory

from numpy import uint32,uint16,uint8,float16
from pandas import read_csv, unique
from yaml import dump,load
from argparse import ArgumentParser
from os import path


def load_answer_csv(path, types = {'user':uint32,'id':uint32,'place_asked':uint16,'place_answered':float16,'type':uint8,'response_time':uint32,'number_of_options':uint8,'place_map':float16,'ip_address':object}
):
    """Imports answer csv into pandas DataFrame

    default dtypes:

    - 'user':uint32
    - 'id':uint32
    - 'place_asked':uint16
    - 'place_answered':float16 -- has to be float, because uint does not understand NaN (which place_answered may contain)
    - 'type':uint8
    - 'response_time':uint32
    - 'number_of_options':uint8
    - 'place_map':float16 -- has to be float, because uint does not understand NaN (which place_map may contain)
    - 'ip_address':object
    
    :param path: load csv from this path
    """

    df = read_csv(path, sep=',',parse_dates=[5],dtype=types,index_col='id')
    return df


def load_place_csv(path, types = {'id':uint32,'code':object,'name':object,'type':uint8}):
    """Used for importing csv of places
    
    :param path: load csv from this path
    """
    
    places = read_csv(path,encoding='utf-8', dtype = types)
    places.code = places.code.str.upper()
    return places


def load_ab_csv(path):
    '''Used for importing csv of AB testing. Splits dataframe into N categories based on its ab_value column. 
    Expects same csv as answer, but with two additional columns:
    - 'ab_id':uint32
    - 'ab_value':object
    
    :param path: load csv from this path
    '''
    types = {'ab_id':uint32, 'user':uint32,'id':uint32,'place_asked':uint16,'place_answered':float16,'type':uint8,'response_time':uint32,'number_of_options':uint8,'place_map_id':float16,'ip_address':object, 'ab_value':object}
    frame = read_csv(path, parse_dates=[6],dtype=types,index_col='id')
    frame.rename(columns={'place_map_id':'place_map'}, inplace=True)
    result =[]
    for element in unique(frame.ab_values):
        result.append(frame[frame.ab_value == element])
    return result


def save_prior(out, path):
    """Calculates and saves difficulties of countries into json file.

    :param frame: calculate from this frame
    :param path: save to this path
    """

    with open(path,'w') as diff:
        dump(out,diff)


def load_prior(path):
    """Returns difficulties and prior_skills of places by loading yaml file

    :param path: load yaml from this path
    """

    with open(path) as diff:
        return load(diff)

def get_arguments(directory, require_items=True):
    """Parses arguments from command line (-f for directory and -i for items) and returns them as tuple.
    
    :param directory: load from this directory as default (if -f is not specified)
    :param require_items: whether to is item argument required
    :returns: (items, frame, prior, codes, working_directory)
    """

    parser = ArgumentParser()
    parser.add_argument('-f', '--file', metavar = 'FILE', help='Optional path to directory with geography-answer.csv and prior.yaml')
    if require_items:
        parser.add_argument('-i', '--items', required=True, metavar = 'ITEMS',nargs='+', help='id of an item to filter')
    args = parser.parse_args()
    
    if args.file is None:
        working_directory = directory
    else:
        working_directory = args.file
    
    frame = load_answer_csv(working_directory+"/data/geography.answer.csv")
    codes = load_place_csv(working_directory+'/data/geography.place.csv')

    if path.exists(working_directory+'/data/prior.yaml'):
        prior = load_prior(working_directory+'/data/prior.yaml')
    else:
        frame = frame.groupby('user').apply(add_session_numbers)
        prior = calculate_difficulties(frame)
        save_prior(prior,working_directory+'/data/prior.yaml')
    
    if require_items:
        return (args.items, frame, prior, codes, working_directory)
    else:
        return (None, frame, prior, codes, working_directory)