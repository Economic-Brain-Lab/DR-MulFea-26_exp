#!../venv/bin/python
# -*- coding: utf-8 -*-
# @Author: Dragan Rangelov <uqdrange>
# @Date:   05-2-2019
# @Email:  d.rangelov@uq.edu.au
# @Last modified by:   uqdrange
# @Last modified time: 22-10-2019
# @License: CC-BY-4.0
#===============================================================================
# issue tracker
#===============================================================================
# %%
#===============================================================================
# importing libraries
#===============================================================================
from __future__ import division, print_function
import sys
sys.dont_write_bytecode = True
import os
from auxfunctions import createMonitor
from datetime import datetime
import eegtriggers as eegtrigs
from eyelink import TrackerEyeLink
from experimentinfo import ExperimentInfo
import json
from motionstim import MotionStim
import numpy as np
import pandas as pd
from psychopy import core, data, monitors, logging, visual
from psychopy.sound import Sound
from psychopy.tools.monitorunittools import deg2pix
import psutil
from responsestim import ResponseStim
from runfunctions import runTrial
from timerstim import TimerStim
#===============================================================================
# setting process priority
#===============================================================================
ps = psutil.Process()
if sys.platform == 'win32': ps.nice(psutil.REALTIME_PRIORITY_CLASS)
else: ps.nice(0)
#===============================================================================
# main experiment function
#===============================================================================
def main(info, params, intro):
    '''
    Main experiment routine
    Params:
        - info: session specific information
        - params: parameters for the experiment
        - intro: instructions
    '''
    #===========================================================================
    # setting experimental parameters
    #===========================================================================
    # GENERAL
    refreshRate = int(info.monitorRefreshRate)
    sNo = info.subjectNumber.rjust(3,'0')
    runfile = info.runfile
    monitor = monitors.Monitor(info.monitorName)
    nTrialsPerRun = 20 # how many trials

    # INNER circle
    # radius of the central ring area
    circleRadius = deg2pix(params['stim']['circleRadius']['value'], monitor)
    # proportion of the radius that will be masked
    circleMaskRadius = params['stim']['circleMaskRadius']['value']
    # section of the circumference that will be masked
    circleMaskSpan = params['stim']['circleMaskSpan']['value'] * np.pi
    circleArea = circleRadius ** 2 * np.pi
    circleNDots = params['stim']['circleNDots']['value']

    # OUTER arcs
    # radius of the outer arcs
    ringRadius = deg2pix(params['stim']['ringRadius']['value'], monitor)
    # proportion of the radius that will be masked
    ringMaskRadius = params['stim']['ringMaskRadius']['value']
    # section the circumference that will be masked
    ringMaskSpan = params['stim']['ringMaskSpan']['value'] * np.pi
    ringArea = ringRadius ** 2 * np.pi
    # matching inner and outer areas for dot density
    ringNDots = int(circleNDots / circleArea * ringArea)

    # RESPONSE area
    responseRadius = circleRadius * circleMaskRadius

    # DOTS
    dotSize = deg2pix(params['stim']['dotSize']['value'], monitor)
    dotSpeed = deg2pix(params['stim']['dotSpeed']['value'], monitor)
    dotOffsetPerFrame = dotSpeed / refreshRate
    dotCoherenceRing = params['stair']['dotCoherenceRing']['value'] # coherence of the outer circle
    nMotionDirections = params['stim']['nMotionDirections']['value'] # how many motion directions will be presented


    # SOUNDS
    soundPitch = params['stim']['soundPitch']['value']
    soundDurationSec = params['stim']['soundDurationSec']['value']
    soundOctaveRespOn = params['stim']['soundOctaveRespOn']['value']
    soundOctaveRespOff = params['stim']['soundOctaveRespOff']['value']

    # TEXT
    textHeight = deg2pix(params['stim']['textHeight']['value'], monitor)
    textWidth = deg2pix(params['stim']['textWidth']['value'], monitor)
    textPosition = deg2pix(params['stim']['textPosition']['value'], monitor)

    # TIMING
    centralSignalDuration = int(params['stim']['centralSignalDuration']['value']
                                * refreshRate) # how long ot present task-relevant motion
    peripheralSignalDuration = int(params['stim']['peripheralSignalDuration']['value']
                                   * refreshRate) # how often to change the motion in peripheral arcs

    trialDuration = np.nan
    feedbackDuration = int(params['stim']['feedbackDuration']['value']
                        * refreshRate)
    breakDuration = int(params['stim']['breakDuration']['value']
                        * refreshRate)
    #===========================================================================
    # container structures to select attributes while drawing stimuli
    #===========================================================================
    radInn = {'C': circleMaskRadius,
              'L': ringMaskRadius,
              'R': ringMaskRadius}
    arcPos = {'C': 0 * np.pi,
              'L': 1 * np.pi,
              'R': 0 * np.pi}
    arcSpan = {'C': circleMaskSpan,
               'L': ringMaskSpan,
               'R': ringMaskSpan}
    motionDirections = np.linspace(-np.pi, np.pi,
                                   nMotionDirections, endpoint = False)
    soundOctaves = {'on': soundOctaveRespOn,
                    'off': soundOctaveRespOff}
    signalDuration = {'central': centralSignalDuration,
                      'peripheral': peripheralSignalDuration}
    bhvData = pd.DataFrame()
    conditions = [{'label':'Up',
                   'nReversals': 20,
                   'nTrials': 30,
                   'startVal': .5,
                   'minVal': .01,
                   'maxVal': 10,
                   'stepSizes': 4,
                   'stepType': 'db',
                   'nUp': 1,
                   'nDown': 1,
                   'autoLog': False},
                  {'label':'Down',
                   'nReversals': 20,
                   'nTrials': 30,
                   'startVal': 5,
                   'minVal': .01,
                   'maxVal': 10,
                   'stepSizes': 4,
                   'stepType': 'db',
                   'nUp': 1,
                   'nDown': 1,
                   'autoLog': False}]
    #===========================================================================
    # creating objects
    #===========================================================================
    win = visual.Window(monitor = info.monitorName, units = 'pix',
                        fullscr = info.fullScreen, color = 'black',
                        screen = int(info.monitorNumber))

    stimText = visual.TextStim(win,
                               height = textHeight,
                               wrapWidth = textWidth,
                               pos = textPosition)
    stimText.text = 'Loading the experiment. Please wait.'
    stimText.draw()
    win.flip()

    stimDotField = dict((stim, MotionStim(win,
                                          fieldElements = [circleNDots,
                                                           ringNDots,
                                                           ringNDots][idx],
                                          fieldSize = [circleRadius,
                                                       ringRadius,
                                                       ringRadius][idx]))
                        for idx, stim in enumerate(['C', 'L', 'R']))
    # set properties of individual dots
    for stim in stimDotField.values():
        stim.sizes = dotSize
        stim.elementTex = 'none'
        stim.elementMask = 'circle'

    responseDevice = ResponseStim(win,
                                  dialRadiusDeg = responseRadius * .75,
                                  responseMotion = info.responseMotion,
                                  padHeightCm = params['hardware']['padHeight']['value'])

    stimFeedback = dict((key, Sound(value = soundPitch,
                                    secs = soundDurationSec,
                                    octave = value,
                                    sampleRate = 44100))
                        for key, value in soundOctaves.items())

    stairs = data.MultiStairHandler(conditions = conditions, autoLog = False)

    timer = TimerStim(win, size = responseRadius, color = 'white')

    if info.sendTriggers:
        triggers = info.triggers

    if info.trackEyes:
        # set eye tracker
        calibTargetSize = deg2pix(.75, monitor)
        innerAreaProportion = .25
        texRes = 256
        xys = np.indices([texRes, texRes], dtype = float)
        xys -= xys.max() * .5
        xys /= xys.max()
        xys_abs = np.abs(xys[0] + xys[1] * 1j)
        mask = np.array((xys_abs <= 1) & (xys_abs >= innerAreaProportion),
                        dtype = int)
        mask[mask == 0] = -1
        calibTarget = visual.ImageStim(win,
                                       image = np.ones([texRes, texRes]),
                                       mask = mask,
                                       texRes = texRes,
                                       size = calibTargetSize)
        ilnk = TrackerEyeLink(win,
                              sampleRate = 500,
                              saccadeSensitivity = 0,
                              calibrationType = 'HV5',
                              target = calibTarget,
                              text = stimText)
    #===========================================================================
    # run trials
    #===========================================================================
    task = runfile
    trialNumber = 0
    for thisSD, thisSTAIR in stairs:
        if responseDevice.stop:
            break
        #=======================================================================
        # take a break
        #=======================================================================
        responseDevice.update()
        if trialNumber == 0:
            win.color = 'gray'
            win.flip()
            if info.trackEyes and ilnk.tracker.isRecording() == 0:
                # stop recording and save data
                ilnk.endRecording()
            stimText.text = '\n'.join(intro[runfile])
            while True:
                stimText.draw()
                win.flip()
                if responseDevice.stop or responseDevice.cont or info.simulate:
                    win.color = 'black'
                    win.flip()
                    responseDevice.setPointerPos(.5 * np.pi)
                    break
                responseDevice.update()
            if info.trackEyes and ilnk.tracker.isConnected():
                # start recording and open an new data file
                timestamp =  datetime.now().strftime("%y%m%d%H%M%S")
                edfFileName = info.path + '/EYE/S{}_task-{}_{}.edf'.format(sNo,
                                                                           runfile,
                                                                           timestamp)
                ilnk.beginRecording(win,
                                    edfFileName = edfFileName)

        elif trialNumber % nTrialsPerRun == 0:
            win.color = 'gray'
            win.flip()
            stimText.text = '{} remaining reversals.'.format(np.sum([stair.nReversals
                                                                     - len(stair.reversalIntensities)
                                                                     for stair in stairs.staircases]))
            breakFrame = 0
            while True:
                if (responseDevice.stop # abort experiment
                    or breakFrame == breakDuration # end break
                    or info.simulate): # skip break if simulate
                    win.color = 'black'
                    win.flip()
                    responseDevice.setPointerPos(.5 * np.pi)
                    break
                responseDevice.update()
                # set timer mark
                timer.setMark(breakFrame / breakDuration)
                timer.draw()
                stimText.draw()
                win.flip()
                breakFrame += 1
        #=======================================================================
        # set coherence levels and run trial
        #========================================================================
        kappas = {'C': thisSD,
                  'L': dotCoherenceRing,
                  'R': dotCoherenceRing}

        responseDevice.update()
        [dirsLeft,
         dirsRight,
         targetAngle,
         responseAngle,
         responseTime,
         flipTimes] = runTrial(win,
                             task,
                             info.simulate,
                             trialNumber + 1,
                             responseDevice,
                             stimDotField,
                             kappas,
                             radInn,
                             arcPos,
                             arcSpan,
                             dotOffsetPerFrame,
                             stimFeedback,
                             signalDuration,
                             trialDuration,
                             motionDirections,
                             refreshRate,
                             feedbackDuration)
        frameDurations = np.array(flipTimes)[1:] - np.array(flipTimes[:-1])
        flips, freqs = np.unique(frameDurations.round(3), return_counts = True)
        logMssg= '_'.join(['TASK:{}'.format(task),
                           'TRIAL:{}'.format(trialNumber),
                           'FLIPS:{}'.format('|'.join([str(i) for i in flips])),
                           'FREQS:{}'.format('|'.join([str(i) for i in freqs])),
                           'END',
                           '',
                           '',
                           '',
                           ''])
        logging.warning(logMssg)
        logging.flush()
        if info.sendTriggers:
            triggers.sendTrigger(trialNumber + 1)
        if info.trackEyes:
            ilnk.sendMessage(logMssg)

        errorMagnitude = np.angle(np.exp(targetAngle * 1j)
                                  / np.exp(responseAngle * 1j))
        correct = np.abs(errorMagnitude) < (np.pi / nMotionDirections)

        dataTypes = (['experiment', 'refreshRate', 'trialNumber']
                     + [key for key in dir(info) if 'subject' in key]
                     + ['dirLeft_' + str(idx).rjust(2, '0') for idx in range(len(dirsLeft))]
                     + ['dirRight_' + str(idx).rjust(2, '0') for idx in range(len(dirsRight))]
                     + ['targetAngle', 'responseAngle', 'responseTime'])

        dataValues = ([info.experiment, int(refreshRate), int(trialNumber) + 1]
                      + [info.__dict__[key] for key in dir(info) if 'subject' in key]
                      + [direction for direction in dirsLeft]
                      + [direction for direction in dirsRight]
                      + [targetAngle, responseAngle, responseTime])
        bhvData = pd.concat([bhvData,
                     pd.DataFrame([dict(zip(dataTypes, dataValues))])],
                    ignore_index = True)

        stairs.addResponse(correct)
        trialNumber += 1


    #===========================================================================
    # finish experiment and save data
    #===========================================================================
    stimText.text = 'We are done with this part. Thank you.'
    responseDevice.update()
    win.color = 'gray'
    win.flip()
    stairs.saveAsPickle(str(info.path + '/BHV/S{}_{}'.format(sNo,
                                                             runfile)),
                        fileCollisionMethod = 'overwrite')
    bhvData.to_csv(info.path + '/BHV/S{}_{}.tsv.gz'.format(sNo,
                                                           runfile),
                   sep = '\t',
                   na_rep = 'n/a',
                   index = False,
                   float_format = '%.3f',
                   mode = 'a')
    if info.trackEyes and ilnk.tracker.isRecording() == 0:
        # stop recording and save data
        ilnk.endRecording()
        # stop eye-tracker
        ilnk.closeConnection()
    while True:
        stimText.draw()
        win.flip()
        if responseDevice.stop or responseDevice.cont or info.simulate:
            break
        responseDevice.update()
    win.close()
