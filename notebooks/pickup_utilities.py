import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

def extractGroupedAcorn(df):
    Acorn1 = df["A_sigma"] + df["B_sigma"] + df["C_sigma"]
    Acorn2 = df["D_sigma"] + df["E_sigma"]
    Acorn3 = df["F_sigma"] + df["G_sigma"] + df["H_sigma"] \
                                           + df["I_sigma"] + df["J_sigma"]
    Acorn4 = df["K_sigma"] + df["L_sigma"] + df["M_sigma"] \
                                           + df["N_sigma"]
    Acorn5 = df["O_sigma"] + df["P_sigma"] + df["Q_sigma"]
    return (Acorn1, Acorn2, Acorn3, Acorn4, Acorn5)

def eventPlotterAcorn(dfevent, dtitle, tsb, tse, breaktime=None):
    grps = extractGroupedAcorn( dfevent )
    plt.figure(figsize=(12,4))
    break_idx = 0
    hnds = []
    for ii, acorn in enumerate(grps):
        weight = 1.0
        if breaktime is not None:
            break_idx = dfevent.loc[dfevent['tstamp']==breaktime].index[0]
            weight = 1.0/acorn[break_idx]
        tmp, = plt.plot(dfevent['tstamp'], weight * acorn, label = f'Acorn {ii+1}')
        hnds.append( tmp )

    plt.xticks(rotation='vertical')
    plt.title(dtitle)
    plt.xlabel("time stamp")
    if breaktime is not None:
        plt.ylabel("Normalized Energy Consumption")
    else:
        plt.ylabel("Energy Consumption (kW-h/hh)")

    plt.grid()
    plt.plot([tsb, tse], [0, 0], color='r', linestyle='-', linewidth=2)
    plt.legend(handles=hnds, loc="right")
    plt.show()
    pass


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

