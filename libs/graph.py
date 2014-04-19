# -*- coding: utf-8 -*-

from drawable import *
import analysis

from numpy import arange
import matplotlib.pyplot as plt
from matplotlib import interactive
from matplotlib.dates import date2num
from matplotlib.ticker import FuncFormatter, MultipleLocator
from pandas import DateOffset
import colorbrewer
import colorsys

class Graph(Drawable):

    def __init__(   self, path='', df=None, user=None, place_asked=None, prior=None, codes= None):
        """Sets matplotlib to be non-interactive. All other defaults are same as in Drawable.
        """

        Drawable.__init__(self, path, df, user, place_asked, prior, codes)
        interactive(False) #disable matplotlib interactivity


    @staticmethod
    def colour_range(length,hue_limit=1.0):
        """Generates range of colours.
    
        :param length: how many colours to generate
        :param hue_limit: limits the hue value -- default 0.32
        """
        colors = [colorsys.hsv_to_rgb((hue_limit*x)/length,1,1) for x in range(length)]
        return colors


    def weekday_activity(self, path=''):
        """Draws number of questions asked per weekday.

        :param path: output directory -- default is '' (current dir)
        """

        if not path:
            path = self.current_directory+'/graphs/'
        data = analysis.weekdays(self.frame)
        if not data.empty:
            ind = arange(7)
            width = 0.4
            fig, ax = plt.subplots()
            bars = ax.bar(ind+width/2, data, width=width, color="cyan")
            ax.set_xticks(ind+width)

            ax.set_ylabel(u"Number of questions")
            ax.set_title(u"Number of questions per weekday")
            ax.set_xticklabels( (u"Monday", u"Tuesday", u"Wednesday", u"Thursday", u"Friday",u"Saturday",u"Sunday"))

            plt.savefig(path+'weekday_activity.svg', bbox_inches='tight')
            plt.close()


    def hourly_activity(self, path=''):
        """Draws number of questions asked per hour.

        :param path: output directory -- default is '' (current dir)
        """

        if not path:
            path = self.current_directory+'/graphs/'
        data = analysis.hours(self.frame)
        if not data.empty:
            ind = arange(24)
            width = 0.4

            fig, ax = plt.subplots()
            bars = ax.bar(ind+width/2, data, width, color="cyan")
            ax.set_xticks(ind+width)

            ax.set_ylabel(u"Number of questions")
            ax.set_title(u"Number of questions per hour")
            ax.set_xticklabels(ind)

            plt.savefig(path+'hourly_activity.svg', bbox_inches='tight')
            plt.close()


    def lengths_of_sessions(self, path='',threshold=None):
        """Draws graph of lengths of sessions per session.

        :param threshold: how many sessions to plot (globally there are 50+ sessions, but most of the people stay for 10+-)
        :param path: -- default is '' (current_directory)
        """

        if not path:
            path = self.current_directory+'/graphs/'
        data = analysis.lengths_of_sessions(self.frame, threshold)
        if not data.empty:
            fig, ax = plt.subplots()

            ax.bar(arange(len(data)),data.values, color="cyan")
            
            ax.set_title(u"Lengths of sessions over time")
            ax.set_ylabel(u"Session length [seconds]")
            ax.set_xlabel(u"Session number")

            plt.savefig(path+'lenghts_of_sessions.svg', bbox_inches='tight')
            plt.close()

    @staticmethod
    def locator(x):
        return MultipleLocator(int(round(len(x)/20.0))) #magic value


    def number_of_answers(self, path='',threshold=None):
        """Draws graph of number of answers per session.

        :param threshold: how many sessions to plot
        :param path: -- default is '' (current_directory)
        """

        if not path:
            path = self.current_directory+'/graphs/'
        data = analysis.number_of_answers_session(self.frame,threshold)
        if not data.empty:
            fig, ax = plt.subplots()

            ax.bar(arange(len(data)),data.values, color="cyan")
            ax.set_title(u"Number of questions over sessions")
            ax.set_ylabel(u"Mean number of questions")
            ax.set_xlabel(u"Session number")

            plt.savefig(path+'number_of_answers.svg', bbox_inches='tight')
            plt.close()


    def success(self,path='',threshold=None):
        """Draws graph of mean success and mean response per session.

        :param threshold: how many sessions to draw -- default is 10
        :param path: output directory -- default is '' (current_directory)
        """

        if not path:
            path = self.current_directory+'/graphs/'
        data = analysis.mean_success_session(self.frame,self.codes,threshold)

        if not data.empty:
            fig, ax = plt.subplots()

            data = data.reset_index()
            diff = (data.values.max() - data.values.min())/10.0
            max_limit = 1 if data.values.max()+diff>1 else data.values.max()+diff
            min_limit = 0 if data.values.min()-diff<0 else data.values.min()-diff
            plt.ylim((min_limit,max_limit))
            plt.xlim((data.session_number.min()-0.1,data.session_number.max()+0.1))

            data = data.groupby(['place_map','place_type'])
            _colours = self.colour_range(len(data)+1)
            data.apply(lambda x: self._plot_group(x,ax,_colours.pop()))

            ax.set_title(u"Progress of success rate over sessions")
            ax.set_xlabel('Session number')
            ax.set_ylabel('Mean success rate')
            plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

            plt.savefig(path+'success.svg', bbox_inches='tight')
            plt.close()


    def _plot_group(self, data, ax, colour):
        ax.plot(data['session_number'],data[0],color=colour,marker='o',label=(str(self.get_country_code(data.name[0])),data.name[1]))


    def skill(self, path='', threshold=None):
        """Draws graph of mean skill and mean response time per session.

        :param threshold: how many sessions to draw -- default is 10
        :param path: output directory -- default is '' (current_directory)
        """

        if not path:
            path = self.current_directory+'/graphs/'
        data = analysis.prior_skill_session(self.frame,self.prior,self.codes)

        if not data.empty:
            fig, ax = plt.subplots()

            data = data.reset_index()
            diff = (data[0].max() - data[0].min())/10.0
            plt.ylim((data[0].min()-diff,data[0].max()+diff))
            plt.xlim((data.session_number.min()-0.1,data.session_number.max()+0.1))

            data = data.groupby(['place_map','place_type'])
            _colours = self.colour_range(len(data)+1)
            data.apply(lambda x: self._plot_group(x,ax,_colours.pop()))

            ax.set_title(u"Progress of skill over sessions for individual regions")
            ax.set_xlabel('Session number')
            ax.set_ylabel('Skill')
            plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

            plt.savefig(path+'skill.svg', bbox_inches='tight')
            plt.close()


    def answers_percentages(self, path='', threshold=0.01):
        """Draws graph 

        :param threshold: how many sessions to draw -- default is 10
        :param path: output directory -- default is '' (current_directory)
        """

        if not path:
            path = self.current_directory+'/graphs/'
        data = analysis.answers_percentages(self.frame, threshold)

        if not data.empty:
            fig, ax = plt.subplots()

            colours = colorbrewer.Paired[len(data)]
            colours = [tuple(i/255. for i in c) for c in colours]
            labels = []
            for index,values in data.iteritems():
                id = int(index)
                if id==0:
                    labels += ['others']
                else:
                    labels += [self.get_country_name(id)]

            ax.pie(data.values,colors=colours ,labels=labels, autopct='%1.1f%%')
            ax.set_title(u"Percentages of answers for "+labels[-2])

            plt.savefig(path+'answers_percentages.svg', bbox_inches='tight')
            plt.close()


    def number_of_users(self, path ='', frequency = 'M'):
        """Draws graph

        :param frequency: defines sampling value - all available frequencies are available at pandas documentation (http://pandas.pydata.org/pandas-docs/stable/timeseries.html#dateoffset-objects) -- default is 'M' == month
        :param path: output directory -- default is '' (current_directory)
        """
        
        if not path:
            path = self.current_directory+'/graphs/'
        data = analysis.number_of_users(self.frame,frequency)

        if not data.empty:
            fig, ax = plt.subplots()
            ax.bar(data.index,data.values, color="cyan", width=15)

            diff = (data.max() - data.min())/10.0
            min_limit = 0 if data.min()-diff<0 else data.min()-diff
            plt.ylim((min_limit,data.max()+diff))
            plt.xlim((data.index.min()-DateOffset(days=3),data.index.max()+DateOffset(days=3)))

            ax.set_title(u"Number of users per "+frequency)
            ax.set_ylabel(u"Number of users")
            ax.set_xlabel(u"Date")
            fig.autofmt_xdate()

            plt.savefig(path+'number_of_users.svg', bbox_inches='tight')
            plt.close()


    def mean_success_rate(self, path ='',frequency='M'):
        """Draws graph

        :param path: output directory -- default is '' (current_directory)
        """
        
        if not path:
            path = self.current_directory+'/graphs/'
        data = analysis.mean_success_rate(self.frame,frequency)

        if not data.empty:
            fig, ax = plt.subplots()
            ax.bar(data.index,data.values, color="cyan")

            diff = (data.max() - data.min())/10.0
            max_limit = 1 if data.max()+diff>1 else data.max()+diff
            min_limit = 0 if data.max()-diff<0 else data.min()-diff
            plt.ylim((min_limit,max_limit))
            plt.xlim((data.index.min()-DateOffset(days=3),data.index.max()+DateOffset(days=3)))

            fig.autofmt_xdate()
            ax.set_title(u"Mean success rate of users per "+frequency)
            ax.set_ylabel(u"Mean success rate")
            ax.set_xlabel(u"Date")

            plt.savefig(path+'mean_success_rate.svg', bbox_inches='tight')
            plt.close()


    def mean_number_of_answers(self, path='', frequency='M'):
        """Draws graph

        :param path: output directory -- default is '' (current_directory)
        """
        
        if not path:
            path = self.current_directory+'/graphs/'
        data = analysis.mean_number_of_answers(self.frame,frequency)

        if not data.empty:
            fig, ax = plt.subplots()
            ax.bar(data.index,data.values, color="cyan")

            diff = (data.max() - data.min())/10.0
            min_limit = 0 if data.min()-diff<0 else data.min()-diff
            plt.ylim((min_limit,data.max()+diff))
            plt.xlim((data.index.min()-DateOffset(days=3),data.index.max()+DateOffset(days=3)))

            fig.autofmt_xdate()
            ax.set_title(u"Mean number of answers per "+frequency)
            ax.set_ylabel(u"Mean number of answers")
            ax.set_xlabel(u"Date")

            plt.savefig(path+'mean_number_of_answers.svg', bbox_inches='tight')
            plt.close()