import pandas as pd
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

# ##############################################################################

# acorn groupings
acorn_groups = [ ['A','B','C'],         # affluent
                 ['D','E'],             # rising
                 ['F','G','H','I','J'], # comfortable
                 ['K','L','M','N'],     # stretched 
                 ['O','P', 'Q'],        # adversity
                 ['U'] ]                # other

# acorn group 'designations'
acorn_names = [ 'Affluent',
                'Rising',
                'Comfortable',
                'Stretched',
                'Adversity',
                'Other']

def extractGroupedAcorn(df):
    if 'group1_sigma' in df.columns:
        return (df['group1_sigma'], 
                df['group2_sigma'], 
                df['group3_sigma'], 
                df['group4_sigma'], 
                df['group5_sigma'])
    
    Acorn1 = df["A_sigma"] + df["B_sigma"] + df["C_sigma"]
    Acorn2 = df["D_sigma"] + df["E_sigma"]
    Acorn3 = df["F_sigma"] + df["G_sigma"] + df["H_sigma"] \
                                           + df["I_sigma"] + df["J_sigma"]
    Acorn4 = df["K_sigma"] + df["L_sigma"] + df["M_sigma"] \
                                           + df["N_sigma"]
    Acorn5 = df["O_sigma"] + df["P_sigma"] + df["Q_sigma"]
    return (Acorn1, Acorn2, Acorn3, Acorn4, Acorn5)

def eventPlotterAcorn(dfevent, dtitle, tsb, tse):
    grps = extractGroupedAcorn(dfevent)
    plt.figure(figsize=(12,4))
    hnds = []
    for ii, acorn in enumerate(grps):
        tmp, = plt.plot(dfevent['tstamp'], acorn,
                        label = f'{acorn_names[ii]}')
        hnds.append( tmp )

    plt.xticks(rotation='vertical')
    plt.title(dtitle)
    plt.xlabel("Timestamp")
    plt.ylabel("Energy Consumption Z-Score")
    
    plt.grid()
    plt.axvspan(tsb, tse, color='red', alpha=0.4)
    plt.legend(handles=hnds, loc="best")
    pass


def eventPlotter(dfx, title, tsb, tse, col = "sigma"): 
    plt.figure(figsize=(12,4))
    plt.plot(dfx["tstamp"],dfx[col])
    plt.xticks(rotation='vertical')
    plt.title(title)
    plt.xlabel("time stamp")
    plt.ylabel("Energy Consumption Z-Score")
    plt.grid()
    plt.axvspan(tsb, tse, color='red', alpha=0.4)
    pass
	

# ##############################################################################

data = pd.read_csv('./data/complete.csv')
events = pd.read_csv('/home/burned/Events-2012.csv')

grps = extractGroupedAcorn( data )
# generate columns for acorn groups
for ii, grp in enumerate(grps):
    data[f'group{ii+1}_sigma'] = grp
    
# convert date/time columns and generate 'tstamp' column
data['datetime'] = pd.to_datetime( data['datetime'] )
data['tstamp'] = data['datetime'].apply( lambda x : f'{x.hour}:{x.minute:02}')
events['Date'] = pd.to_datetime( events['Date'] )
events['Time'] = pd.to_datetime( events['Time'] )
events['Start-Time'] = pd.to_datetime( events['Start-Time'] )
events['End-Time'] = pd.to_datetime( events['End-Time'] )

# calculate mean hourly usage and std.dev for hourly signals
mdata = data.loc[ data['datetime'] >= pd.to_datetime('2012-05-01') ]
means = mdata.groupby(['hour', 'minute']).mean().reset_index()
stds = mdata.groupby(['hour', 'minute']).std().reset_index()

means['tstamp']=means.reset_index().apply(
    lambda x : f"{int(x['hour'])}:{int(x['minute']):02}",
    axis=1)

stds['tstamp']=stds.reset_index().apply(
    lambda x : f"{int(x['hour'])}:{int(x['minute']):02}",
    axis=1)

means = means.set_index('tstamp')
stds = stds.set_index('tstamp')

# loop through events
for idx in range(0, len(events)):
    event = events.iloc[idx]

    year, month, day = \
        event['Date'].year, event['Date'].month, event['Date'].day

    # isolate event day
    dfevent = data.loc[
        data['year']==year].loc[
            data['month']==month].loc[
                data['day']==day]

    # calculate z-score series for power signals 
    dfevent = dfevent.set_index('tstamp')
    for name in dfevent.columns:
        if name.endswith('sigma'):
            dfevent[name] = (dfevent[name]-means[name])/stds[name]    
    dfevent = dfevent.reset_index()

    # gen. plot parameters
    title = (f'{event["Event Name"]} ({event["Sport"]})'
             f' {event["Date"].month}/{event["Date"].day}/{event["Date"].year}'
             f' at {event["Time"].hour}:{event["Time"].minute:02}'
             f' ({event["Audience"]}m)')

    tsb = f'{event["Start-Time"].hour}:{event["Start-Time"].minute:02}'
    tse = f'{event["End-Time"].hour}:{event["End-Time"].minute:02}'

    # produce plots and save results
    cname = event["Event Name"].replace(" ", "-").replace(".","")
    cname = cname.replace("'", "")
    csport = event["Sport"].replace(" ", "")
    
    eventPlotter(dfevent, title, tsb, tse)
    plt.savefig(('./images/'
                 f'{cname}_{csport}_1.png'))
    plt.close()
    
    eventPlotterAcorn(dfevent, title, tsb, tse)
    plt.savefig(('./images/'
                 f'{cname}_{csport}_2.png'))
    plt.close()
