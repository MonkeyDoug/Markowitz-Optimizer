import math
from time import perf_counter
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sn
from scipy.optimize import minimize
import streamlit as st

#  @st.cache(suppress_st_warning=True,allow_output_mutation=True)
def run(df,returni,choice,n_sim,sim_scalei,c1i):
    """ Drives either Simulation/Minimization or both based on choice """
    global c1
    c1 = c1i
    global returns
    returns = returni
    global n_weights
    n_weights = len(df.columns)
    global sim_scale
    sim_scale = sim_scalei
    if choice == 'Minimization Function':
        return optimize()
    if choice == 'Simulation':
        return simulate(n_sim)
    else:
        res1 = simulate(n_sim)
        res2 = optimize()
        return res1,res2

def simulate(n_sim):
    """ Simulates portfolios and plots a covariance and efficient frontier plot """
    n_ports = n_sim
    ret_arr = np.zeros(n_ports)
    ret_per_int_arr = np.zeros(n_ports)
    vol_arr = np.zeros(n_ports)
    vol_per_int_arr = np.zeros(n_ports)
    weights = np.zeros((n_ports,n_weights))
    sharpe_arr = np.zeros(n_ports)
    bar = c1.progress(0)
    with st.spinner('Simulating Portfolios...'):
        for x in range(n_ports):
            t_weight = np.array(np.random.random(n_weights))
            t_weight = t_weight/np.sum(t_weight)

            weights[x,:] = t_weight

            ret_arr[x] = np.sum( returns.mean() * t_weight * sim_scale )

            ret_per_int_arr[x] = np.sum( returns.mean() * t_weight)

            vol_arr[x] = np.sqrt( np.dot(t_weight.T, np.dot(returns.cov()*sim_scale,t_weight)) )

            vol_per_int_arr[x]  = np.sqrt( np.dot(t_weight.T, np.dot(returns.cov(),t_weight)) )

            sharpe_arr[x] = ret_arr[x]/vol_arr[x]
            bar.progress(((x+1)/n_ports))

    index = sharpe_arr.argmax()

    max_sr_ret = ret_arr[index]
    max_sr_vol = vol_arr[index]

    indexm = vol_arr.argmin()
    min_vol_ret = ret_arr[indexm]
    min_vol_vol = vol_arr[indexm]

    with c1.expander('Simulation Charts',expanded=True):
        with st.spinner('Plotting Covariance'):
            st.write('# Covariance Heatmap')
            fig = plt.figure(figsize=(12,8))
            sn.heatmap(round(returns.cov(),6),annot=True,fmt='g',cmap='viridis')
            plt.xlabel('Log Returns')
            plt.ylabel('Log Returns')
            st.pyplot(fig)

        with st.spinner('Plotting Efficient Frontier'):
            frontier_y = np.linspace(ret_arr.min(),ret_arr.max(),200)
            frontier_x = []
            for ret in frontier_y:
                bounds = []
                for _ in range(n_weights): bounds.append([0,1])
                guess = [n_weights*( 1/n_weights )]
                cons = ({'type':'eq', 'fun':check_sum},
                        {'type':'eq','fun':lambda w: get_ret_vol_sr(w)[0] - ret})
                result = minimize(minimize_vol,guess,method='SLSQP',bounds=bounds,constraints=cons)
                frontier_x.append(result['fun'])

            st.write('# Efficient Frontier')
            st.write("If efficient frontier is very straight, it's because one ticker ( usually risk free rate or the one with the most weighting ) has a overwhelmingly good sharpe ratio.")
            fig = plt.figure(figsize=(12,8))
            plt.scatter(vol_arr,ret_arr,c=sharpe_arr,cmap='viridis')
            plt.colorbar(label='Sharpe Ratio')
            plt.xlabel('Volatility')
            plt.ylabel('Return')
            plt.plot(frontier_x,frontier_y,'r--',linewidth=3)
            plt.scatter(max_sr_vol, max_sr_ret,c='red', s=50) # red dot
            plt.scatter(min_vol_vol, min_vol_ret,c='black', s=50) # red dot
            st.pyplot(fig)
    res = {
            'Max Sharpe Ratio':sharpe_arr.max(),
            'Logged Annualized Expected Return':f'{ max_sr_ret * 100 }%',
            'Unlogged Annualized Expected Return':f'{ (math.e**max_sr_ret - 1) * 100 }%',
            'Annualized Portfolio Variance':f'{ max_sr_vol * 100 }',
            'Logged Expected Return Per ':f'{vol_per_int_arr[index] * 100 }%',
            'Unlogged Expected Return Per ':f'{ (math.e**vol_per_int_arr[index] - 1) * 100 }%',
            'Portfolio Variance Per ':f'{ ret_per_int_arr[index] * 100 }',
            'Weights':weights[index,:]*100,
            'Portfolio Number':str( index ),
            'Logged Annualized Expected Return of Minimum Variance Portfolio':f'{ min_vol_ret* 100 }%',
            'Unlogged Annualized Expected Return of Minimum Variance Portfolio':f'{ (math.e**min_vol_ret - 1 ) * 100 }%',
            'Annualized Portfolio Variance of Minimum Variance Portfolio':f'{ min_vol_vol * 100 }',
            'Sharpe Ratio of Minimum Variance Portfolio':min_vol_ret/min_vol_vol,
            }
    return res

def get_ret_vol_sr(weights):
    weights = np.array(weights)
    ret = np.sum(returns.mean() * weights) * sim_scale
    vol = np.sqrt(np.dot(weights.T, np.dot(returns.cov()*sim_scale,weights)))
    sr = ret/vol
    return np.array([ret,vol,sr])

def neg_sharpe(weights):
    return get_ret_vol_sr(weights)[2] * -1

def check_sum(weights):
    return np.sum(weights)-1

def optimize():
    """ Minimizes neg_sharpe using Sequential Least Squares Programming
    bounds = 0 - 1
    inital guess = equal weights among all assets
    constraints = individual weights must sum to 1
    """
    cons = ({'type':'eq','fun':check_sum})
    bounds = []
    for _ in range(n_weights): bounds.append([0,1])
    guess = [n_weights*( 1/n_weights )]
    s = perf_counter()
    with st.spinner('Minimizing'):
        results = minimize(neg_sharpe,guess,method='SLSQP',bounds=bounds,constraints=cons)
    e = perf_counter()
    c1.success(f'Minimization finished in {e-s} seconds')
    tmp = get_ret_vol_sr(results.x)
    res = {
            'Weights':(results.x) * 100,
            'Max Sharpe Ratio':tmp[2],
            'Logged Annualized Expected Return':f'{ tmp[0]*100 }%',
            'Unlogged Annualized Expected Return':f'{ (math.e**tmp[0] - 1)*100 }%',
            'Annualized Portfolio Variance':f'{ tmp[1]*100 }%',
            }
    return res

def minimize_vol(weights):
    return get_ret_vol_sr(weights)[1]
