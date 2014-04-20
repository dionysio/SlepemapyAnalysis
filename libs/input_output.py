# -*- coding: utf-8 -*-

from elo_rating_system import calculate_difficulties
from common import add_session_numbers, defaultdict_factory

from numpy import uint32,uint16,uint8,float16
from pandas import read_csv
from yaml import dump,load
from argparse import ArgumentParser
from os import path

def load_geo_csv(path):
    """Imports csv into pandas DataFrame

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
    """

    types = {'user':uint32,'id':uint32,'place_asked':uint16,'place_answered':float16,'type':uint8,'response_time':uint32,'number_of_options':uint8,'place_map':float16,'ip_address':object}
    df = read_csv(path, parse_dates=[5],dtype=types,index_col='id')
    return df


def load_general_csv(path,enc = 'utf-8'):
    """Used for importing general csv

    :param names: new names for columns
    :param enc: encoding of csv file
    """

    return read_csv(path,encoding=enc)


def save_prior(out, path):
    """Calculates and saves difficulties of countries into json file.

    :param frame: calculate from this frame
    :param path: save to this path
    """

    with open(path,'w') as diff:
        dump(out,diff)


def load_prior(path):
    """Returns difficulties and prior_skills of places by loading yaml

    """

    with open(path) as diff:
        return load(diff)

def get_arguments(directory, require_items=True):
    parser = ArgumentParser()
    parser.add_argument('-f', '--file', metavar = 'FILE', help='Optional path to directory with geography-answer.csv and prior.yaml')
    if require_items:
        parser.add_argument('-i', '--items', required=True, metavar = 'ITEMS',nargs='+', help='id of an item to filter')
    args = parser.parse_args()
    
    if args.file is None:
        working_directory = directory
    else:
        working_directory = args.file
    
    frame = load_geo_csv(working_directory+"/data/geography.answer.csv")
    codes = load_general_csv(path=working_directory+'/data/geography.place.csv')

    if path.exists(working_directory+'/data/prior.yaml'):
        prior = load_prior(path=working_directory+'/data/prior.yaml')
    else:
        frame = add_session_numbers(frame)
        prior = calculate_difficulties(frame)[0]
        save_prior(prior,working_directory+'/data/prior.yaml')
    
    if require_items:
        return (args.items, frame, prior, codes, working_directory)
    else:
        return (None, frame, prior, codes, working_directory)