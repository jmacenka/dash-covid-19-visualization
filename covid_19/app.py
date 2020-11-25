# Import modules from main framework
import dash, dash_table, os
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State

# Import helper modules
import requests, base64, io
import pandas as pd
from flask import Flask
from datetime import datetime
from random import randint

# Import custom modules
from settings import INITIAL_COUNTRIES, GRAPH_SCALE_OPTIONS, DATE_FORMAT, EXTERNAL_STYLESHEETS
from settings.markdown_text import JHCCU_TITLE, JHCCU_INFO_TEXT
from pandemic_models.sir_model import SIR
from data_api.apis import get_population_by_country_dict, generate_dataframes_dict

# Server serttings
FRAMEWORK_STYLESHEETS = [
    dbc.themes.GRID,
    # dbc.themes.MATERIA,
    dbc.themes.BOOTSTRAP,
]

# Server initialization
server = Flask(__name__)
server.secret_key = os.environ.get('COVID_APP_SECRET_KEY', str(randint(0, 100000000000)))
app = dash.Dash(__name__, external_stylesheets=FRAMEWORK_STYLESHEETS+EXTERNAL_STYLESHEETS,include_assets_files=True, server=server)
app.title = 'covid-19 Dashboard by Jan Macenka'
app.css.config.serve_locally = True

# Helper Functions
def index_to_date(date_list,n_index):
    return date_list[n_index].strftime(DATE_FORMAT)

def get_slider_marks(dates_list,num_marks=15):
    mark_stepsize = len(dates_list) // num_marks
    dates = {}
    for idx, date in enumerate(dates_list):
        if date.day == 1 or idx == 0:
            dates[idx]={
                'label':date.strftime('%b'),
                'style':{'font-weight': 'bold','size':'5px', 'transform': 'rotate(70deg)'},
            }
        elif date.day % mark_stepsize == 0:
            dates[idx]=str(date.day)
        else:
            dates[idx] = ''
    return dates

def get_country_data_df(data_selection_value:str, data_evaluation_value:str, country:str, range_slider_value:list):
    return dfs[data_selection_value][data_evaluation_value]['data'][country][range_slider_value[0] : range_slider_value[-1]]

def build_graph(country_selection_value, range_slider_value, yaxis_data_selection_value, xaxis_data_selection_value, yaxis_data_evaluation_value, xaxis_data_evaluation_value, yaxis_type_value, xaxis_type_value, yaxis_averaging_days, xaxis_averaging_days, data=None, *args, **kwargs):
    data = []
    if not country_selection_value:
        return None
    for country in country_selection_value:
        y = get_country_data_df(yaxis_data_selection_value, yaxis_data_evaluation_value, country, range_slider_value)
        x = get_country_data_df(xaxis_data_selection_value, xaxis_data_evaluation_value, country, range_slider_value)
        y_unit = dfs[yaxis_data_selection_value][yaxis_data_evaluation_value]['unit']
        x_unit = dfs[xaxis_data_selection_value][xaxis_data_evaluation_value]['unit']
        yaxis_type = 'lin'
        xaxis_type = 'lin'
        yaxis_title = str(yaxis_data_selection_value)
        xaxis_title = str(xaxis_data_selection_value)
        if yaxis_data_selection_value != 'time':
            y = y.rolling(yaxis_averaging_days).mean()
            yaxis_type = yaxis_type_value
            if yaxis_averaging_days > 1:
                yaxis_title += f' with moving average of {yaxis_averaging_days} days'
        if xaxis_data_selection_value != 'time':
            x = x.rolling(xaxis_averaging_days).mean()
            xaxis_type = xaxis_type_value
            if xaxis_averaging_days > 1:
                xaxis_title += f' with moving average of {xaxis_averaging_days} days'
        yaxis_title += f'<br>[{y_unit}]'
        xaxis_title += f'<br>[{x_unit}]'    
        
        data.append(dict(
            x=x,
            y=y,
            text=country_selection_value,
            mode='line',
            opacity=.7,
            marker={
                'size':15,
                'line': {'width':.5}
            },
            name=country,
        ))
    graph = dcc.Graph(
        id='covid-graph',
        className='spaced',
        figure = {
            'data': data,
            'layout': dict(
                xaxis={'title':xaxis_title, 'type':xaxis_type},
                yaxis={'title':yaxis_title, 'type':yaxis_type},
                padding={'l':40,'b':40,'t':70,'r':10, 'pad':10},
                legend={'x':0,'y':1},
                title=f'{yaxis_data_selection_value} ({GRAPH_SCALE_OPTIONS[yaxis_type].lower()}) vs {xaxis_data_selection_value.lower()} ({GRAPH_SCALE_OPTIONS[xaxis_type].lower()})',
                hovermode='closest',
            ),
        }
    )
    return graph

