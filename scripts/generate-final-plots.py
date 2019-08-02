from plot_utils import *

# ##############################################################################

highlight_regions = [
    ('2013-03-30', '2013-04-02', 'Bank Holiday?', 'red'),
    ('2013-09-04', '2013-10-26', 'Primary School Term?? .. Daylight Saving??!',
     'red'),
    ('2013-12-24', '2013-12-27', 'Christmas.', 'green'),
    
]

# number of daily pow. usage bits to plot
sample_size = 35

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
dates = pd.Series(weather.index).sample( sample_size )

dfs=[]
for date in dates:
    dname = f'{date.year}-{date.month}-{date.day}'
    
    df = data.loc[dname]
    dfs.append(
        (dname, (0.5, date.month/12.0, 0.5), df))
    
plotSamplePaths( dfs, f'n={sample_size} Daily Power Curves',
                 means, stds )
#plt.show()
plt.savefig('sample-paths.png')
#plt.close()

# ##############################################################################

figsize=(200//12//2,5)
rng = data['date'].apply(lambda date: \
                         date >= pd.to_datetime('2013-12-19'))
region = data.loc[rng]
daily = region.groupby('date').apply(lambda x : x.set_index('time')['sigma'])
zdaily = pd.DataFrame(
    dict([(date,
           (daily.loc[date] - means['sigma'])/stds['sigma']) \
                              for date in daily.index ]) ).transpose()
# plot full adjusted year
plt.figure(figsize=figsize)

delta = pd.to_timedelta('1 day')
zero = pd.to_timedelta('00:00:00')
for date in zdaily.index[:-1]:
    ser = zdaily.loc[date]

    if date.day_name() in ['Saturday', 'Sunday']:
        color = 'green'
    else:
        color = 'blue'

    xvals = [ date + ts for ts in zdaily.columns ]
    xvals.append(date + delta)
    ser.loc['1 day'] = zdaily.loc[date+delta][zero]
    plt.plot(xvals, ser, color=color, linewidth=1)
    pass

srise = zdaily.index + times.loc[zdaily.index, 'sunrise']
sset = zdaily.index + times.loc[zdaily.index, 'sunset']

# show nights
for day in srise.index[:-1]:
    plt.axvspan( sset[day], srise[day+delta], ymax=1.0,
                 color=(0,0,0.5,0.08,))

# highlight interesting regions
#for beg, end, name, color in highlight_regions:
#    beg = pd.to_datetime(beg)
#    end = pd.to_datetime(end)
#    
#    plt.axvspan( beg, end, color=color, alpha=0.3, ymin=0.84, ymax=1.0)
#    plt.text(beg, 4.0, name, fontsize=15)
    
# extract x-ticks and labels
xvals = pd.to_datetime(data['date'].unique())
labels = [ f'{x.month}-{x.day:02}' for x in xvals ]

plt.xticks( xvals, labels, rotation='vertical')
plt.xlim( min(zdaily.index) , max(zdaily.index) )
plt.ylim(-2, 4.2)
             
plt.tight_layout()
plt.savefig('adjusted-event.png')

# plot unscaled power usage
plt.figure(figsize=figsize)
delta = pd.to_timedelta('1 day')
zero = pd.to_timedelta('00:00:00')
for date in daily.index[:-1]:
    ser = daily.loc[date]

    if date.day_name() in ['Saturday', 'Sunday']:
        color = 'green'
    else:
        color = 'blue'

    xvals = [ date + ts for ts in daily.columns ]
    xvals.append(date + delta)
    ser.loc['1 day'] = daily.loc[date+delta][zero]
    plt.plot(xvals, ser, color=color, linewidth=1)
    pass

srise = daily.index + times.loc[zdaily.index, 'sunrise']
sset = daily.index + times.loc[zdaily.index, 'sunset']

# show nights
for day in srise.index[:-1]:
    plt.axvspan( sset[day], srise[day+delta], ymax=1.0,
                 color=(0,0,0.5,0.08,))

xvals = pd.to_datetime(data['date'].unique())
labels = [ f'{x.month}-{x.day:02}' for x in xvals ]

plt.xticks( xvals, labels, rotation='vertical')
plt.xlim( min(zdaily.index) , max(zdaily.index) )
            
plt.tight_layout()
plt.savefig('raw-event.png')

#plt.close()

