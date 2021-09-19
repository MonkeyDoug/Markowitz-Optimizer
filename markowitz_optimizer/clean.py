import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

#  @st.cache(suppress_st_warning=True)
def clean(df,c1):
    """ Cleans multi-indexed pandas dataframe with stock price data and also plots a stock price and percent change chart.
    Cleans by removes unneeded columns, columns with large amounts of N/A values, and rows with any N/A values.
    Returns a log of the dataframe, a cleaned multi-indexed pandas dataframe, and names of the columns in the first level of the multi index
    """
    drops = ['Open','High','Low','Volume','Close']
    df.drop(drops,level=1,axis=1,inplace=True)
    df.dropna(inplace=True,axis=1,thresh=500/4)
    df.dropna(inplace=True,axis=0)
    with c1.expander('Stock Charts'):
        with st.spinner('Plotting Stock Prices'):
            st.markdown('## Stock Prices')
            fig = plt.figure(figsize=(14,7))
            for c in df.columns.values:
                plt.plot(df.index,df[c],lw=3,label=c)
            plt.legend(loc='upper left',fontsize=12)
            plt.ylabel('price in $')
            st.pyplot(fig)
        returns = df.pct_change() 
        with st.spinner('Plotting Percent Change'):
            st.markdown('## Percent Change')
            fig = plt.figure(figsize=(14, 7))
            for c in returns.columns.values:
                plt.plot(returns.index, returns[c]*100, lw=3, alpha=0.8,label=c)
            plt.legend(loc='upper right', fontsize=12)
            plt.ylabel('Returns Across Interval')
            st.pyplot(fig)
    log_ret = np.log(df/df.shift(1))
    return log_ret,df,df.columns.get_level_values(0)
