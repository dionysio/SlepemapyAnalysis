# -*- coding: utf-8 -*-

from numpy import uint32,uint16,uint8,float16
from pandas import read_csv
'''takes care of csv import from the website and loads csv into dataframe
'''
class Importer():        
    def load_geo_csv(self,filepath):
        #place_answered defaults to float dtype because integer dtype does not understand empty cells yet
        types = {'user':uint32,'id':uint32,'place_asked':uint16,'place_answered':float16,'type':uint8,'response_time':uint32,'number_of_options':uint8}
        df = read_csv(filepath, parse_dates=[5],dtype=types,index_col='id')
        return df
    
    def load_general_csv(self,filepath,columns = None):
        if columns is not None:
            df = read_csv(filepath,usecols=columns)
        else:
            df = read_csv(filepath)
        return df