global list_of_avaliable_countries, evaluation_options, list_of_available_dates, dfs, country_population_dict
list_of_avaliable_countries, evaluation_options, list_of_available_dates, dfs = generate_dataframes_dict()
country_population_dict = get_population_by_country_dict()

app.layout = dbc.Jumbotron(
    id='root',
    className='container my-5',
    children = [
        dcc.Location(id='url', refresh=False),        
        html.Div(
            id='header-information',
            className='text-center',
            style={'textAlign': 'center',},
            children=[
                html.H1(
                    children=[
                        "Interactive visualization of covid-19 progression",
                    ],
                ),
                html.H3(
                    # className='text-warning',
                    children=[
                    "with data from Johns Hopkins University",
                    ],
                ),
                dbc.Button(
                    id='open-info-modal',
                    className='btn-primary',
                    children=[
                        "About this App"
                    ]
                ),                
                dbc.Modal(
                    id='info-modal',
                    size='xl',
                    children=[
                        dbc.ModalHeader(
                            className='text-center',
                            children=[
                                dcc.Markdown(
                                    children=JHCCU_TITLE,
                                ),
                            ],    
                        ),
                        dbc.ModalBody(
                            children=[
                                dcc.Markdown(JHCCU_INFO_TEXT),
                            ]
                        ),
                        dbc.ModalFooter(
                            className='text-right',
                            children=[
                                html.Blockquote(
                                    html.Cite('created by Jan Macenka',)
                                ),
                                dbc.Button("Close", id="close-info-modal", className="ml-auto"),
                            ]
                        ),
                    ],
                ),
                html.Hr(
                    className="my-2"
                ),
            ],
        ),
        dcc.Tab(
            id='data-visualization-tab',
            label='Data-Visualization',
            children=[
                dbc.Row(
                    className='my-2',
                    children=[
                        dbc.Col(
                            id='yaxis-settings-col',
                            children=[
                                html.H3(
                                    className='centered p-2',
                                    children='Y-axis',
                                ),
                                dbc.Card(
                                    className='border-5 rounded py-2 m-2 bg-light',
                                    children= [        
                                        html.P(
                                            className='centered text-muted pt-2',
                                            children='data',
                                        ),                                                                 
                                        dbc.RadioItems(
                                            id="yaxis-data-selection",
                                            value= list(dfs.keys())[0],
                                            className="date-group-items centered pb-2",
                                            labelClassName="date-group-labels btn btn-warning",
                                            labelCheckedClassName="date-group-labels-checked",
                                            inline=True,
                                            options=[
                                                {'value':key, 'label': key} for key in dfs.keys()
                                            ],
                                        ),
                                        html.P(
                                            className='centered text-muted pt-2',
                                            children='evaluation',
                                        ),                                                     
                                        dbc.RadioItems(
                                            id='yaxis-data-evaluation',
                                            value = list(evaluation_options)[0],
                                            className="date-group-items centered pb-2",
                                            labelClassName="date-group-labels btn btn-warning",
                                            labelCheckedClassName="date-group-labels-checked",
                                            inline=True,
                                            options=[
                                                {'value':key, 'label': key} for key in evaluation_options
                                            ],
                                        ),
                                        html.P(
                                            className='centered text-muted pt-2',
                                            children='axis scale',
                                        ),
                                        dbc.RadioItems(
                                            id='yaxis-type',
                                            value=list(GRAPH_SCALE_OPTIONS.keys())[-1],
                                            className="date-group-items centered pb-2",
                                            labelClassName="date-group-labels btn btn-warning",
                                            labelCheckedClassName="date-group-labels-checked",
                                            inline=True,
                                            options=[{'value': value, 'label': label} for value, label in GRAPH_SCALE_OPTIONS.items()],
                                        ),
                                        html.P(
                                            className='centered text-muted pt-2',
                                            children='number of moving average days',
                                        ),                                                         
                                        dbc.RadioItems(
                                            id='yaxis-averaging-range-slider',
                                            value=1,
                                            className="date-group-items centered pb-2",
                                            labelClassName="date-group-labels btn btn-warning",
                                            labelCheckedClassName="date-group-labels-checked",
                                            inline=True,
                                            options=[{'value': value, 'label': value} for value in range(1,8,1)],
                                        ),                                                        
                                    ],
                                ),
                            ],
                        ),
                        dbc.Col(
                            id='xaxis-settings-col',
                            children=[
                                html.H3(
                                    className='centered p-2',
                                    children='X-axis',
                                ),
                                dbc.Card(
                                    className='border-5 rounded py-2 m-2 bg-light',
                                    children= [        
                                        html.P(
                                            className='centered text-muted pt-2',
                                            children='data',
                                        ),                                                                 
                                        dbc.RadioItems(
                                            id="xaxis-data-selection",
                                            value= list(dfs.keys())[-1],
                                            className="date-group-items centered pb-2",
                                            labelClassName="date-group-labels btn btn-warning",
                                            labelCheckedClassName="date-group-labels-checked",
                                            inline=True,
                                            options=[
                                                {'value':key, 'label': key} for key in dfs.keys()
                                            ],
                                        ),
                                        html.P(
                                            className='centered text-muted pt-2',
                                            children='evaluation',
                                        ),                                                     
                                        dbc.RadioItems(
                                            id='xaxis-data-evaluation',
                                            value = list(evaluation_options)[0],
                                            className="date-group-items centered pb-2",
                                            labelClassName="date-group-labels btn btn-warning",
                                            labelCheckedClassName="date-group-labels-checked",
                                            inline=True,
                                            options=[
                                                {'value':key, 'label': key} for key in evaluation_options
                                            ],
                                        ),
                                        html.P(
                                            className='centered text-muted pt-2',
                                            children='axis scale',
                                        ),
                                        dbc.RadioItems(
                                            id='xaxis-type',
                                            value=list(GRAPH_SCALE_OPTIONS.keys())[-1],
                                            className="date-group-items centered pb-2",
                                            labelClassName="date-group-labels btn btn-warning",
                                            labelCheckedClassName="date-group-labels-checked",
                                            inline=True,
                                            options=[{'value': value, 'label': label} for value, label in GRAPH_SCALE_OPTIONS.items()],
                                        ),
                                        html.P(
                                            className='centered text-muted pt-2',
                                            children='number of moving average days',
                                        ),                                                         
                                        dbc.RadioItems(
                                            id='xaxis-averaging-range-slider',
                                            value=1,
                                            className="date-group-items centered pb-2",
                                            labelClassName="date-group-labels btn btn-warning",
                                            labelCheckedClassName="date-group-labels-checked",
                                            inline=True,
                                            options=[{'value': value, 'label': value} for value in range(1,8,1)],
                                        ),                                                       
                                    ],
                                ),
                            ],
                        ),                                        
                    ],
                ),
                html.P(
                    className='centered text-muted pt-2',
                    children='country selection',
                ),                            
                dcc.Dropdown(
                    id='country-selection',
                    value = INITIAL_COUNTRIES,
                    placeholder='Select some countries...',
                    multi=True,
                    className='m-2',
                    persistence=True,
                    options=[
                        {'label':country,'value':country} for country in list_of_avaliable_countries
                    ],
                ),
                html.Div(
                    id='data-visualitaion-graph',
                    children=['populated by callback'],
                ),
                dcc.RangeSlider(
                    id='date-range-slider',
                    className='mb-5 pb-2 mx-2',
                    updatemode='drag',
                    min=0,
                    max=(len(list_of_available_dates) - 1),
                    count=1,
                    step=1,
                    allowCross=True,
                    pushable=2,
                    value=[0, (len(list_of_available_dates) - 1)],
                    marks=get_slider_marks(list_of_available_dates),
                    persistence=True,
                ),
            ],
        ),
        html.Footer(
            id='footer-information',
            className='text-muted border-top text-center pt-2',
            children=[
                dcc.Link(
                    id='github-repo-link',
                    href='https://github.com/jmacenka/dash-covid-19-visualization',
                    children=[
                        'App source code',
                    ],
                ),
                html.Br(),
                html.A(
                    id='footer-email-to-developer',
                    href='mailto:corona.macenka.de@gmx.net',
                    children=[
                        'Email to developer'
                    ],
                ),
                html.Br(),
                'App by Jan Macenka - 29.03.2020',
            ]    
        ),
        
    ],
)

