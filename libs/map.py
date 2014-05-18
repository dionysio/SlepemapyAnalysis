# -*- coding: utf-8 -*-

from drawable import Drawable
import analysis_per_place
from classification_methods import Jenks

from pandas import Series, cut
import colorbrewer
from kartograph import Kartograph
from StringIO import StringIO


class MapFile(StringIO):
    '''Dummy subclass of StringIO used for map drawing. Kartograph closes file after drawing map, which is not good. Other drawing methods (title, legend) would have to open the file with map every time. So instead there is this class, that does not close and is passed along to other drawing methods and closed then.
    '''
    def __init__(self):
        StringIO.__init__(self)
    
    def close(self):
        pass

    def real_close(self):
        '''Does exactly same thing as origial close() method
        '''

        if not self.closed:
            self.closed = True
            del self.buf, self.pos


class Map(Drawable):
    def __init__(self, path, frame, prior, codes, config, users=[], places=[]):
        """Draws world map by default. All other defaults are same as in Drawable.
        
        :param config: configuration of kartograph
        """

        Drawable.__init__(self,path, frame, prior, codes, users, places)
        self.config = config
        self._k = Kartograph()


    def draw_map(self, frame, directory, title='', classification_method = None, number_of_bins = 6, 
                colour_range = "YlOrRd", additional_places=None, additional_bins=None):
        """General drawing method through kartograph.

        :param directory: output directory
        :param title: name of map
        :param classification_method: which function to use for binning -- default is None (-> jenks_classification)
        :param colour_range: colorbrewer colour range -- default is "YlOrRd"
        :param number_of_bins: how many bins to divide data-- default is 6
        :param additional_places: whether to add additional places AFTER binning -- default is None
        :param additional_bins: whether to add additional labels AFTER calculations -- default is []
        """


        if classification_method is None:
            classification_method = Jenks()
        (places, legend) = self.bin_data(frame, classification_method, number_of_bins, colour_range, additional_places, additional_bins)

        svg = MapFile()
        self._k.generate(self.config, outfile=svg, format='svg', stylesheet=self.generate_css(places))
        if legend is not None:
            self.draw_legend(legend, svg)
        if title:
            self.draw_title(title, svg)
        with open(directory,'w') as out:
            out.write(svg.getvalue().encode('utf8'))
        svg.real_close()


    def bin_data(self, frame, classification_method, number_of_bins, colour_range,
            additional_places=None, additional_bins=None):
        """Combines classification methods with colouring, returns binned data with assigned colours

        :param frame: values to bin (expects Series)
        :param classification_method: which function to use for binning -- default is None (-> jenks_classification)
        :param number_of_bins: how many bins to divide data-- default is 6
        :param additional_places: whether to add additional places AFTER binning -- default is None
        :param additional_bins: whether to add additional labels AFTER calculations -- default is None
        :param colour_range: colorbrewer colour range

        :returns:  (places, bins) -- places is Series with place_asked IDs and it is used for coloring in places. Bins is Series that is used as legend, it has legend label and color
        """

        bins = classification_method.classify(frame.tolist(),number_of_bins)
        bins = list(set(bins)) #drop duplicate bins
        bins.sort()
        if colour_range == 'RdYlGn':
            colours = colorbrewer.RdYlGn[len(bins)-1] #Red, Yellow, Green
        else:
            colours = colorbrewer.YlOrRd[len(bins)-1] #Yellow, Orange, Red
        colours = ['\'rgb('+str(i[0])+', '+str(i[1])+', '+str(i[2])+')\'' for i in colours]

        places = Series(cut(frame,bins=bins, labels=colours, include_lowest=True, right= True),index=frame.index,name='colour')
        places = self.codes[['code','id']].join(places, on='id', how='right')
        places = places.set_index('code')['colour']
        places = places.append(additional_places).dropna()
        places.name = 'colour'

        bins = Series(colours,index=cut(frame, bins=bins, include_lowest=True, right= True).levels, name='colour')
        bins = bins.append(Series(['\'rgb(255, 255, 255)\''],['No data'])) #white for No data bin
        bins = bins.append(additional_bins)

        return (places, bins)


    @staticmethod
    def generate_css(frame, optional_css=''):
        """Generates css for coloring in places.

        :param frame: Series with place_asked IDs as indices and colours as values
        :param optional_css: append additional css at the end of the calculated css-- default is ''
        """

        data = frame.reset_index()
        data.columns = ['code','colour']
        css = ['']
        def assign(x):
            css[0] += '.states[iso_a2='+x['code']+']'+'{\n\tfill: '+x['colour']+';\n}\n'
        data.apply(assign,axis=1)
        if optional_css:
            with open(optional_css,'r') as optional:
                css[0] += optional.read()
        return css[0]


    @staticmethod
    def draw_legend(legend, svg, xy=('5','175'), bin_width=15, font_size='12'):
        """Draws legend into map. 

        :param legend: Series with labels as indices and colors ('\'rgb(0, 255, 255)\'') as values
        :param x,y: starting x,y position of the legend
        :param bin_width: width of each individual bin -- default is 15
        :param font_size: font size of labels -- default is 12
        """

        svg.seek(-6,2) #skip to the position right before </svg> tag
        svg.write('\n<g transform = \"translate('+xy[0]+' '+xy[1]+')\">\n') #group
        data = legend.reset_index()
        i=[0] #really ugly hack to get around UnboundLocalError inside of _draw_bin

        def _draw_bin(x):
            svg.write(  '<rect x=\"0\" y=\"'+str((i[0]+1)*bin_width)+
                        '\" width=\"'+str(bin_width)+'\" height=\"'+str(bin_width)+
                        '" fill='+x[0]+ '/>\n')
            svg.write(  '<text x=\"20\" y=\"'+str((i[0]+1)*bin_width+11)+
                        '\" stroke=\"none\" fill=\"black\" font-size=\"'+font_size+
                        '" font-family=\"sans-serif\">'+x['index']+'</text>\n')
            i[0]+=1

        data.apply(_draw_bin, axis=1)
        svg.write('</g>\n</svg>') #group


    @staticmethod
    def draw_title(title, svg, xy=('400','410'),font_size='20',colour='black'):
        """Draws title into svg map.

        :param title: text do input into picture
        :param x,y: starting x,y position of the title -- default is ('400','410')
        :param font_size: font size of labels -- default is 20
        :param colour: title colour
        """

        svg.seek(-6,2)
        svg.write(  '\n<text x =\"'+xy[0]+'\" y=\"'+xy[1]+'\" stroke=\"none\" font-size=\"'+
                    font_size+'\" fill=\"'+colour+'\" font-family=\"sans-serif\">'+
                    title+'</text>\n</svg>')


    ############################################################################


    def mistaken_places(self,directory=''):
        """ Draws map of most mistaken places for one specific places.

        :param directory: output directory -- default is '' (./maps/)
        """

        if not directory:
            directory = self.current_directory+'/maps/'
        data = analysis_per_place.mistaken_places(self.frame)
        if not (data[0].empty or self.places[0] is None):
            self.draw_map(data[0], directory+'mistaken_places.svg', 
            'Places mistaken for '+self.get_country_name(self.places[0])+' out of '+str(data[1])+' answers',
            additional_places=Series(['\'rgb(0, 255, 255)\''],[self.get_country_code(self.places[0])]), 
            additional_bins=Series(['\'rgb(0, 255, 255)\''],[self.get_country_name(self.places[0])]))


    def number_of_answers(self, directory=''):
        """Draws map of total number of answers per country.

        :param directory: output directory -- default is '' (./maps/)
        """

        if not directory:
            directory = self.current_directory+'/maps/'
        data = analysis_per_place.number_of_answers(self.frame)
        if not data.empty:
            self.draw_map(data, directory+'number_of_answers.svg','Number of answers')


    def response_time(self, directory=''):
        """Draws map of mean response time per country.

        :param directory: output directory -- default is '' (./maps/)
        """

        if not directory:
            directory = self.current_directory+'/maps/'
        data = analysis_per_place.response_time(self.frame)
        if not data.empty:
            self.draw_map(data, directory+'response_time.svg','Response time')
        


    def prior_knowledge(self, directory=''):
        """Draws map of prior knowledge.

        :param directory: output directory -- default is '' (./maps/)
        """

        if not directory:
            directory = self.current_directory+'/maps/'

        if self.places:
            d = {i: j[0] for i, j in self.prior[0].items() if i in range(self.places[0],self.places[-1])}
        data = analysis_per_place.prior_knowledge(d)
        if not data.empty:
            self.draw_map(data, directory+'prior_knowledge.svg','Average prior knowledge',colour_range="RdYlGn")


    def average_current_knowledge(self,directory='',classification_method=None,number_of_bins=6):
        """Draws map of user knowledge.

        :param directory: output directory -- default is '' (./maps/)
        """

        if not directory:
            directory = self.current_directory+'/maps/'
        data = analysis_per_place.average_current_knowledge(self.frame,self.prior[0])
        if not data.empty:
            self.draw_map(data, directory+'average_current_knowledge.svg','Average current knowledge ',colour_range="RdYlGn")


    def success(self,directory='',classification_method=None,number_of_bins=6):
        """Draws map of mean success rate per country.

        :param directory: output directory -- default is '' (./maps/)
        """

        if not directory:
            directory = self.current_directory+'/maps/'
        data = analysis_per_place.success(self.frame)
        if not data.empty:
             self.draw_map(data, directory+'success.svg','Success rate',colour_range="RdYlGn")


class WorldMap(Map):
    def __init__(self, path, frame, prior, codes, users=[], places= range(51,225)+[234,235]):
        config ={
            "layers": {
                "states": {
                    "src": path+"/data/ne_110m_admin_1_countries/ne_110m_admin_0_countries.shp",
                    "filter": ["continent", "in", ["Europe","Asia","Africa","South America","Oceania","North America"]],
                    "class": "states"
                }
            }
        }
        Map.__init__(self,path, frame, prior, codes, config, users, places)