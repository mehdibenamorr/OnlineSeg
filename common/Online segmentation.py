import pandas as pd
import numpy as np
import os, sys, glob
import platform
import time
import matplotlib.pyplot as plt
import yaml
import datetime
from matplotlib.font_manager import FontProperties
from matplotlib.cm import get_cmap
import pickle
from common.common import *
# framerate = 50.0

EPS = 1e-15
theta=0.005


if __name__ == '__main__':
    #All global variables

    # if platform.system() == 'Windows':
    #     path_ = 'Y:'
    # elif platform.system() == 'Linux':
    #     path_ = '/mnt/Y'
    # path = path_ + '/Football/soccer_experiments/soccer-kickups/processed_ball_and_pose/'
    # file_path = path + '00049_alex_kickups_01_jointsball.csv'
    #
    # df_ball = pd.read_csv(file_path, usecols=['frame_idx','top','bottom','left','right'], index_col='frame_idx') #ball data
    # df_ball_y= pd.DataFrame({'BallY': df_ball['bottom']},
    #                 index=df_ball.index)
    # df_ball=df_ball_y.reset_index().drop_duplicates('frame_idx').set_index('frame_idx')

    #our time serie
    # P = df_ball['BallY']
    # Index = P.index

    # testing on other time series (synthetic)
    #sinusoidal
    Fs = 1000
    f = 10
    x = np.arange(0, 100, 1)
    y = np.abs(np.sin(2 * np.pi * f * x / Fs))
    #quadratic
    # x = np.arange(0, 100, 1)
    # y = x** 2 + 5 *x + 10
    # y = x ** 2 - 25 * x + 510
    P = pd.DataFrame(y, index=x, columns=['Y'])['Y']
    Index=P.index


    # Initialization
    F = ['linear','quadratic']  # Linear , quadtratic candidate funcitons
    params=[2,3]
    lg = []  # list of approx params of global segments of the time series
    ll = [[] for j in range(len(F))]  # list of lists of approx params of local segments for each candidate function
    lla=[]
    p_first = Index[0]
    p_start = []
    for j in range(len(F)):
        p_start.append(Index[0])

    FCS = [Polygon() for j in range(len(F))]  # feasible coeff space of each candidate func
    Fcf = False  # Whether a candidate function has been picked as approx func or not
    Frv = False  # whether the chosen approx func is not longer feasible for further approx

    #Finding Segmenting Points
    i = 0
    last = False
    while i < len(Index)-1:
        i += 1
        p_next = Index[i]
        if i==len(Index)-1:
            last=True
        if not Fcf:  # have not chosen an apporx func for the current subsequence
            for j in range(len(F)):
                fcs = FCSA(F[j], FCS[j], p_start[j], p_next)
                if fcs.isempty(): #Look for a better condition
                    ll[j].append((p_start[j],Index[i-1],FCS[j]))  # figure out what to append as local segment (start,end,..)
                    p_start[j] = Index[i-1]
                    fcs = FCSA(F[j], FCS[j], p_start[j], p_next)
                FCS[j] = fcs
            local_seg_for_all_fc = True #all llj!=empty
            for j in range(len(F)):
                if not ll[j]:
                    local_seg_for_all_fc = False
            if local_seg_for_all_fc or last:
                nbp=[0 for j in range(len(F))]
                for j in range(len(F)):
                    # calculate np between p_first and p_next-1
                    if last:                                            # Changes in here to handle the end of the time series
                        ll[j].append((p_start[j],p_next,FCS[j]))
                        p_start[j]=Index[i-1]
                    nbp[j]=params[j]*len(ll[j]) #not so sure about this
                # choose fa with the min np and (error later) lla=(p_start_a,np,cf,p_end_a)
                # print (nbp , ll[0], ll[1])
                fa=nbp.index(min(nbp))

                if (p_start[fa] != Index[i-1]):
                    Fcf = True
                else:
                    Frv = True
                    lg.append((ll[fa],F[fa]))
        else:  # have chosen approx func
            FCS[fa] = FCSA(F[fa], FCS[fa], p_start[fa], p_next)
            if FCS[fa].isempty():
                ll[fa].append((p_start[fa],Index[i-1],FCS[fa]))
                lg.append((ll[fa],F[fa]))
                Fcf = False
                Frv = True
            elif last:                                              # Changes in here to handle the end of the time series
                ll[fa].append((p_start[fa],p_next,FCS[fa]))
                lg.append((ll[fa],F[fa]))
        if Frv:
            p_first=Index[i-1]
            for j in range(len(F)):
                ll[j]=[]
                p_start[j] = Index[i - 1]
                FCS[j]=FCSA(F[j],FCS[j],p_start[j],p_next)
            Frv = False
    #AA alogorithm ends here
    print (len(lg))
    for seg in lg:
        print (seg)


    #Plotting Results
    plt.scatter(P.index, P.values, marker='x')
    ax=plt.gca()
    starts=[[] for j in range(len(F))]
    ends = [[] for j in range(len(F))]
    for segment in lg:
        for local_seg in segment[0]:
            if segment[1]=='linear':
                starts[0].append(local_seg[0])
                ends[0].append(local_seg[1])
            elif segment[1]=='quadratic':
                starts[1].append(local_seg[0])
                ends[1].append(local_seg[1])
    ax.vlines(starts[0],ymin=ax.get_ylim()[0],ymax=ax.get_ylim()[1],color='g',label='linear_start')
    # ax.vlines(ends[0], ymin=ax.get_ylim()[0], ymax=ax.get_ylim()[1], color='g', label='linear_end',linestyles='--')
    ax.vlines(starts[1],ymin=ax.get_ylim()[0], ymax=ax.get_ylim()[1], color='r', label='quadratic_start')
    # ax.vlines(ends[0], ymin=ax.get_ylim()[0], ymax=ax.get_ylim()[1], color='r', label='quadratic_end',linestyles='--')
    ax.legend(bbox_to_anchor=(1.005, 0.5))
    plt.show()