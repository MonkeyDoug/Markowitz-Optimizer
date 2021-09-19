=========================================================
Overview
=========================================================

`Link to website <https://share.streamlit.io/monkeydoug/markowitz-optimizer/main/markowitz_optimizer/app.py>`_

A project applying Modern Portfolio Theory, written by Harry Markowitz, to select the most 'efficient' ( highest sharpe ratio ) portfolio. Uses historical log returns to calculate expected return and standard deviation with a covariance matrix of the log returns for the variance. Two main methods are employed, bruteforce simulation and Sequential Least Squares Prorgamming from scipy for the optimization ( minimization ). Data is pulled through the yfinance library, and intervals and periods are based on user input. As always, the projet is built on and hosted on streamlit.

The optimization will always output the most 'efficient' portfolio, its sharpe ratio, its logged and unlogged annualized expected returns, its 'risk', and all the components along with their weights. If the simulation method is used, it will also output charts for the covariance matrix and the efficient frontier, on which the most efficient portfolios lie on. The method will also calculate the minimum variance portfolio, or the portfolio with the least risk, along with its respective statistics.