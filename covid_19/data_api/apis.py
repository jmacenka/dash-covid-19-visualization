import requests, copy
import pandas as pd
# from collections import OrderedDict as dict

LIST_OF_AVALIABLE_DATASETS = ['confirmed','recovered', 'deaths']

def get_population_by_country_dict():
    return {c['name'].lower():c['population'] for c in requests.get('https://restcountries.eu/rest/v2/all').json()}

def generate_dataframes_dict(source_file_list = [(sub,f"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_{sub}_global.csv") for sub in LIST_OF_AVALIABLE_DATASETS]):
    dfs = dict()
    country_population_dict = get_population_by_country_dict()
    for sub, path in source_file_list:
        # TODO: Parallelize this
        sub_cap = sub.lower()
        df = pd.read_csv(path)
        df = df.groupby('Country/Region').agg('sum').drop(['Lat','Long'],axis=1).T
        df.rename(columns={'US':'United States of America'}, inplace=True)
        df['World'] = df.sum(axis=1)
        df.index = pd.to_datetime(df.index, infer_datetime_format=True)

        # Normalizing by country population
        available_country_population = set(country_population_dict.keys())
        df_normalized = pd.DataFrame()
        for country in df.columns:
            c = country.lower()
            if c in available_country_population:
                country_population = country_population_dict.get(c)
                df_normalized[country] = df[country] / (country_population/100)
            else:
                df_normalized[country] = pd.Series([0 for _ in df.index])
        
        cases = {
            'data':df.copy(deep=True),
            'unit':'# cases',
            'tool_tip':'# of cases as gathered in Johns Hopkins data-repository',
        }
        cases_growth_rate = {
            'data':df.pct_change().copy(deep=True)*100,
            'unit':'% change from previous day',
            'tool_tip':'calculated % change from # of cases as gathered in Johns Hopkins data-repository',
        }
        new_cases = {
            'data':df.diff().copy(deep=True),
            'unit':'# cases / day',
            'tool_tip':'calculated difference of cases (as gathered in Johns Hopkins data-repository) between two consecutive days',
        }
        new_cases_normalized = {
            'data':df_normalized.diff().copy(deep=True),
            'unit':'% of countrys population / day',
            'tool_tip':'calculated difference of cases (as gathered in Johns Hopkins data-repository) between two consecutive days',
        }
        normalized_cases = {
            'data': df_normalized.copy(deep=True),
            'unit':'% of countrys population',
            'tool_tip':'calculated from # of cases as gathered in Johns Hopkins data-repository divided by countrys population countn as collected from https://restcountries.eu',
        }
        dfs[sub_cap] = {
            'cumulative cases':cases,
            'cumulative cases normalized':normalized_cases,
            'new cases':new_cases,
            'new cases normalized':new_cases_normalized,
            'growth rate':cases_growth_rate,
        }
        evaluation_options = dfs[sub_cap].keys()
    
    # Calculate the current infected count
    name_infected = 'infected'
    dfs[name_infected] = dict()
    
    for key in evaluation_options:
        dfs[name_infected][key] = copy.deepcopy(dfs['confirmed'][key])
        dfs[name_infected][key]['data'] = dfs['confirmed'][key]['data'] - dfs['deaths'][key]['data'] - dfs['recovered'][key]['data']

    dfs['time'] = {key:{
        'data':pd.DataFrame({country:df.index for country in df.columns}),
        'unit':'date',
    } for key in evaluation_options}

    # Sort dfs by key
    # dfs = {key: value for key, value in sorted(dfs.items(),key=lambda i: i[0])}
    dfs = {key: dfs[key] for key in ['confirmed',name_infected,'recovered','deaths','time']}

    return (df.columns.unique(), evaluation_options, df.index, dfs)
