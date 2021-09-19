import yfinance as yf
import streamlit as st

@st.cache(allow_output_mutation=True,suppress_st_warning=True)
def get_data(tickers,period,interval):
    """ Grabs data based on inputted tickers, returns a multi-indexed pandas dataframe """
    with st.spinner('Download Ticker Data'):
        data = yf.download(tickers,period=period,interval=interval,group_by="ticker",threads=True,actions=False)
    return data
