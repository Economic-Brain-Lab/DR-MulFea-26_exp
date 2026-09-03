# -*- coding: utf-8 -*-
# @Author: Dragan Rangelov <uqdrange>
# @Date:   07-3-2019
# @Email:  d.rangelov@uq.edu.au
# @Last modified by:   uqdrange
# @Last modified time: 21-3-2019
# @License: CC-BY-4.0
#===============================================================================
# importing libraries
#===============================================================================
from __future__ import division, print_function
import sys
sys.dont_write_bytecode = True
import numpy as np
from scipy.special import iv
from experimentinfo import ExperimentInfo
from psychopy import monitors
# import h5py
#===============================================================================
# utility functions
#===============================================================================
def wrapTopi(theta):
    '''
    Wrap array of angles in pi radians from -pi to pi
    Params:
    theta: array of angles in pi radians
    Returns:
    wrapped thetas
    '''
    return (theta + np.pi) % (2 * np.pi) - np.pi

def wrapTo2pi(theta):
    '''
    Wrap array of angles in pi radians from 0 to 2pi
    Params:
    theta: array of angles in pi radians
    Returns:
    wrapped thetas
    '''
    return (theta + 2 * np.pi) % (2 * np.pi)

def k2sd(K):
    '''
    Convert kappa parameter to circular standard deviation
    Params:
    K - kappa of von Mises distribution
    Returns:
    S - standard deviation of circular variable
    '''
    if K == 0:
        S = np.inf
    elif np.isinf(K):
        S = 0
    else:
        S = np.sqrt(-2*np.log(iv(1,K)/iv(0,K)))
    return S

def sd2k(S):
    '''
    Convert circular standard deviation to kappa parameter
    Params:
    S - standard deviation of circular variable
    Returns:
    K - kappa of von Mises distribution
    '''
    R = np.exp(-S**2/2.)
    if R < .85:
        K = -.4 + 1.39*R + .43/(1 - R)
    elif R < .53:
        K = 2*R + R**3 + (5*R**5)/6.
    else:
        K = 1./(R**3 - 4*R**2 + 3*R)
    return(K)
#===============================================================================
# GUI functions
#===============================================================================
def createMonitor(monitorName, data):
    monInfo = ExperimentInfo(title = 'Create new monitor',
                             data = data)
    mon = monitors.Monitor(monitorName)
    mon.setDistance(float(monInfo.monitorDistanceCm))
    mon.setWidth(float(monInfo.monitorWidthCm))
    mon.setSizePix([int(dim)
                    for dim in monInfo.monitorSizePix.split('x')])
    mon.saveMon()
# #===============================================================================
# # save ragged data array
# #===============================================================================
# def saveHDF(file, data, name):
#     '''
#     Add data to an existing hdf file
#     Params:
#         - file - the path name
#         - data - data to save
#         - name - the name under which to save the data
#     '''
#     # make non-ragged arrays
#     dataMerged = np.concatenate(data)
#     # save indices to split the arrays
#     idxSplit = np.cumsum([len(i) for i in data])
#     dataKey = '/' + name + '/' + 'data'
#     idxKey = '/' + name + '/' + 'idx'
#
#     with h5py.File(file,'a') as hf:
#         if name not in hf.keys():
#             maxsizeData = list(dataMerged.shape)
#             maxsizeData[0] = None
#             hf.create_dataset(dataKey,
#                               data = dataMerged,
#                               maxshape = maxsizeData,
#                               compression = 'gzip',
#                               compression_opts = 9)
#             maxsizeIdx = list(idxSplit.shape)
#             maxsizeIdx[0] = None
#             hf.create_dataset(idxKey,
#                               data = idxSplit,
#                               maxshape = maxsizeIdx,
#                               compression = 'gzip',
#                               compression_opts = 9)
#         else:
#             hf[dataKey].resize(len(hf[dataKey]) + len(dataMerged), 0)
#             hf[dataKey][len(hf[dataKey]) - len(dataMerged):] = dataMerged
#
#             idxSplit = hf[idxKey][-1] + idxSplit
#             hf[idxKey].resize(len(hf[idxKey]) + len(idxSplit), 0)
#             hf[idxKey][len(hf[idxKey]) - len(idxSplit):] = idxSplit
