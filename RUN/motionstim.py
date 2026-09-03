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
import numpy as np
from psychopy.visual.elementarray import ElementArrayStim
from auxfunctions import wrapTopi
#===============================================================================
# defining class
#===============================================================================
class MotionStim(ElementArrayStim):
    '''
    Stimulus display comprising many individual elements that move with the
    global motion being controlled using class methods.
    '''
    def __init__(self,
                 win,
                 fieldSize = 1,
                 nFields = 1,
                 fieldElements = 100,
                 dotLife = -1):
        '''
        Params:
        win: active display window
        fieldSize: radius of the element field
        nFields: how many fields should the stimulus comprise
        fieldElements: number of elements per field
        dotLife: how long should a dot follow a trajectory before replotting
        Returns:
        MotionStim instance
        '''
        super(MotionStim, self).__init__(win,
                                         fieldSize = fieldSize,
                                         nElements = nFields * fieldElements,
                                         autoLog = False)
        self.nFields = nFields
        self.radius = fieldSize
        self.setDotLife(dotLife)
        self.xys = self.setRandomXYs(self.nElements)

    def setDotLife(self, dotLife):
        self.dotLife = dotLife
        self.dotAge = np.random.uniform(low = 1,
                                        high = dotLife + 1,
                                        size = self.nElements).astype('int')

    def setRandomXYs(self, nDots):
        thetas = np.exp(np.random.vonmises(0, 0, nDots)*1j)
        radius = np.sqrt(np.random.rand(nDots))*self.radius
        newXYs = thetas*radius
        return np.array([np.real(newXYs), np.imag(newXYs)]).T

    def setNewXYs(self, mu = 0, K = 0, dist = 0):
        oldXYs = self.xys # 388 ns
        oldXYs_cmplx = oldXYs[:,0] + oldXYs[:,1] * 1j # 4.7 µs
        mu = np.array(mu)
        K = np.array(K)
        if mu.size == 1:
            mu = np.repeat(mu, self.nFields)
        elif mu.size  != self.nFields:
            raise ValueError('Motion direction has wrong shape.')
        if K.size == 1:
            K = np.repeat(K, self.nFields)
        elif K.size != self.nFields:
            raise ValueError('Motion coherence has wrong shape.') # 10.3 µs

        fields = np.split(np.random.permutation(np.arange(self.nElements)),
                          self.nFields)
        newXYs = [] # 47 µs
        for field, field_idx in enumerate(fields):
            thetas = np.exp(np.random.vonmises(mu[field],
                                               K[field],
                                               size = len(field_idx))*1j) # 71 µs
            newXYs += [oldXYs_cmplx[field_idx] + thetas*dist] # 94 µs
            # wrapping dots that have left the field
            outliers = np.abs(newXYs[field]) > self.radius # 98 µs
            outXY = -newXYs[field][outliers] # rotating for 1 pirad
            newXYs[field][outliers] = (np.exp(np.angle(outXY) * 1j)
                                       * (2 * self.radius
                                          - np.abs(outXY))) # 113 µs
        newXYs = np.concatenate(newXYs)[np.concatenate(fields).argsort(0)] # 128 µs
        self.dotAge -= 1
        dead = (self.dotAge == 0)
        self.dotAge[dead] = self.dotLife # 143 µs
        newXYs_cart = np.array([np.real(newXYs), np.imag(newXYs)]).T # 155 µs
        newXYs_cart[dead] = self.setRandomXYs(np.sum(dead)) # 197 µs
        # self.setXYs(newXYs_cart, log = False)
        self.xys = newXYs_cart

    def setArcMask(self,
                   radOut = 1, radInn = .5,
                   arcPos = 0, arcSpan = np.pi):
        '''
        Make a color circle texture with a transparent arc
        Params:
        - xys: coordinates to be processed
        - radius: what is the radius of the display area
        - radOut: the outer edge of the transparent arc, proportion of radius
        - radInn: the inner edge of the transparent arc, proportion of radius
        - arcPos: the position of the arc on the circle
        - arcSpan: how much of the circle should the arc span
        Returns:
        numpy array mask
        '''
        self.opacities = 1
        xys = self.xys.T
        dist, theta = np.stack([np.sqrt((xys**2).sum(0)),
                                np.arctan2(*xys[::-1])])
        dist /= self.radius
        thetaDiff = np.abs(wrapTopi(wrapTopi(theta) - wrapTopi(arcPos)))
        mask = ((dist > 1)
                | (dist < radInn) | (dist > radOut)
                | (thetaDiff > arcSpan * .5))
        self.opacities[mask] = -1
