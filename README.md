### About
mapViz is a Python tool for data analysis, map drawing and graph drawing. It uses data obtained from users learning geography through interactive system available on slepemapy.cz. Each class has specific role:

* Importer is responsible for loading and parsing csv into pandas DataFrame
* Analysis is used for general calculations on DataFrames, most of the methods return pandas Series objects
* Map is responsible for drawing choropleth maps in .svg format through kartograph. It has separate methods for drawing, legend, title, classification methods etc.
* Graph class is used for drawing graphs
* Every classes' frame is customizable, so that you can create your own frame and pass it on to these classes to draw/do more analysis on them.

### Requirements
All of the requirements are listed in requirements.txt. Some of them (namely [GDAL](http://www.gdal.org), [kartograph](http://kartograph.org/docs/kartograph.py/)) will probably not install automatically through pip. 

You will also need the csv user data, csv with country codes (included in [/base/](../blob/master/base/areas.csv)) and shapefile data for map regions. These shapefiles are available on [Natural Earth Data](http://www.naturalearthdata.com/) (world map included in [/base/](../blob/master/base/ne_110m_admin_1_countries)).

### Usage example
I want to draw a map for specific user\_id with my own binning\_function and my own number of bins (5)

Parsing phase:

* input = Importer()
* codes = input.load\_general\_csv(path\_to\_areas\_csv)
* csv = input.load\_geo\_csv(path\_to\_user\_data\_csv)

Map drawing phase:

* m = Map(output\_path,csv,codes,**user=user_id**) #create map object
* m.number\_of\_answers(binning\_function=**binning\_function**,number\_of\_bins=**5**)

There are also few examples of usage for predefined maps and graphs included in main.py