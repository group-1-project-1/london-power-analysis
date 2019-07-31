import pandas as pd
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

# ##############################################################################

start_date = pd.to_datetime('2013-01-01')

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
                df['group6_sigma'])
    
    Acorn1 = df["A_sigma"] + df["B_sigma"] + df["C_sigma"]
    Acorn2 = df["D_sigma"] + df["E_sigma"]
    Acorn3 = df["F_sigma"] + df["G_sigma"] + df["H_sigma"] \
                                           + df["I_sigma"] + df["J_sigma"]
    Acorn4 = df["K_sigma"] + df["L_sigma"] + df["M_sigma"] \
                                           + df["N_sigma"]
    Acorn5 = df["O_sigma"] + df["P_sigma"] + df["Q_sigma"]
    Acorn6 = df["U_sigma"]
    return (Acorn1, Acorn2, Acorn3, Acorn4, Acorn5)


def eventPlotter(dfx, title, col='sigma', suffix="", label=None, color=None):
    xvals = dfx['time'].astype('timedelta64[m]')
    if color:
        plt.plot(xvals, dfx[col], label=label, color=color)
    else:
        plt.plot(xvals, dfx[col], label=label)
    
    plt.xticks(xvals, rotation='vertical')
    plt.title(title)
    plt.ylabel(f"Energy Consumption {suffix}")
    #plt.grid(True)
    pass
	

def plotUsageProfile(means, stds):

    plt.ylabel('Energy Usage (kW-h/hh)')
    xvals = means.index.astype('timedelta64[m]')
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
    plt.ylim([10, 1700])
    plt.legend(loc='lower left')

    #plt.fill_between(xvals, min15, min25, facecolor='black', alpha=0.10)
    #plt.fill_between(xvals, mu,    min15, facecolor='black', alpha=0.155)
    #plt.fill_between(xvals, mu,    add15, facecolor='black', alpha=0.155)
    #plt.fill_between(xvals, add15, add25, facecolor='black', alpha=0.10)
        
    pass


def plotSamplePaths(dfs, title, means, stds, col='sigma', tsb=None, tse=None):
    plt.figure(figsize=(figsize[0], figsize[1]*2))

    # first subplot
    plt.subplot(2,1,1)
    plotUsageProfile(means, stds)
    for label, color, samp in dfs:
        eventPlotter(samp, title, col=col, label=label, color=color)
        
    # highlight interesting region
    if tsb != None and tse != None:
        plt.axvspan(tsb, tse, color='red', alpha=0.2)

    #plt.yticks([])
    plt.setp( plt.xticks()[1], visible=False )
    plt.grid(True)
    
    # second subplot
    plt.subplot(2,1,2)    
    # plot z-scores
    for label, color, samp in dfs:
        # calculate z-score series for power signals 
        samp = samp.set_index('time')
        for name in samp.columns:
            if name in means.columns:
                samp[name] = (samp[name]-means[name])/stds[name]
        samp = samp.reset_index()
        
        # plot the new series
        eventPlotter(samp, '', suffix='(Z-Score)', col=col, label=label, color=color)
        pass

    # highlight interesting region
    if tsb != None and tse != None:
        plt.axvspan(tsb, tse, color='red', alpha=0.2)

    plt.xlabel("time (minutes)")
    plt.ylim([-3,3])
    plt.grid(True)
    if len(dfs) < 10:
        plt.legend(loc='upper left')
     
    # adjust subplot locations
    plt.subplots_adjust(bottom=0.125, top=1.0 - 0.0425, wspace=0.35)
    plt.tight_layout()
    pass

# ##############################################################################

# load data
raw = pd.read_csv('./data/complete.csv')
raw['datetime'] = pd.to_datetime(raw['datetime']) # convert datetime column

# select dates with large enough sample
data = raw.loc[raw['datetime'] >= start_date].copy()

# compute acorn group sigmas
grps = extractGroupedAcorn( data )

# generate columns for acorn groups
for ii, grp in enumerate(grps):
    data[f'group{ii+1}_sigma'] = grp

# generate 'tstamp' column
data['time'] = data['datetime'].apply(
    lambda x : pd.to_timedelta(f'{x.hour}:{x.minute:02}:00',
                               unit='m'))

# calculate hourly usage mean and std.dev
means = data.groupby('time').mean()
stds = data.groupby('time').std()

for obj in [means, stds]:
    obj['time'] = \
        obj.apply(lambda row :\
                  pd.to_timedelta(f'{int(row["hour"])}:{int(row["minute"]):02}:00',
                                  unit='m'),
                  axis=1)
    del obj['hour'], obj['minute']
    del obj['year'], obj['month']
    del obj['day'], obj['Unnamed: 0']
    pass



# ##############################################################################

data.set_index('datetime', inplace=True)

weather = pd.read_csv('./data/openweather-london-2013.csv')
weather['date'] = pd.to_datetime(weather['date'])
weather['time'] = pd.to_timedelta(weather['time'])

times = pd.read_csv('./data/london-sunrise-sunset.csv')
times['date']=pd.to_datetime(times['date'])
times['sunrise']=pd.to_timedelta(times['sunrise'])
times['sunset']=pd.to_timedelta(times['sunset'])
times.set_index('date', inplace=True)

dates = weather['date'].sample(3)
weather.set_index('date', inplace=True)

dfs=[]

for idx in range(0, len(dates)):
    date = dates.iloc[idx]
    
    dname = f'{date.year}-{date.month}-{date.day}'
    df = data.loc[dname]
    dfs.append((dname, None, df))
    
plotSamplePaths( dfs, 'title', means, stds )
