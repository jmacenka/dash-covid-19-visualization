import requests
import pandas as pd

LIST_OF_AVALIABLE_DATASETS = ['confirmed','deaths','recovered']

def get_population_by_country_dict():
    return {c['name'].lower():c['population'] for c in requests.get('https://restcountries.eu/rest/v2/all').json()}

def generate_dataframes_dict(source_file_list = [(sub,f"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_{sub}_global.csv") for sub in LIST_OF_AVALIABLE_DATASETS]):
    dfs = {}
    country_population_dict = get_population_by_country_dict()
    for sub, path in source_file_list:
        # TODO: Parallelize this
        sub_cap = sub.capitalize()
        df = pd.read_csv(path)
        df = df.groupby('Country/Region').agg('sum').drop(['Lat','Long'],axis=1).T
        df.index = pd.to_datetime(df.index, infer_datetime_format=True)
        df['World'] = df.sum(axis=1)
        dfs[f'{sub_cap} cases'] = {
            'data':df.copy(deep=True),
            'unit':'total cases',
        }
        dfs[f'{sub_cap} new cases'] = {
            'data':df.diff().copy(deep=True),
            'unit':'cases / day',
        }
        dfs[f'{sub_cap} cases growth rate'] = {
            'data':df.pct_change().copy(deep=True)*100,
            'unit':'% change from previous day',
        }

        # Normalizing by country population
        available_country_population = set(country_population_dict.keys())
        df_normalized = pd.DataFrame()
        for country in df.columns:
            c = country.lower()
            if c in available_country_population:
                country_population = country_population_dict.get(c)
                df_normalized[country] = df[country] / (country_population/100)
            else:
                df_normalized[country] = pd.Series([1 for _ in df.index])
        dfs[f'{sub_cap} normalized country population'] = {
            'data': df_normalized,
            'unit':'% of countrys population',
        }
        
    dfs['Time'] = {
        'data':pd.DataFrame({country:df.index for country in df.columns}),
        'unit':'date',
    }
    return (df.columns.unique(), df.index, dfs)