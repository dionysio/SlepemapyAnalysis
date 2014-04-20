# -*- coding: utf-8 -*-

from drawable import Drawable
import analysis_per_country
from classification_methods import Jenks

from pandas import DataFrame, cut
import colorbrewer
from codecs import open as copen
from kartograph import Kartograph


class Map(Drawable):

    def __init__(self, path='', df=None, user=None, place_asked=None, prior = None, codes=None, bounds = (50,236)):
        """Draws world map by default. All other defaults are same as in Drawable.
        
        :param codes: basically geography.places.csv, it has information about codes of countries defined by ISO_3166-1_alpha-2 -- default None -- default None
        """

        if not df.empty:
            df = df[(df.place_asked>=bounds[0]) & (df.place_answered<=bounds[1])]
        Drawable.__init__(self,path,df,user,place_asked,prior,codes)

        config ={
            "layers": {
                "states": {
                    "src": self.current_directory+"/data/ne_110m_admin_1_countries/ne_110m_admin_0_countries.shp",
                    "filter": ["continent", "in", ["Europe","Asia","Africa","South America","Oceania","North America"]],
                    "class": "states"
                }
            }
        }

        self.bounds = bounds
        self.set_config(config)
        self._k = Kartograph()


    def set_config(self,config):
        self.config = config

    @staticmethod
    def bin_data(data,classification_method=None,number_of_bins=6,
            additional_countries=None,additional_labels=[],colour_range="YlOrRd"):
        """Combines classification methods with colouring, returns binned data with assigned colours

        :param data: values to bin
        :param classification_method: which function to use for binning -- default is None (-> jenks_classification)
        :param number_of_bins: how many bins to divide data-- default is 6
        :param reverse_colours: whether to reverse generated color scheme
        :param additional_countries: whether to add additional countries AFTER binning -- default is None
        :param additional_labels: whether to add additional labels AFTER calculations -- default is []
        :param colours: use these colours instead of predefined ones

        """

        if classification_method is None:
            classification_method = Jenks()
        binned = DataFrame(data)
        binned = binned.reset_index()
        binned.columns=['country','counts']

        bins = classification_method.classify(binned['counts'],number_of_bins)
        binned['bin'] = cut(binned['counts'], bins=bins,labels=False)

        if colour_range == 'RdYlGn':
            colours = colorbrewer.RdYlGn[len(bins)-1] #Red, Yellow, Green
        else:
            colours = colorbrewer.YlOrRd[len(bins)-1] #Yellow, Orange, Red

        binned['rgb'] = binned.bin.apply(lambda x: colours[x])
        binned = binned.append(additional_countries)

        colours = list(reversed(colours))
        colours = DataFrame(zip(colours))
        if additional_countries is not None:
            colours = colours.append([[additional_countries.rgb.values[0]]],ignore_index=True)
        colours = colours.append([[(255,255,255)]],ignore_index=True) #white for No data bin
        colours.columns = ['rgb']
        colours['label'] = Map.bins_to_string(bins)+additional_labels+['No data']
        return (binned,colours)


    @staticmethod
    def bins_to_string(bins):
        """ Returns list of strings from the bins in the interval form: (lower,upper]

        :param bins: bins to get strings from
        """

        bins[0]+=1 #corrections for bins
        bins[-1]-=1
        bins = [round(x,2) for x in bins]
        labels = ['('+str(bins[curr])+', '+str(bins[curr+1])+']' for curr in range(len(bins)-1)]
        labels.reverse()
        return labels


    def generate_css(self,data,path,optional_css=''):
        """Generates css for coloring in countries.

        :param data: df with columns [country,rgb], where country is an ID and rgb are colour values
        :param path: output directory
        :param optional_css: append additional css at the end of the calculated css-- default is ''
        """

        with open(path,'w+') as css:
            if not data.empty:
                for index,row in data.iterrows():
                    code = self.get_country_code(row.country).upper()
                    colour = self.colour_value_rgb_string(row.rgb[0],row.rgb[1],row.rgb[2])
                    if code and colour:
                        css.write('.states[iso_a2='+code+']'+'{\n\tfill: '+colour+';\n}\n')
            if optional_css:
                with open(optional_css,'r') as optional:
                    css.write(optional.read())


    @staticmethod
    def colour_value_rgb_string(r,g,b):
        """Returns string in format 'rgb(r,g,b)'.
        """

        return '\'rgb('+str(r)+', '+str(g)+', '+str(b)+')\''


    @staticmethod
    def draw_bins(data,path,xy=(5,175),bin_width=15,font_size=12):
        """Draws bins into svg.

        :param data: data with columns [label,r,g,b] where label is text next to the bin and rgb are colour values
        :param path: path to svg
        :param x: starting x position of the legend
        :param y: starting y position of the legend
        :param bin_width: width of each individual bin -- default is 15
        :param font_size: font size of labels -- default is 12
        """

        with copen(path,'r+','utf-8') as svg:
            svg.seek(-6,2) #skip to the position right before </svg> tag
            svg.write('\n<g transform = \"translate('+str(xy[0])+' '+str(xy[1])+')\">\n') #group
            for i in range(len(data)):
                svg.write(  '<rect x=\"0\" y=\"'+str((i+1)*bin_width)+
                            '\" width=\"'+str(bin_width)+'\" height=\"'+str(bin_width)+
                            '" fill='+Map.colour_value_rgb_string(data.rgb.values[i][0],data.rgb.values[i][1],data.rgb.values[i][2])+ '/>\n')
                svg.write(  '<text x=\"20\" y=\"'+str((i+1)*bin_width+11)+
                            '\" stroke=\"none\" fill=\"black\" font-size=\"'+str(font_size)+
                            '" font-family=\"sans-serif\">'+data.label.values[i]+'</text>\n')
            svg.write('</g>\n</svg>') #group


    @staticmethod
    def draw_title(path,title='',xy=(400,410),font_size=20,colour='black'):
        """Draws title into svg.

        :param path: path to svg
        :param title: text do input into picture
        :param x: starting x position of the title
        :param y: starting y position of the title
        :param font_size: font size of labels -- default is 20
        :param colour: title colour
        """

        with copen(path,'r+','utf-8') as svg:
            svg.seek(-6,2)
            svg.write(  '\n<text x =\"'+str(xy[0])+'\" y=\"'+str(xy[1])+'\" stroke=\"none\" font-size=\"'+
                        str(font_size)+'\" fill=\"'+colour+'\" font-family=\"sans-serif\">'+
                        title+'</text>\n</svg>')


    def draw_map(self,path,title='',colours=None):
        """General drawing method through kartograph. Looks for css in current_directory+'/style.css' for styling css.

        :param path: output directory
        :param title: name of map
        :param colours: dataframe with colours for bins -- default is None
        """

        with open(self.current_directory+'/data/style.css') as css:
            self._k.generate(self.config,outfile=path,stylesheet=css.read())
        if colours is not None:
            self.draw_bins(colours,path)
        if title:
            self.draw_title(path,title)

    ############################################################################


    def mistaken_countries(self,path='',classification_method=None,number_of_bins=6):
        """ Draws map of most mistaken countries for this specific one

        :param classification_method: which function to use for binning -- default is None (-> jenks_classification)
        :param path: output directory -- default is '' (current dir)
        :param number_of_bins: how many bins to divide data into-- default is 6
        """

        if not path:
            path = self.current_directory+'/maps/'

        data = analysis_per_country.mistaken_countries(self.frame)
        colours = None
        if not (data.empty or self.place_asked is None):
            place = DataFrame([[self.place_asked,(0,255,255)]],columns=['country','rgb'])
            (data,colours) = self.bin_data(data,classification_method,number_of_bins,additional_countries=place,additional_labels=[self.get_country_name(self.place_asked)])
            self.generate_css(data[['country','rgb']],path=self.current_directory+'/data/style.css')

        self.draw_map(path+'mistaken_countries.svg','Countries mistaken for '+self.get_country_name(self.place_asked),colours)


    def number_of_answers(self,path='',classification_method=None,number_of_bins=6):
        """Draws map of total number of answers per country.

        :param classification_method: which function to use for binning -- default is None (-> jenks_classification)
        :param path: output directory -- default is '' (current dir)
        :param number_of_bins: how many bins to divide data into-- default is 6
        """

        if not path:
            path = self.current_directory+'/maps/'

        data = analysis_per_country.number_of_answers(self.frame)
        colours = None
        if not data.empty:
            (data,colours) = self.bin_data(data,classification_method,number_of_bins)
            self.generate_css(data[['country','rgb']],path=self.current_directory+'/data/style.css')

        self.draw_map(path+'number_of_answers.svg','Number of answers',colours)


    def response_time(self,path='',classification_method=None,number_of_bins=6):
        """Draws map of mean response time per country.

        :param classification_method: which function to use for binning -- default is None (-> jenks_classification)
        :param path: output directory -- default is '' (current dir)
        :param number_of_bins: how many bins to divide data into-- default is 6
        """

        if not path:
            path = self.current_directory+'/maps/'

        data = analysis_per_country.response_time(self.frame)
        colours = None
        if not data.empty:
            (data,colours) = self.bin_data(data,classification_method,number_of_bins)
            self.generate_css(data[['country','rgb']],path=self.current_directory+'/data/style.css')

        self.draw_map(path+'response_time.svg','Response time',colours)


    def average_knowledge(self,path='',classification_method=None,number_of_bins=6):
        """Draws map of total number of answers per country.

        :param classification_method: which function to use for binning -- default is None (-> jenks_classification)
        :param path: output directory -- default is '' (current dir)
        :param number_of_bins: how many bins to divide data into-- default is 6
        """

        if not path:
            path = self.current_directory+'/maps/'
        data = analysis_per_country.average_knowledge(self.prior)[self.bounds[0]:self.bounds[1]] #filter only for world countries
        colours = None

        if not data.empty:
            (data,colours) = self.bin_data(data,classification_method,number_of_bins,colour_range="RdYlGn")
            self.generate_css(data[['country','rgb']],path=self.current_directory+'/data/style.css')

        self.draw_map(path+'average_knowledge.svg','Average knowledge',colours)


    def knowledge(self,path='',classification_method=None,number_of_bins=6):
        """Draws map of user knowledge.

        :param classification_method: which function to use for binning -- default is None (-> jenks_classification)
        :param path: output directory -- default is '' (current dir)
        :param number_of_bins: how many bins to divide data into-- default is 6
        """

        if not path:
            path = self.current_directory+'/maps/'
        data = analysis_per_country.knowledge(self.frame,self.prior)
        colours = None

        if not data.empty:
            (data,colours) = self.bin_data(data,classification_method,number_of_bins,colour_range="RdYlGn")
            self.generate_css(data[['country','rgb']],path=self.current_directory+'/data/style.css')

        self.draw_map(path+'knowledge.svg','Knowledge ',colours)


    def success(self,path='',classification_method=None,number_of_bins=6):
        """Draws map of mean success rate per country.

        :param classification_method: which function to use for binning -- default is None (-> jenks_classification)
        :param path: output directory -- default is '' (current dir)
        :param number_of_bins: how many bins to divide data into-- default is 6
        """

        if not path:
            path = self.current_directory+'/maps/'
        data = analysis_per_country.success(self.frame)
        colours = None

        if not data.empty:
            (data,colours) = self.bin_data(data,classification_method,number_of_bins,colour_range="RdYlGn")
            self.generate_css(data[['country','rgb']],path=self.current_directory+'/data/style.css')

        self.draw_map(path+'success.svg','Success',colours)