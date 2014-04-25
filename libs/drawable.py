# -*- coding: utf-8 -*-

from common import add_session_numbers

class Drawable():

    """Drawable object should have assigned path, codes and DataFrame. Can be created empty and then assigned by setters.

    :param path: default output directory
    :param df: dataframe to save -- default None
    :param user: filter by user id -- default None
    :param place_asked: filter by place_asked -- default None
    """

    def __init__(self,path='', df=None, user=None, place_asked=None, prior=None, codes=None):
        self.current_directory = path
        self.prior = prior
        self.frame = None
        self.place_asked = place_asked
        self.codes = codes

        if df is not None:
            self.frame = df
            if user is not None:
                self.frame = self.frame[self.frame.user==user]
            if place_asked is not None:
                self.frame = self.frame[self.frame.place_asked==place_asked]

            #adding new values to frame
            self.frame = self.frame.groupby('user').apply(add_session_numbers)
            self.frame.sort()


    def set_frame(self,frame):
        self.frame = frame


    def set_prior(self,prior):
        self.prior = prior


    def set_path(self,path):
        self.path = path


    def get_country_record(self,id):
        return self.codes[self.codes.id==id]


    def get_country_code(self,id):
        return self.get_country_record(id)['code'].values[0]


    def get_country_name(self,id):
        return self.get_country_record(id)['name'].values[0]


    def set_codes(self,codes):
        self.codes = codes


    def get_place_type_name(self,id):
        places = [u'Unknown',u'State',u'City',u'World',u'Continent',u'River',u'Lake',u'Region_cz',u'Bundesland',u'Province',u'Region_it',u'Region',u'Autonomous_Comunity',u'Mountains',u'Island']
        return places[id]


    def get_place_type_name_plural(self,id):
        places =[u'Unknown',u'States',u'Cities',u'World',u'Continents',u'Rivers',u'Lakes',u'Regions_cz',u'Bundesländer',u'Provinces',u'Regions_it',u'Regions',u'Autonomous_Comunities',u'Mountains',u'Islands']
        return places[id]