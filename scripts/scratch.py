import pandas as pd
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


# ##############################################################################

colors  = list(mcolors.CSS4_COLORS.keys())
del colors[:14]

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
        plt.plot(xvals, dfx[col], label=label, color=color, linewidth=0.8)
    else:
        plt.plot(xvals, dfx[col], label=label, linewidth=0.8)
    
    #plt.xticks(xvals, rotation='vertical')
    plt.title(title)
    plt.ylabel(f"Energy Consumption {suffix}")
    #plt.grid(True)
    pass
	

def plotUsageProfile(means, stds):

    plt.ylabel('Energy Usage (kW-h/hh)')
    
    xvals = pd.Series(means.index).astype('timedelta64[m]')

    plt.plot( xvals,
              means['sigma']+2.0*stds['sigma'],
              color='gray', label='$\mu + 2\sigma$', 
              linewidth=2, linestyle='--')
    
    plt.plot( xvals, means['sigma']+stds['sigma'],
              color='black', label='$\mu + \sigma$',
              linewidth=2, linestyle='--')
    
    plt.plot( xvals, means['sigma'],
              label='$\mu$', color='blue',
              linewidth=2.0)
    
    plt.plot( xvals, means['sigma']-stds['sigma'],
              color='black', label='$\mu - \sigma$',
              linewidth=2, linestyle='--')
    
    plt.plot( xvals, means['sigma']-2.0*stds['sigma'],
              color='gray', label='$\mu - 2\sigma$',
              linewidth=2, linestyle='--')
    
    plt.ylim([10, 1700])
    plt.legend(loc='lower left')
    plt.xticks(xvals, rotation='vertical')

    #plt.fill_between(xvals, min15, min25, facecolor='black', alpha=0.10)
    #plt.fill_between(xvals, mu,    min15, facecolor='black', alpha=0.155)
    #plt.fill_between(xvals, mu,    add15, facecolor='black', alpha=0.155)
    #plt.fill_between(xvals, add15, add25, facecolor='black', alpha=0.10)
        
    pass


def plotSamplePaths(dfs, title, means, stds, col='sigma', tsb=None, tse=None):
    xvals = means.index.astype('timedelta64[m]')

    # new figure
    plt.figure(figsize=(figsize[0], figsize[1]*2))

    # first subplot
    plt.subplot(2,1,1)
    plotUsageProfile(means, stds)
    for label, color, samp in dfs:
        eventPlotter(samp, title, col=col,
                     label=label, color=mcolors.to_rgb(color)+(0.75,))
        
    # highlight interesting region
    if tsb != None and tse != None:
        plt.axvspan(tsb, tse, color='red', alpha=0.2)

    #plt.yticks([])
    plt.xticks(xvals)
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
        eventPlotter(samp, '', suffix='(Z-Score)',
                     col=col, label=label, color=color)
        pass

    # highlight interesting region
    if tsb != None and tse != None:
        plt.axvspan(tsb, tse, color='red', alpha=0.2)

    plt.xlabel("time (minutes)")
    plt.xticks(xvals, rotation='vertical')
    
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

# generate 'time' column
data['time'] = data['datetime'].apply(
    lambda x : \
    pd.to_timedelta(f'{x.hour}:{x.minute:02}:00',
                    unit='m'))

# generate 'date' column 
data['date'] = data['datetime'] - data['time']

# calculate hourly usage mean and std.dev
means = data.groupby('time').mean()
stds  = data.groupby('time').std()

for obj in [means, stds]:
    obj['time'] = \
        obj.apply(lambda row :\
                  pd.to_timedelta(
                      f'{int(row["hour"])}:{int(row["minute"]):02}:00',
                      unit='m'),
                  axis=1)
    
    del obj['hour'], obj['minute']
    del obj['year'], obj['month']
    del obj['day'], obj['Unnamed: 0']
    pass

# ##############################################################################

data.set_index('datetime', inplace=True)

# load weather data
weather = pd.read_csv('./data/openweather-london-2013.csv')
weather['date'] = pd.to_datetime(weather['date'])
weather['time'] = pd.to_timedelta(weather['time'])
weather.set_index('date', inplace=True)

# load sunrise/sunset data
times = pd.read_csv('./data/london-sunrise-sunset.csv')
times['date']=pd.to_datetime(times['date'])
times['sunrise']=pd.to_timedelta(times['sunrise'])
times['sunset']=pd.to_timedelta(times['sunset'])
times.set_index('date', inplace=True)

# plot a sample of the daily power usages
sample_size = 15

dates = pd.Series(weather.index).sample( sample_size )

dfs=[]
for date in dates:
    dname = f'{date.year}-{date.month}-{date.day}'
    
    df = data.loc[dname]
    dfs.append(
        (dname, (0.5, date.month/12.0, 0.5), df))
    
plotSamplePaths( dfs, 'title', means, stds )
plt.show()
plt.savefig('sample-paths.png')
plt.close()

# ##############################################################################

daily = data.groupby('date').apply(lambda x : x.set_index('time')['sigma'])
zdaily = pd.DataFrame(
    dict([(date,
           (daily.loc[date] - means['sigma'])/stds['sigma']) \
                              for date in daily.index ]) ).transpose()
plt.figure(figsize=(200,5))
for date in zdaily.index:
    ser = zdaily.loc[date]

    if date.day_name() in ['Saturday', 'Sunday']:
        color = 'green'
    else:
        color = 'blue'

    xvals = [ date + ts for ts in zdaily.columns ]
    plt.plot(xvals, ser, color=color, linewidth=1)
    pass

delta = pd.to_timedelta('1 day')
srise = zdaily.index + times.loc[zdaily.index, 'sunrise']
sset = zdaily.index + times.loc[zdaily.index, 'sunset']

for day in srise.index[:-1]:
    plt.axvspan( sset[day], srise[day+delta],
                 color=(0,0,0.5,0.08,))
plt.xticks( pd.to_datetime(
    [ f'2013-{month+1}-01' for month in range(0,12) ]))

plt.xlim( min(zdaily.index) - 3*delta, max(zdaily.index) + 3*delta )
plt.tight_layout()
plt.show()
plt.savefig('complete-year.png')
#plt.close()

