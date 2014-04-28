# -*- coding: utf-8 -*-

from drawable import Drawable
import analysis_per_country
import analysis_per_time
import analysis_per_session
from common import colour_range
from elo_rating_system import calculate_difficulties

from numpy import arange, ceil
import matplotlib.pyplot as plt
from matplotlib import interactive
from matplotlib import rc
import colorbrewer
from os import path, makedirs

class Graph(Drawable):

    def __init__(self, path='', df=None, user=None, place_asked=None, prior=None, codes= None):
        """Sets matplotlib to be non-interactive. All other defaults are same as in Drawable.
        """

        Drawable.__init__(self, path, df, user, place_asked, prior, codes)
        interactive(False) #disable matplotlib interactivity
        rc('font', **{'sans-serif' : 'Times New Roman','family' : 'sans-serif'})


    def _plot_group(self,data, ax, colour, marker):
        name = self.get_country_name(data.name[0])+', '+self.get_place_type_name_plural(data.name[1])
        return ax.plot(data['session_number'],data['result'],color=colour,marker=marker, label=name)


    def _plot_separated_group(self, data, output, name):
        if len(data)>1:
            fig, ax = plt.subplots()
            ax.set_xlabel('Session number')
            ax.set_ylabel(name, color='cyan')
            l1 = self._plot_second_axis(data, ax)
            l2 = self._plot_group(data, ax, 'cyan', 'o')
            lines = l1+l2
            labels = [l.get_label() for l in lines]
            plt.legend(lines, labels, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
            plt.savefig(output, bbox_inches='tight')
            plt.close()


    def _plot_second_axis(self, data, first_ax, name='Count'):
        ax = first_ax.twinx()
        ax.set_ylabel(name, color='red')
        return ax.plot(data['session_number'], data['counts'], color = 'red', linestyle='--', label='Count')


    def format_date(x, pos=None):
        thisind = np.clip(int(x+0.5), 0, N-1)
        return r.date[thisind].strftime('%Y-%m-%d')


    def skill(self, directory='', threshold=None, plot_individual_graphs = True):
        """Draws graph of mean skill and mean response time per session.

        :param threshold: how many sessions to draw -- default is 10
        :param directory: output directory -- default is '' (current_directory)
        """

        if not directory:
            directory = self.current_directory+'/graphs/'
        data = analysis_per_session.average_skill(self.frame,self.prior[0],self.codes)

        if not data.empty:
            fig, ax = plt.subplots()

            data = data.reset_index()
            data = data.groupby(['place_map','place_type'])
            colours = colour_range(len(data)+1)
            markers = ['o', 'x', 's']*(ceil((len(data)+1)/3.0))
            data.apply(lambda x: self._plot_group(x,ax,colours.pop(),markers.pop()))
            ax.set_title(u"Progress of skill over sessions for individual regions")
            ax.set_xlabel('Session number')
            ax.set_ylabel('Skill')
            plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
            plt.savefig(directory+'skill.svg', bbox_inches='tight')
            plt.close()

            if plot_individual_graphs:
                if not path.exists(directory+'skill_separated/'):
                    makedirs(directory+'skill_separated/')
                paths = [directory+'skill_separated/'+str(item[0])+'-'+str(item[1])+'.svg' for item in data.apply(lambda x: x.name).values]
                def _get_default():
                    try:
                        return paths.pop()
                    except IndexError:
                        return (0,0)
                data.apply(lambda x: self._plot_separated_group(x, _get_default(),'Skill'))


    def success_over_session(self,directory='', plot_individual_graphs=True):
        """Draws graph of mean success per session.

        :param threshold: how many sessions to draw -- default is 10
        :param directory: output directory -- default is '' (current_directory)
        """

        if not directory:
            directory = self.current_directory+'/graphs/'
        data = analysis_per_session.average_success(self.frame,self.codes)

        if not data.empty:
            fig, ax = plt.subplots()

            data = data.reset_index()
            data = data.groupby(['place_map','place_type'])
            colours = colour_range(len(data)+1)
            markers = ['o', 'x', 's']*(ceil((len(data)+1)/3.0))
            data.apply(lambda x: self._plot_group(x,ax,colours.pop(),markers.pop()))  
            ax.set_title(u"Progress of success rate over sessions")
            ax.set_xlabel('Session number')
            ax.set_ylabel('Mean success rate')
            plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
            plt.savefig(directory+'success_over_session.svg', bbox_inches='tight')
            
            if plot_individual_graphs:
                if not path.exists(directory+'success_separated/'):
                    makedirs(directory+'success_separated/')
                paths = [directory+'success_separated/'+str(i)+'.svg' for i in xrange(len(data)+1)]
                data.apply(lambda x: self._plot_separated_group(x, paths.pop(),'Success'))
            plt.close()


    def lengths_of_sessions(self, directory='',threshold=None):
        """Draws graph of lengths of sessions per session.

        :param threshold: how many sessions to plot (globally there are 50+ sessions, but most of the people stay for 10+-)
        :param directory: -- default is '' (current_directory)
        """

        if not directory:
            directory = self.current_directory+'/graphs/'
        data = analysis_per_session.lengths_of_sessions(self.frame, threshold)
        if not data.empty:
            fig, ax = plt.subplots()

            ax.bar(range(len(data)),data.values, color="cyan")
            
            ax.set_title(u"Lengths of sessions over time")
            ax.set_ylabel(u"Session length [seconds]")
            ax.set_xlabel(u"Session number")

            plt.savefig(directory+'lenghts_of_sessions.svg', bbox_inches='tight')
            plt.close()


    def number_of_answers_over_session(self, directory='',threshold=None):
        """Draws graph of number of answers per session.

        :param threshold: how many sessions to plot
        :param directory: -- default is '' (current_directory)
        """

        if not directory:
            directory = self.current_directory+'/graphs/'
        data = analysis_per_session.number_of_answers(self.frame,threshold)
        if not data.empty:
            fig, ax = plt.subplots()

            data = data.reset_index()
            ax.bar(range(len(data)),data.result, color="cyan")
            self._plot_second_axis(data, ax)
            ax.set_title(u"Number of questions over sessions")
            ax.set_ylabel(u"Mean number of questions")
            ax.set_xlabel(u"Session number")

            plt.savefig(directory+'number_of_answers_over_session.svg', bbox_inches='tight')
            plt.close()


################################################################################


    def weekday_activity(self, directory=''):
        """Draws number of questions asked per weekday.

        :param directory: output directory -- default is '' (current dir)
        """

        if not directory:
            directory = self.current_directory+'/graphs/'
        data = analysis_per_time.weekday_activity(self.frame)
        if not data.empty:
            ind = arange(7)
            width = 0.4
            fig, ax = plt.subplots()
            bars = ax.bar(ind+width/2, data, width=width, color="cyan")
            ax.set_xticks(ind+width)

            ax.set_ylabel(u"Number of questions")
            ax.set_title(u"Number of questions per weekday")
            ax.set_xticklabels( (u"Monday", u"Tuesday", u"Wednesday", u"Thursday", u"Friday",u"Saturday",u"Sunday"))

            plt.savefig(directory+'weekday_activity.svg', bbox_inches='tight')
            plt.close()


    def hourly_activity(self, directory=''):
        """Draws number of questions asked per hour.

        :param directory: output directory -- default is '' (current dir)
        """

        if not directory:
            directory = self.current_directory+'/graphs/'
        data = analysis_per_time.hourly_activity(self.frame)
        if not data.empty:
            ind = arange(24)
            width = 0.4

            fig, ax = plt.subplots()
            bars = ax.bar(ind+width/2, data, width, color="cyan")
            ax.set_xticks(ind+width)

            ax.set_ylabel(u"Number of questions")
            ax.set_title(u"Number of questions per hour")
            ax.set_xticklabels(ind)

            plt.savefig(directory+'hourly_activity.svg', bbox_inches='tight')
            plt.close()


    def success_over_time(self, directory ='',frequency='M'):
        """Draws graph

        :param directory: output directory -- default is '' (current_directory)
        """
        
        if not directory:
            directory = self.current_directory+'/graphs/'
        data = analysis_per_time.success(self.frame,frequency)

        if not data.empty:
            fig, ax = plt.subplots()
            ind = arange(len(data))
            width = 0.4
            bars = ax.bar(ind+width/2, data.values, width=width, color="cyan")

            ax.set_title(u"Mean success rate of users per "+frequency)
            ax.set_ylabel(u"Mean success rate")
            ax.set_xlabel(u"Date")
            ax.set_xticks(ind+width)
            ax.set_xticklabels(data.index.date)
            fig.autofmt_xdate()

            plt.savefig(directory+'success_over_time.svg', bbox_inches='tight')
            plt.close()


    def number_of_answers_over_time(self, directory='', frequency='M'):
        """Draws graph

        :param directory: output directory -- default is '' (current_directory)
        """
        
        if not directory:
            directory = self.current_directory+'/graphs/'
        data = analysis_per_time.number_of_answers(self.frame,frequency)

        if not data.empty:
            fig, ax = plt.subplots()
            ind = arange(len(data))
            width = 0.4
            bars = ax.bar(ind+width/2, data.values, width=width, color="cyan")

            ax.set_title(u"Mean number of answers per "+frequency)
            ax.set_ylabel(u"Mean number of answers")
            ax.set_xlabel(u"Date")
            ax.set_xticks(ind+width)
            ax.set_xticklabels(data.index.date)
            fig.autofmt_xdate()

            plt.savefig(directory+'number_of_answers_over_time.svg', bbox_inches='tight')
            plt.close()


    def number_of_users(self, directory ='', frequency = 'M'):
        """Draws graph

        :param frequency: defines sampling value - all available frequencies are available at pandas documentation (http://pandas.pydata.org/pandas-docs/stable/timeseries.html#dateoffset-objects) -- default is 'M' == month
        :param directory: output directory -- default is '' (current_directory)
        """
        
        if not directory:
            directory = self.current_directory+'/graphs/'
        data = analysis_per_time.number_of_users(self.frame,frequency)

        if not data.empty:
            fig, ax = plt.subplots()
            ind = arange(len(data))
            width = 0.4
            ax.bar(ind+width/2, data.values, width=width, color="cyan")

            ax.set_title(u"Number of new users per "+frequency)
            ax.set_ylabel(u"Number of new users")
            ax.set_xlabel(u"Date")
            ax.set_xticks(ind+width)
            ax.set_xticklabels(data.index.date)
            fig.autofmt_xdate()

            plt.savefig(directory+'number_of_users.svg', bbox_inches='tight')
            plt.close()


################################################################################


    def answer_portions(self, directory='', threshold=0.01):
        """Draws graph 

        :param threshold: how many sessions to draw -- default is 10
        :param directory: output directory -- default is '' (current_directory)
        """

        if not directory:
            directory = self.current_directory+'/graphs/'
        data = analysis_per_country.answer_portions(self.frame, threshold)

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

            plt.savefig(directory+'answers_portions.svg', bbox_inches='tight')
            plt.close()
    
    
    def difficulty_histogram(self, directory=''):
        """Draws graph 

        :param directory: output directory -- default is '' (current_directory)
        """

        if not directory:
            directory = self.current_directory+'/graphs/'
        fig, ax = plt.subplots()
        items = [item[0] for item in self.prior[0].itervalues()]
        ax.hist(items)
        ax.set_title(u"Histogram of difficulty ")
        ax.set_ylabel(u"Number of countries")
        ax.set_xlabel(u"Estimated difficulty")
        plt.savefig(directory+'difficulty_histogram.svg', bbox_inches='tight')
        plt.close()

    
    def prior_skill_histogram(self, directory=''):
        """Draws graph 

        :param directory: output directory -- default is '' (current_directory)
        """

        if not directory:
            directory = self.current_directory+'/graphs/'
        fig, ax = plt.subplots()
        items = [item[0] for item in self.prior[1].itervalues()]
        ax.hist(items)
        ax.set_title(u"Histogram of prior skill ")
        ax.set_ylabel(u"Number of users")
        ax.set_xlabel(u"Estimated prior skill")
        plt.savefig(directory+'prior_skill_histogram.svg', bbox_inches='tight')
        plt.close()