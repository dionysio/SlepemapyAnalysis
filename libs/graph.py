# -*- coding: utf-8 -*-

from drawable import Drawable
import analysis_per_country
import analysis_per_time
import analysis_per_session
from common import colour_range, logis

from numpy import arange, ceil, log
import matplotlib.pyplot as plt
from matplotlib import interactive
from matplotlib import rc
import colorbrewer
from os import path, makedirs

class Graph(Drawable):
    def __init__(self, path='', df=None, user=None, place_asked=None, prior=None, codes= None):
        """Sets matplotlib to be non-interactive and default font to Times New Roman. All other defaults are same as in Drawable.
        """

        Drawable.__init__(self, path, df, user, place_asked, prior, codes)
        interactive(False) #disable matplotlib interactivity
        rc('font', **{'sans-serif' : 'Times New Roman','family' : 'sans-serif'})


    def _plot_group(self, data, ax, colour, marker):
        """Plots data.result over data.session_number on prepared ax
        
        :param data: what to plot
        :param ax: where to plot
        :param colour: colour of curve
        :param marker: marker of points on curve
        """

        name = self.get_label(data.name[0], data.name[1])
        return ax.plot(data['session_number'],data['result'],color=colour,marker=marker, label=name)


    def _plot_separated_group(self, data, output, name):
        """Plots group (data.result over data.session_number) in separated graph with labels, second axis and legend.
        
        :param data: what to plot
        :param output: output directory
        :param name: label name for Y axis (result)
        """

        if len(data)>1:
            fig, ax = plt.subplots()
            ax.set_xlabel('Session number')
            ax.set_ylabel(name, color='cyan')
            l1 = self._plot_second_axis(data, ax)
            l2 = self._plot_group(data, ax, 'cyan', 'o')
            lines = l1+l2
            labels = [l.get_label() for l in lines]
            plt.legend(lines, labels, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
            plt.savefig(output+labels[1]+'.svg', bbox_inches='tight')
            plt.close()


    def _plot_second_axis(self, data, first_ax, name='Log of count'):
        """Plots second axis of log of data.counts over data.session_number. Uses symlog for yscale
        
        :param data: what to plot
        :param first_ax: where to plot
        :param name: label name for second Y axis (data.counts) -- default is 'Log of count'
        """

        ax = first_ax.twinx()
        ax.set_ylabel(name, color='red')
        ax.set_yscale('symlog')
        return ax.plot(data['session_number'], log(data['counts']), color = 'red', linestyle='--', label='Count')


    def response_time(self, directory=''):
        if not directory:
            directory = self.current_directory+'/graphs/'
        data = analysis_per_session.average_response_time(self.frame)
        if not data.empty:
            fig, ax = plt.subplots()
            data = data.reset_index()
            ax.plot(data.session_number, data.incorrect, color = 'red', label='Incorrect')
            ax.plot(data.session_number, data.correct, color = 'green', label='Correct')
            ax.set_yscale('symlog')

            self._plot_second_axis(data, ax)
            ax.set_title(u"Progress of mean response times over sessions")
            ax.set_xlabel('Session number')
            ax.set_ylabel('Mean log of response times')
            plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
            plt.savefig(directory+'response_time.svg', bbox_inches='tight')
            plt.close()


    def skill(self, directory='', plot_individual_graphs = True):
        """Draws graph of mean skill per session.

        :param directory: output directory -- default is '' (current_directory)
        :param plot_individual_graphs: whether to also draw separated graphs for each curve -- default is True
        """

        if not directory:
            directory = self.current_directory+'/graphs/'
        data = analysis_per_session.average_skill(self.frame,self.prior[0],self.codes)
        data.result = data.result.apply(logis)
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
                data.apply(lambda x: self._plot_separated_group(x, directory+'skill_separated/','Skill'))


    def success_over_session(self,directory='', plot_individual_graphs=True):
        """Draws graph of mean success per session.

        :param directory: output directory -- default is '' (current_directory)
        :param plot_individual_graphs: whether to also draw separated graphs for each curve -- default is True
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
                data.apply(lambda x: self._plot_separated_group(x, directory+'success_separated/','Success'))
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

            data = data.reset_index()
            ax.bar(range(len(data)),data.result, color="cyan")
            self._plot_second_axis(data, ax)
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


    def number_of_users_over_session(self, directory=''):
        """Draws graph of number of answers per session.

        :param threshold: how many sessions to plot
        :param directory: -- default is '' (current_directory)
        """

        if not directory:
            directory = self.current_directory+'/graphs/'
        data = analysis_per_session.number_of_users(self.frame)
        if not data.empty:
            fig, ax = plt.subplots()

            ax.bar(range(len(data)),data.values, color="cyan")
            ax.set_title(u"Number of users over sessions")
            ax.set_ylabel(u"Number of users")
            ax.set_xlabel(u"Session number")

            plt.savefig(directory+'number_of_users_over_session.svg', bbox_inches='tight')
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
        """Draws graph of mean success rate over time.

        :param directory: output directory -- default is '' (current_directory)
        :param frequency: describes over what time period to sample, use only 'M'/'W'/'D'!
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
        """Draws graph of mean number of answers over time.

        :param directory: output directory -- default is '' (current_directory)
        :param frequency: describes over what time period to sample, use only 'M'/'W'/'D'!
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


    def number_of_users_over_time(self, directory ='', frequency = 'M'):
        """Draws graph of number of users over time

        :param frequency: describes over what time period to sample, use only 'M'/'W'/'D'!
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

            plt.savefig(directory+'number_of_users_over_time.svg', bbox_inches='tight')
            plt.close()


################################################################################


    def answer_portions(self, directory='', threshold=0.01):
        """Draws pie chart of portions of answers to specific country.

        :param threshold: limit of values to include as separate slice
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
        """Draws histogram of difficulties. 

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
        """Draws graph of prior skill.

        :param directory: output directory -- default is '' (current_directory)
        """

        if not directory:
            directory = self.current_directory+'/graphs/'
        fig, ax = plt.subplots()
        items = [logis(item[0]) for item in self.prior[1].itervalues()]
        ax.hist(items)
        ax.set_title(u"Histogram of prior skill ")
        ax.set_ylabel(u"Number of users")
        ax.set_xlabel(u"Estimated prior skill")
        plt.savefig(directory+'prior_skill_histogram.svg', bbox_inches='tight')
        plt.close()


    def difficulty_response_time(self, directory=''):
        """Draws plot of mean response time for correct/incorrect answers over difficulties

        :param directory: output directory -- default is '' (current_directory)
        """

        if not directory:
            directory = self.current_directory+'/graphs/'
        data = analysis_per_country.difficulty_response_time(self.frame, self.prior[0])

        if not data.empty:
            fig, ax = plt.subplots()

            ax.plot(data.difficulty, log(data.correct), color='green', label='Correct')
            ax.plot(data.difficulty, log(data.incorrect), color='red', label='Incorrect')
            ax.set_yscale('symlog')
            ax.set_title(u"Mean response times of correct/incorrect answers for different difficulties")
            ax.set_xlabel(u"Difficulty")
            ax.set_ylabel(u"Log of mean response time [ms]")
            plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

            plt.savefig(directory+'difficulty_response_time.svg', bbox_inches='tight')
            plt.close()