# -*- coding: utf-8 -*-

from common import add_session_numbers

class Drawable():
    def __init__(self,path, frame, prior, codes, users=[], places=[]):
        """Drawable object should have assigned path, codes and DataFrame. 

        :param path: default output directory
        :param frame: dataframe to save
        :param prior: prior knowledge dict
        :param codes: dataframe with geography.place info
        :param users: filter by list of user IDs -- default [] -- no filter
        :param places: filter by place_asked IDs-- default [] -- no filter
        """
        self.current_directory = path
        self.prior = prior
        self.frame = frame
        self.codes = codes
        self.users = users
        self.places = places

        if users:
            self.frame = self.frame[self.frame.user.isin(users)]
        if places:
            self.frame = self.frame[self.frame.place_asked.isin(places)]

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


    def get_label(self, mapa, type):
        return self.get_country_name(mapa)+', '+self.get_place_type_name_plural(type)


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