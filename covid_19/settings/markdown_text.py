JHCCU_TITLE = """
# Interactive visualization of covid-19 progression
"""

JHCCU_INFO_TEXT = """
## About
The [data](https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv) is pulled from Johns Hopkins University's [GitHub-Repositors](https://github.com/CSSEGISandData/COVID-19) and visualized using [Dash](https://dash.plotly.com/) which is a Python Wrapper/Framework for [Flask](https://flask.palletsprojects.com/), [Plotly.js](https://plotly.com/) and [React.js](https://reactjs.org/)
This is an extension to my original [Jupyter-Notebook](https://github.com/jmacenka/jupyternotebook_covid_19_visualization/blob/master/analysis_of_the_covid_19_course.ipynb) based analysis. The [source code for this WebApp](https://github.com/jmacenka/dash-covid-19-visualization) can also be found on Github.

Primarily I built this app for myself but feel free to use. Its not the most beautiful but for 800 lies of code its quite ok I think ;-)

Have fun exploring the data with views you control.

## View options
#### Data
cases => The total cumulative number of cases as reported in the Johns Hopkins Data-Set.

cases normalized => Numer of cases divided by the respective countries population.

daily cases => The numer of cases reportet for each day, effectively the time-derivative of #cases.

daily cases normalized => Numer of daily cases divided by the respective contries population.

growth rate => The percentage change of the #cases based on the previous day. Not exactly the R-number but verry similar.

#### Scale
You can either use linear or logarithmic scale.

#### Moving average
To flatten peaks in the figures, you can apply a moving average filter for up to 7 days. Bear in mind that this will blur the data into later days. A moving average of 1 is equal to no moving average. 

### Get in contact
Have a comment or feature request?

Shoot me an email to [corona.macenka.de@gmx.net](mailto:corona.macenka.de@gmx.net). I will look every now and then.

or

Write a feature request on [the projects GitHub-page](https://github.com/jmacenka/dash-covid-19-visualization/issues)
"""