### About
SlepemapyAnalysis is a Python tool used for data analysis, map and graph visualisations. It uses data obtained from users learning geography through adaptive system available on [Slepemapy](http://www.slepemapy.cz). Each class has specific role:

------

### Requirements
All of the requirements are listed in requirements.txt. Some of them (namely [GDAL](https://pypi.python.org/pypi/GDAL/), [kartograph](http://kartograph.org/docs/kartograph.py/)) will probably not install automatically through pip. 

You will also need the geography.answer.csv, [geography.places.csv](../master/data/geography.places.csv) and [shapefile](../master/data/ne_110m_admin_1_countries) data for map regions. These shapefiles are originally from [Natural Earth Data](http://www.naturalearthdata.com/).

------

### Usage example
There are 3 types of filtering: by user, by place, global. Then there are also 2 types of visualisations - maps and graphs. You can combine those to generate predefined graphs/maps by call from commandline:
python [graphs/maps]-[user/place/global].py -i <id1> <id2> ... <idn>

So for example, if you want to generate graphs for 5 specific users, you can run from commandline:
python graphs-user.py -i 10 25 2277 96 156

Those generators expect you have: geography.answer.csv and [geography.places.csv](../master/data/geography.places.csv).

#### For much more customization and analysis read the [documentation](../master/docs/index.html)