# -*- coding: utf-8 -*-
# @Author: Dragan Rangelov <uqdrange>
# @Date:   07-3-2019
# @Email:  d.rangelov@uq.edu.au
# @Last modified by:   uqdrange
# @Last modified time: 26-3-2019
# @License: CC-BY-4.0
#===============================================================================
# importing libraries
#===============================================================================
from __future__ import division, print_function
import numpy as np
from psychopy.visual import Circle
from psychopy.event import Mouse
from psychopy.event import getKeys
from psychopy.tools.monitorunittools import cm2pix
#===============================================================================
# defining class
#===============================================================================
class ResponseStim():
    '''
    Stimulus display showing response interface with methods to monitor for
    responses.
    '''
    def __init__(self, win,
                 dialRadiusDeg = 1,
                 lineWidthPix = 1,
                 responseMotion = 'circular',
                 padHeightCm = 8):
        '''
        Params:
        - win: window on which the response interface is shown
        - padHeightCm: the height (y axis) of the touchpad in cm
        - dialRadiusDeg: the radius of the response area (clockface) in dva
        - lineWidthPix: line thicknes of the response area in pix
        '''
        # creating response sprites
        self.__dict__['pedestal'] = Circle(win,
                                           radius = dialRadiusDeg,
                                           fillColor = None,
                                           lineColor = 'white',
                                           lineWidth = lineWidthPix,
                                           autoLog = False)

        self.__dict__['pointer'] = Circle(win,
                                          radius = dialRadiusDeg * .20,
                                          fillColor = 'white',
                                          autoLog = False)

        self.__dict__['feedback'] = Circle(win,
                                           radius = dialRadiusDeg * .20,
                                           fillColor = [0, 1, 0],
                                           lineColor = [0, 1, 0],
                                           autoLog = False)


        self.__dict__['mouse'] = Mouse(visible = False,
                                       win = win)

        # asigning attributes
        self.__dict__['win'] = win
        self.__dict__['dialRadiusDeg'] = dialRadiusDeg
        self.__dict__['responseMotion'] = responseMotion
        self.__dict__['padHeightPix'] = cm2pix(padHeightCm, self.win.monitor)
        # these parameters control response collection
        self.__dict__['waitResponse'] = False # should we monitor for response
        self.__dict__['responded'] = False # has response been given
        self.__dict__['stop'] = False # should we stop experiment
        self.__dict__['cont'] = False # should we continue experiment
        self.__dict__['pause'] = False # should we continue experiment
        self.__dict__['respTime'] = np.nan # initialize RT
        self.__dict__['respAngle'] = np.nan # initialize RT
        self.__dict__['targAngle'] = np.nan

        self.update()
        self.setPointerPos(.5 * np.pi)

    def setPointerPos(self, theta):
        newPos_cmplx = np.exp(theta * 1j)
        newPos = (np.array([newPos_cmplx.real, newPos_cmplx.imag])
                            * self.dialRadiusDeg / np.abs(newPos_cmplx))
        self.pointer.pos = newPos
        self.mouse.setPos(newPos)

    def draw(self, drawFeedback = False):
        '''
        draw individual elements of the response display
        '''
        self.pedestal.draw(self.win)
        self.pointer.draw(self.win)
        if drawFeedback:
            feedbackPosition_cmplx = np.exp(self.targAngle * 1j)
            self.feedback.pos = (np.array([feedbackPosition_cmplx.real,
                                           feedbackPosition_cmplx.imag])
                                * self.dialRadiusDeg)
            self.feedback.draw(self.win)

    def update(self):
        '''
        update response interface
        '''
        self.stop = False
        self.cont = False
        keys = getKeys()
        if u'q' in keys:
            self.stop = True
        elif u'space' in keys:
            self.cont = True
        elif u'p' in keys:
            self.pause = True

        # get response position
        x_pos, y_pos = self.mouse.getPos()
        if self.responseMotion == 'circular':
            # compute position as a combination of x and y coordinates
            newPos_cmplx = x_pos + y_pos * 1j
        elif self.responseMotion == 'linear':
            # compute proportion relative to the width of response pad
            newPos_cmplx = np.exp(2 * np.pi * 1j
                                  # this wrap the y_pos to the range of pad width
                                  * ((y_pos + self.padHeightPix) % self.padHeightPix)
                                  # this computes the proportion relative to the pad width
                                  / self.padHeightPix) * np.exp(.5 * np.pi * 1j)

        self.theta = np.angle(newPos_cmplx)
        self.pointer.pos = (np.array([newPos_cmplx.real, newPos_cmplx.imag])
                            * self.dialRadiusDeg / np.abs(newPos_cmplx))

        if self.waitResponse:
            responses, times = self.mouse.getPressed(getTime = True)
            if np.sum(responses):
                self.responded = True
                # saving response angle and response time
                self.respTime = round(times[responses.index(1)], 3)
                self.respAngle = round(self.theta, 3)
            else:
                self.respTime = np.nan
                self.respAngle = np.nan
        else:
            self.responded = False
