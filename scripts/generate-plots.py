import pandas as pd
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

# ##############################################################################
# size of plots (inches)
figsize = (12, 5.5)

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
    hnds = []
    for ii, acorn in enumerate(grps):
        tmp, = plt.plot(list(dfevent.index), acorn,
                        label = f'{acorn_names[ii]}')
        hnds.append( tmp )

    plt.xticks(rotation='vertical')
    plt.title(dtitle)
    plt.xlabel("Timestamp")
    plt.ylabel("Energy Consumption Z-Score")
    
    plt.grid()
    plt.legend(handles=hnds, loc="best")
    pass


def eventPlotter(dfx, title, col='sigma', suffix="", label=None, color=None):
    if color:
        plt.plot(dfx['tstamp'],dfx[col], label=label, color=color)
    else:
        plt.plot(dfx['tstamp'],dfx[col], label=label)
    
    plt.xticks(rotation='vertical')
    plt.title(title)
    plt.xlabel("Timestamp")
    plt.ylabel(f"Energy Consumption {suffix}")
    #plt.grid('on')
    pass
	

def plotUsageProfile():
    #plt.figure(figsize=(figsize[0], figsize[1]*1.5))
    plt.ylabel('Energy Usage (kW-h/hh)')
    plt.plot( xvals, means['sigma']+2.0*stds['sigma'],
              color='darkgray', label='$\mu + 2\sigma$', linestyle='--')
    plt.plot( xvals, means['sigma']+stds['sigma'],
              color='gray', label='$\mu + \sigma$', linestyle='--')
    plt.plot( xvals, means['sigma'],
              label='$\mu$', color='lightblue'  )
    plt.plot( xvals, means['sigma']-stds['sigma'],
              color='gray', label='$\mu - \sigma$', linestyle='--')
    plt.plot( xvals, means['sigma']-2.0*stds['sigma'],
              color='darkgray', label='$\mu - 2\sigma$', linestyle='--')
    plt.title('Usage Profile')
    plt.xticks(rotation='vertical')
    plt.ylim([10, 1700])
    plt.legend(loc='lower left')
    plt.tight_layout()


def plotSamplePaths(dfs, title, means, stds, tsb=None, tse=None):
    plt.figure(figsize=(figsize[0], figsize[1]*2))

    # first subplot
    plt.subplot(2,1,1)
    plotUsageProfile()
    for label, color, samp in dfs:
        eventPlotter(samp, title, label=label, color=color)
        
    # highlight interesting region
    if tsb != None and tse != None:
        plt.axvspan(tsb, tse, color='red', alpha=0.2)

    plt.yticks([])
    plt.grid('on')
    plt.legend()

    # second subplot
    plt.subplot(2,1,2)
    
    # plot z-scores
    for label, color, samp in dfs:
        # calculate z-score series for power signals 
        samp = samp.set_index('tstamp')
        for name in samp.columns:
            if name.endswith('sigma'):
                samp[name] = (samp[name]-means[name])/stds[name]
        samp = samp.reset_index()

        # plot the new series
        eventPlotter(samp, '', suffix='(Z-Score)', label=label, color=color)
        pass

    # highlight interesting region
    if tsb != None and tse != None:
        plt.axvspan(tsb, tse, color='red', alpha=0.2)
    
    plt.ylim([-2.5,2.5])
    plt.grid('on')
    plt.legend(loc='upper left')
    
    # adjust subplot locations
    plt.subplots_adjust(bottom=0.125, top=1.0 - 0.0425, wspace=0.35)
    pass
# ##############################################################################

data = pd.read_csv('./data/complete.csv')
events = pd.read_csv('./data/Events-2012.csv')

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
mdata = data.loc[data['datetime'] >= pd.to_datetime('2013-01-01')]
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

# plot avg. daily power and std. thereof #######################################
xvals = list(means.index)
plt.figure(figsize=(figsize[0], figsize[1]*2))
plt.subplot(2,1,1)
plotUsageProfile()
plt.grid()

plt.subplot(2,1,2)
#plt.figure(figsize=(figsize[0], figsize[1]*0.5))
plt.xlabel('Timestamp')
plt.ylabel('Energy Usage (kW-h/hh)')
plt.plot( xvals, stds['sigma'], label='$\sigma$', color='orange')
plt.ylim([10, 350])
plt.grid()

plt.legend(loc='upper left')
plt.xticks(rotation='vertical')

plt.subplots_adjust(bottom=0.125, top=1.0 - 0.0425)
plt.savefig('./images/Mean-Hourly-Profile.png')

# ##############################################################################

# loop through events
iid = 1
for idx in events.sort_values(by=['Date', 'Time']).index:
    event = events.iloc[idx]

    delta = pd.to_timedelta('1 day')
    year, month, day = \
        ((event['Date']).year,
         (event['Date']).month,
         (event['Date']).day)
    

    # isolate event day
    dfevent = data.loc[
        data['year']==year].loc[
            data['month']==month].loc[
                data['day']==day].copy()

    # generate neighborhood of event day
    dfs = []
    for ii in range(1, 3):
        year0, month0, day0 = \
            ((event['Date']-ii*delta).year,
             (event['Date']-ii*delta).month,
             (event['Date']-ii*delta).day)
        year1, month1, day1 = \
            ((event['Date']+ii*delta).year,
             (event['Date']+ii*delta).month,
             (event['Date']+ii*delta).day)
    
        pfevent = data.loc[
            data['year']==year0].loc[
                data['month']==month0].loc[
                    data['day']==day0].copy()
        nfevent = data.loc[
            data['year']==year1].loc[
                data['month']==month1].loc[
                    data['day']==day1].copy()
        
        dfs.extend([(f'day +{ii}', 'gray', nfevent),
                    (f'day -{ii}', 'gray', pfevent)])
        pass
    dfs.append(('day +/-0', 'blue', dfevent))
    
    # gen. plot parameters
    title = (f'{event["Event Name"]} ({event["Sport"]})'
             f' {event["Date"].month}/{event["Date"].day}/{event["Date"].year}'
             f' at {event["Time"].hour}:{event["Time"].minute:02}'
             f' ({event["Audience"]}m)'
             f' (n~{int(dfevent["count"].mean())})')
    tsb = f'{event["Start-Time"].hour}:{event["Start-Time"].minute:02}'
    tse = f'{event["End-Time"].hour}:{event["End-Time"].minute:02}'

    # produce plots and save results
    cname = event["Event Name"].replace(" ", "-").replace(".","")
    cname = cname.replace("'", "")
    csport = event["Sport"].replace(" ", "")

    plotSamplePaths( dfs, title, means, stds, tsb=tsb, tse=tse )
    plt.savefig(('./images/'
                 f'{iid:03}-{cname}_{csport}_1.png'))
    plt.close()

    # separate plot
    #eventPlotterAcorn(dfevent, title, tsb, tse)
    #plt.grid('on')
    #plt.axvspan(tsb, tse, color='red', alpha=0.2)
    #plt.savefig(('./images/'
    #             f'{iid:03}-{cname}_{csport}_2.png'))
    #plt.close()

    iid += 1
