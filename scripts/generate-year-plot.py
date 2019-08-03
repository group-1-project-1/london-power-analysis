from plot_utils import *

# ##############################################################################

start_date = pd.to_datetime('2013-01-01')

# ##############################################################################

# load data
raw = pd.read_csv('./data/complete.csv')
raw['datetime'] = pd.to_datetime(raw['datetime']) # convert datetime column

# select dates with large enough sample
data = raw.loc[raw['datetime'] >= start_date].copy()

# generate 'time' column
data['time'] = data['datetime'].apply(
    lambda x : \
    pd.to_timedelta(f'{x.hour}:{x.minute:02}:00',
                    unit='m'))

# generate 'date' column 
data['date'] = data['datetime'] - data['time']
del data['datetime']

# ##############################################################################

figsize=(200,5)
rng = data['date'].apply(lambda date: \
                         date >= pd.to_datetime('2013-01-01'))
region = data.loc[rng]
daily = region.groupby('date').apply(lambda x : x.set_index('time')['sigma'])

# plot full year
plt.figure(figsize=figsize)

delta = pd.to_timedelta('1 day')
zero = pd.to_timedelta('00:00:00')

# plot unscaled power usage
plt.figure(figsize=figsize)
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

srise = daily.index + times.loc[daily.index, 'sunrise']
sset = daily.index + times.loc[daily.index, 'sunset']

# show nights
for day in srise.index[:-1]:
    plt.axvspan( sset[day], srise[day+delta], ymax=1.0,
                 color=(0,0,0.5,0.08,))

xvals = pd.to_datetime(data['date'].unique())
labels = [ f'{x.month}-{x.day:02}' for x in xvals ]

plt.xticks( xvals, labels, rotation='vertical')
plt.xlim( min(daily.index) , max(daily.index) )
            
plt.tight_layout()
plt.savefig('complete-2013.png')

plt.close()

