import os
import pickle

def generate():
    """ Pre-Generates mappings from user_input to function accepted parameters and also scaling for different time units 
    Saves two dicts of mappings in storage
    """

    path = os.path.dirname(__file__)
    asset_path = os.path.join(path,'assets')
    # Yahoo Finance Maps
    yf = {
            # '1 Day':{},
            '1 Week':{},
            '1 Month':{},
            '6 Months':{},
            '1 Year':{},
            '5 Years':{},
            '10 Years':{},
            'Max':{},
            }
    # Period for stock prices
    yf_period = {
            # '1 Day':'1d',
            '1 Week':'5d',
            '1 Month':'1mo',
            '6 Months':'6mo',
            '1 Year':'1y',
            '5 Years':'5y',
            '10 Years':'10y',
            'Max':'max',
            }

    # Interval for stock prices
    yf_interval = {
            # '1 Day':['1m','2m','5m','15m','30m','60m','90m','1h'],
            '1 Week':['1m','2m','5m','15m','30m','60m','90m','1h','1d'],
            '1 Month':['2m','5m','15m','30m','60m','90m','1h','1d','5d','1wk'],
            '6 Months':['1d','5d','1wk','1mo','3mo'],
            '1 Year':['1d','5d','1wk','1mo','3mo'],
            '5 Years':['1d','5d','1wk','1mo','3mo'],
            '10 Years':['1d','5d','1wk','1mo','3mo'],
            'Max':['1d','5d','1wk','1mo','3mo'],
            }

    simulation_scaling = {
            '1m':362880,
            '2m':181440,
            '5m':72576,
            '15m':24192,
            '30m':12096,
            '60m':6048,
            '90m':4032,
            '1h':6048,
            '1d':252,
            '5d':50.4,
            '1wk':50.4,
            '1mo':8.4,
            '3mo':2.8,
            }

    sdicts = {'yf_period':yf_period,'yf_interval':yf_interval}

    for horizon in yf.keys():
        for string,dic in sdicts.items():
            yf[horizon][string] = dic[horizon]

    if not os.path.isdir(asset_path):
        os.mkdir(asset_path)

    with open(os.path.join(asset_path,'yf_map.pickle'),'wb') as f:
        pickle.dump(yf,f)

    with open(os.path.join(asset_path,'sim_scale.pickle'),'wb') as f:
        pickle.dump(simulation_scaling,f)
