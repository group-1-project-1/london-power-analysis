
from plot_utils import *

# ##############################################################################


start_date = pd.to_datetime('2013-01-01')

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
# ##############################################################################

# load events
events = pd.read_csv('./data/Events-2012.csv').astype(
    { 'Date': 'datetime64',
      'Time': 'datetime64',
      'Start-Time': 'datetime64',
      'End-Time': 'datetime64' })


# load data
data = pd.read_csv('./data/complete.csv')
data['datetime'] = pd.to_datetime(data['datetime']) # convert datetime column

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

idx = (data['datetime'] >= start_date)
# calculate hourly usage mean and std.dev
means = data.loc[idx].groupby('time').mean()
stds  = data.loc[idx].groupby('time').std()

for obj in [means, stds]:
    del obj['hour'], obj['minute']
    del obj['year'], obj['month']
    del obj['day'], obj['Unnamed: 0']
    pass


# plot avg. daily power and std. thereof #######################################

xvals = means.index.astype('timedelta64[m]').values
plt.figure(figsize=(figsize[0], figsize[1]*2))
plt.subplot(2,1,1)
plotUsageProfile(means, stds)
plt.xticks(xvals)
plt.setp( plt.xticks()[1], visible=False )
plt.xlim(min(xvals), max(xvals))
plt.grid()

plt.subplot(2,1,2)
plt.plot(xvals, stds['sigma'], label='$\sigma$', color='orange')
plt.xlim(min(xvals), max(xvals))
plt.ylim([10, 350])
plt.xlabel('time (m)')
plt.ylabel('Energy Usage (kW-h/hh)')
plt.xticks(xvals)
plt.grid(True)

plt.legend(loc='upper left')
plt.xticks(rotation='vertical')
plt.tight_layout()

plt.subplots_adjust(bottom=0.125, top=1.0 - 0.0425)
plt.savefig('./images/Mean-Hourly-Profile.png')
plt.close()
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
        
        dfs.extend([(f'day +{ii}', 'green', nfevent),
                    (f'day -{ii}', 'green', pfevent)])
        pass
    dfs.append(('day +/-0', 'blue', dfevent))
    
    # gen. plot parameters
    title = (f'{event["Event Name"]} ({event["Sport"]})'
             f' {event["Date"].month}/{event["Date"].day}/{event["Date"].year}'
             f' at {event["Time"].hour}:{event["Time"].minute:02}'
             f' ({event["Audience"]}m)'
             f' (n~{int(dfevent["count"].mean())})')

    tsb = pd.to_timedelta(
        f'{event["Start-Time"].hour}:{event["Start-Time"].minute:02}:00',
        unit='m').seconds//60
    tse = pd.to_timedelta(
        f'{event["End-Time"].hour}:{event["End-Time"].minute:02}:00',
        unit='m').seconds//60

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
    #plt.grid(True)
    #plt.axvspan(tsb, tse, color='red', alpha=0.2)
    #plt.savefig(('./images/'
    #             f'{iid:03}-{cname}_{csport}_2.png'))
    #plt.close()

    iid += 1
