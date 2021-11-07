import os
import re
import pickle
import streamlit as st
import pandas as pd
from ingest import get_data
from clean import clean
from simulate import run

st.set_page_config(layout="wide")

st.markdown("""
    # Portfolio Optimization App
    This app takes tickers as inputs and produces the optimal allocation of the given stocks based on either simulations or Sequential Least Squares Programming
    """)

c1,c2 = st.columns(( 2,2 ))

footer="""<style>
a:link , a:visited{
color: #bd93f9;
background-color: transparent;
text-decoration: underline;
}

a:hover,  a:active {
color: #8be9fd;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: #0E1117;
color: #bd93f9;
text-align: center;
}
</style>
<div class="footer">
<p>Developed by Douglas Chen<a style='display: block; text-align: center;' href="https://github.com/MonkeyDoug/" target="_blank">MonkeyDoug</a></p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)

path = os.path.dirname(__file__)
asset_path = os.path.join(path,'assets')

if not os.path.exists(asset_path):
    from generate import generate
    generate()

with open(os.path.join(asset_path,'yf_map.pickle'),'rb') as f:
    yf = pickle.load(f)

with open(os.path.join(asset_path,'sim_scale.pickle'),'rb') as f:
    sim_scale = pickle.load(f)

in_tickers = ['AAPL','AMZN','TSLA']
raw = c1.text_input("Ticker Symbols ( Separated by space or commas )", "AAPL AMZN TSLA")
if ',' in raw:
    in_tickers = raw.split(',')
elif ' ' in raw:
    in_tickers = raw.split(' ')

tickers = []
if 'tickers' in locals():
    for ticker in in_tickers:
        string = ticker.upper()
        re.sub(r'\s+','',string)
        tickers.append(string)
    tickers = set(tickers)
    c1.write('Tickers Inputed')
    c1.write(tickers)

bond_indexes = {
        'iShare Ultra Short-Term Index ( Bills )':'ICSH',
        'Vanguard Short-Term Bond Index ( Notes )':'BSV',
        'Vanguard Long-Term Bond Index ( Bonds )':'BLV'
        }

if st.sidebar.checkbox('Include Risk Free Rate'):
    rfr = st.sidebar.selectbox('Choose the Risk Free Rate',list(bond_indexes.keys()))
    tickers.add(bond_indexes[rfr])

yf_observation = st.sidebar.selectbox("Time horizon for stock data",index=3,options=yf.keys())

yf_interval = st.sidebar.selectbox("Time interval for stock data",index=0,options=yf[yf_observation]['yf_interval'])

choice = st.sidebar.selectbox("Optimization Method",['Minimization Function','Simulation','Both'],help="Minimization is faster than simulation for small number of tickers but does not produce visualizations",index=1)

data = get_data(tickers,yf[yf_observation]['yf_period'],yf_interval)

returns,df,col_names = clean(data,c1)
col_names = list(col_names)

n_sim = 0
if choice == 'Both':
    n_sim = c1.number_input("Number of simulations",1000,help="The more simulations the more accurate, but also the slower it gets",step=1000)
    res1,res2 = run(df,returns,choice,n_sim,sim_scale[yf_interval],c1)
    w1 = res1['Weights']
    res1.pop('Weights')
    w2 = res2['Weights']
    res2.pop('Weights')
    d1 = {}
    for i in range( len(col_names) ):
        d1[col_names[i]] = f'{ round(w1[i],3) }%'
    d2 = {}
    for i in range( len(col_names) ):
        d2[col_names[i]] = f'{ round(w2[i],3) }%'
    with c2.expander('Minimization Stats',expanded=True):
        st.write('Weights')
        st.dataframe(pd.DataFrame.from_dict(d2,orient='index').rename(columns={0:'Weightings'}))
        for key,value in res2.items():
            st.metric(key,value)
    with c2.expander('Simulation Stats',expanded=True):
        st.write('Weights')
        st.dataframe(pd.DataFrame.from_dict(d1,orient='index').rename(columns={0:'Weightings'}))
        for key,value in res1.items():
            if 'Per' in key:
                st.metric(f'{key}{yf_interval}',value)
            else:
                st.metric(key,value)
elif choice == 'Simulation':
    n_sim = c1.number_input("Number of simulations",1000,help="The more simulations the more accurate, but also the slower it gets",step=1000)
    res = run(df,returns,choice,n_sim,sim_scale[yf_interval],c1)
    w = res['Weights']
    res.pop('Weights')
    d = {}
    for i in range( len(col_names) ):
        d[col_names[i]] = f'{ round(w[i],3) }%'
    with c2.expander('Simulation Stats',expanded=True):
        st.write('Weights')
        st.dataframe(pd.DataFrame.from_dict(d,orient='index').rename(columns={0:'Weightings'}))
        for key,value in res.items():
            if 'Per' in key:
                st.metric(f'{key}{yf_interval}',value)
            else:
                st.metric(key,value)
else:
    res = run(df,returns,choice,n_sim,sim_scale[yf_interval],c1)
    w = res['Weights']
    res.pop('Weights')
    d = {}
    for i in range( len(col_names) ):
        d[col_names[i]] = f'{ round(w[i],2) }%'
    with c2.expander('Minimization Stats',expanded=True):
        st.write('Weights')
        st.dataframe(pd.DataFrame.from_dict(d,orient='index').rename(columns={0:'Weightings'}))
        for key,value in res.items():
            st.metric(key,value)
