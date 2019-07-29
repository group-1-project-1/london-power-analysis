import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

def eventPlotter(dfx, title, tsb, tse, col = "sigma", evlev = 160.0): 
    plt.figure(figsize=(12,4))
    plt.plot(dfx["tstamp"],dfx[col])
    plt.xticks(rotation='vertical')
    plt.title(title)
    plt.xlabel("time stamp")
    plt.ylabel("Energy Consumption (kW-h/hh)")
    plt.grid()
    plt.plot([tsb, tse], [evlev, evlev], color='r', linestyle='-', linewidth=2)
    plt.show()
	
def multiEventPlotter(dfxlst, title, tsb, tse, col = "sigma", evlev = 160.0, labels = None): 
    plt.figure(figsize=(12,4))
    handles = []
    tt = labels
    if labels == None:
        tt = [str(xx) for xx in range(len(dfxlst))]
    abc = zip(dfxlst, tt) 	
    for df, lb in abc:
        h, = plt.plot(df["tstamp"],df[col], label = lb)
        handles.append(h)
    plt.legend(loc = 'best', handles = handles)
    plt.xticks(rotation='vertical')
    plt.title(title)
    plt.xlabel("time stamp")
    plt.ylabel("Energy Consumption (kW-h/hh)")
    plt.grid()
    plt.plot([tsb, tse], [evlev, evlev], color='r', linestyle='-', linewidth=2)
    plt.show()

def dayCalc(row):
    return pd.to_datetime(row['datetime']).day

def tstampCalc(row):
    return f"{pd.to_datetime(row['datetime']).hour}:{pd.to_datetime(row['datetime']).minute:02}"