@app.callback(
    Output("info-modal", "is_open"),
    [Input("open-info-modal", "n_clicks"), Input("close-info-modal", "n_clicks")],
    [State("info-modal", "is_open")],
)
def toggle_modal(n_open, n_close, is_open):
    # global list_of_avaliable_countries, evaluation_options, list_of_available_dates, dfs
    # list_of_avaliable_countries, evaluation_options, list_of_available_dates, dfs = generate_dataframes_dict()
    if n_open or n_close:
        return not is_open
    return is_open

@app.callback(
    [Output('data-visualitaion-graph','children'),],
    [Input('country-selection','value'),
    Input('date-range-slider','value'),
    Input('yaxis-type','value'),
    Input('xaxis-type','value'),
    Input('yaxis-data-selection','value'),
    Input('xaxis-data-selection','value'),
    Input('yaxis-data-evaluation','value'),
    Input('xaxis-data-evaluation','value'),
    Input('yaxis-averaging-range-slider','value'),
    Input('xaxis-averaging-range-slider','value'),],    
)
def update_data_visualitaion_graph(country_selection_value, 
                range_slider_value, 
                yaxis_type_value, 
                xaxis_type_value,
                yaxis_data_selection_value,
                xaxis_data_selection_value,
                yaxis_data_evaluation_value,
                xaxis_data_evaluation_value,
                yaxis_averaging_days,
                xaxis_averaging_days,
                ):
    if country_selection_value is None:
        raise PreventUpdate
    env_variables = dict(
            country_selection_value=country_selection_value, 
            range_slider_value=range_slider_value, 
            yaxis_data_selection_value=yaxis_data_selection_value, 
            xaxis_data_selection_value=xaxis_data_selection_value, 
            yaxis_data_evaluation_value=yaxis_data_evaluation_value, 
            xaxis_data_evaluation_value=xaxis_data_evaluation_value, 
            yaxis_type_value=yaxis_type_value, 
            xaxis_type_value=xaxis_type_value, 
            yaxis_averaging_days=yaxis_averaging_days, 
            xaxis_averaging_days=xaxis_averaging_days,
        )
    
    graph = build_graph(**env_variables)
    
    return (
        graph,     
    )


# Extract the Flask-Server for gunicorn
server = app.server
# Run the Dash app, only for local development
if __name__ == '__main__':
    if not os.environ.get('LAUNCHED_FROM_DOCKER_COMPOSE',False):
        app.run_server(debug=True, port=8055)
    else:
        app.server.run(host='0.0.0.0',debug=True, port=int(os.environ.get('COVID_APP_CONTAINER_EXPOSED_PORT',8050)), threaded=True)