#===============================================================================
# running the main function
#===============================================================================
# %%
if __name__ == '__main__':
    RUNPATH, FILENAME = os.path.split(__file__)
    ROOTPATH = os.path.dirname(RUNPATH)
    EXPERIMENT = os.path.split(ROOTPATH)[-1]
    RUNFILE = FILENAME.split('.')[0].split('_')[-1]
    #===========================================================================
    # get experiment info and create monitor if necessary
    #===========================================================================
    with open(ROOTPATH + '/RUN/exp_information.json', 'r') as f:
        dataToCollect = json.load(f)
    # GUI dialog to collect experimental info
    expInfo = ExperimentInfo(title = EXPERIMENT,
                             data = dataToCollect['expData'])
    expInfo.__dict__['path'] = ROOTPATH
    expInfo.__dict__['experiment'] = EXPERIMENT
    expInfo.__dict__['runfile'] = RUNFILE
    # create monitor if necessary
    if expInfo.monitorName not in monitors.getAllMonitors():
        createMonitor(expInfo.monitorName, dataToCollect['monData'])
    if expInfo.sendTriggers:
        if not eegtrigs.USB2LPT:
            portInfo = ExperimentInfo(title = 'Parallel port',
                                      data = dataToCollect['portAddress'])
            expInfo.__dict__['triggers'] = eegtrigs.EegTriggerLPT(portNumber = int(portInfo.portAddress, 16))
        else:
            expInfo.__dict__['triggers'] = eegtrigs.EegTriggerUSB()
    #===========================================================================
    # set up logging
    #===========================================================================
    SNO = expInfo.subjectNumber.rjust(3,'0')
    logging.LogFile(ROOTPATH + '/LOG/S{}_{}.log'.format(SNO,
                                                        RUNFILE))
    #===========================================================================
    # get experimental parameters
    #===========================================================================
    with open(ROOTPATH + '/RUN/exp_parameters.json', 'r') as f:
        expParams = json.load(f)
    #===========================================================================
    # get experimental instructions
    #===========================================================================
    with open(ROOTPATH + '/RUN/exp_instructions.json', 'r') as f:
        expIntro = json.load(f)
    #===========================================================================
    # run the main function
    #===========================================================================
    main(expInfo, expParams, expIntro)
    #===========================================================================
    # close the file
    #===========================================================================
    core.quit()
