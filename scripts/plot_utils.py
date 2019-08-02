
import os
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd


# size of plots (inches)
figsize = (12, 5.5)


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


def eventPlotter(dfx, title, col='sigma', suffix="", lwidth=1.0, label=None, color=None):
    try:
        xvals = dfx['time'].astype('timedelta64[m]')
    except KeyError:
        xvals = dfx.index.astype('timedelta64[m]')
        pass
    
    if color:
        plt.plot(xvals, dfx[col], label=label, color=color, linewidth=lwidth)
    else:
        plt.plot(xvals, dfx[col], label=label, linewidth=lwidth)
    
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
              color=mcolors.to_rgb('gray')+(0.75,), label='$\mu + 2\sigma$', 
              linewidth=2, linestyle='--')
    
    plt.plot( xvals, means['sigma']+stds['sigma'],
              color=(0,0,0,0.5), label='$\mu + \sigma$',
              linewidth=2, linestyle='--')
    
    plt.plot( xvals, means['sigma'],
              label='$\mu$', color=mcolors.to_rgb('lightblue')+(1.0,),
              linewidth=2.0, linestyle='--')
    
    plt.plot( xvals, means['sigma']-stds['sigma'],
              color=(0,0,0,0.5), label='$\mu - \sigma$',
              linewidth=2, linestyle='--')
    
    plt.plot( xvals, means['sigma']-2.0*stds['sigma'],
              color=mcolors.to_rgb('gray')+(0.75,), label='$\mu - 2\sigma$',
              linewidth=2, linestyle='--')
    
    plt.ylim([100, 1900])
    plt.legend(loc='lower left')
    #plt.xticks(xvals, rotation='vertical')

    #plt.fill_between(xvals, min15, min25, facecolor='black', alpha=0.10)
    #plt.fill_between(xvals, mu,    min15, facecolor='black', alpha=0.155)
    #plt.fill_between(xvals, mu,    add15, facecolor='black', alpha=0.155)
    #plt.fill_between(xvals, add15, add25, facecolor='black', alpha=0.10)
        
    pass


def plotSamplePaths(dfs, title, means, stds, col='sigma', tsb=None, tse=None):
    xvals = means.index.astype('timedelta64[m]').values

    # new figure
    plt.figure(figsize=(figsize[0], figsize[1]*2))

    # first subplot
    
    plt.subplot(2,1,1)
    # highlight interesting region
    if tsb != None and tse != None:
        plt.axvspan(tsb, tse, color='red', alpha=0.2)
    
    plotUsageProfile(means, stds)
    for label, color, samp in dfs:
        eventPlotter(samp, title, col=col, lwidth=1.2,
                     label=label, color=mcolors.to_rgb(color)+(0.75,))
        
    plt.xticks(xvals)
    plt.setp( plt.xticks()[1], visible=False )
    plt.xlim( min(xvals), max(xvals) )
    plt.grid(True)

    # second subplot
    plt.subplot(2,1,2)
    
    # highlight interesting region
    if tsb != None and tse != None:
        plt.axvspan(tsb, tse, color='red', alpha=0.2)

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

    plt.xlabel("time (m)")

    plt.setp( plt.xticks()[1], visible=True )
    plt.xlim( min(xvals), max(xvals) )
    plt.ylim([-2.5,2.5])
    plt.xticks(xvals, rotation='vertical')
    plt.grid(True)
    if len(dfs) < 10:
        plt.legend(loc='upper left')
     
    # adjust subplot locations
    plt.subplots_adjust(bottom=0.125, top=1.0 - 0.0425, wspace=0.35)
    plt.tight_layout()
    pass
