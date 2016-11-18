import numpy as np


def get_accum_returns(daily):
    acc_returns = np.zeros(len(daily))
    acc_returns[0] = daily[0]
    for i in range(1, len(daily)):
        acc_returns[i] = (1+acc_returns[i-1])*(1+daily[i]) - 1
    return acc_returns
            

def get_volatility(daily):
    volatility = daily.std() * np.sqrt(250)
    return volatility
    

def get_annual_rate(acc_returns):
    annual_rate = (1 + acc_returns[-1]) ** (250.0 / len(acc_returns)) - 1
    return annual_rate


def get_max_draw_down(acc_returns):
    size = len(acc_returns)
    max_value = 0
    max_drow_down = 0
    for i in range(size):
        if acc_returns[i] > max_value:
            max_value = acc_returns[i]
        elif (max_value - acc_returns[i])*1.0 / (1 + max_value) > max_drow_down: 
            max_drow_down =  (max_value - acc_returns[i])*1.0 / (1 + max_value)
#            print max_value, acc_returns[i], max_drow_down
#    print max_value 
    return max_drow_down


def get_sharpe(annual_rate, volatility):
    if volatility == 0:
        return 0
    rf = 3.5 /100
    sharpe = (annual_rate - rf) / volatility
    return sharpe


def get_calmar_ratio(annual_rate, max_drow_down):
    calmar_ratio = annual_rate / max_drow_down
    return calmar_ratio


