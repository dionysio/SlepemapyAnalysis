# -*- coding: utf-8 -*-

from analysis import add_session_numbers

class Drawable():

    """Drawable object should have assigned path, codes and DataFrame. Can be created empty and then assigned by setters.

    :param path: default output directory
    :param df: dataframe to save -- default None
    :param user: filter by user id -- default None
    :param place_asked: filter by place_asked -- default None
    """

    def __init__(   self,path='', df=None, user=None, place_asked=None, prior=None, codes=None):

        self.current_directory = path
        self.prior = prior
        self.frame = None
        self.place_asked = place_asked
        self.codes = codes

        if df is not None:
            #filtering frame
            self.frame = df
            #self.frame = self.frame[self.frame.response_time<60000]

            if user is not None:
                self.frame = self.frame[self.frame.user==user]
            if place_asked is not None:
                self.frame = self.frame[self.frame.place_asked==place_asked]

            #adding new values to frame
            self.frame = self.frame.groupby('user').apply(lambda x: add_session_numbers(x))
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