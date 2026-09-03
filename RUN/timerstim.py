# -*- coding: utf-8 -*-
# @Author: Dragan Rangelov <uqdrange>
# @Date:   08-3-2019
# @Email:  d.rangelov@uq.edu.au
# @Last modified by:   uqdrange
# @Last modified time: 22-3-2019
# @License: CC-BY-4.0
#===============================================================================
# importing libraries
#===============================================================================
from __future__ import division, print_function
import numpy as np
from psychopy.visual import ImageStim
from auxfunctions import wrapTo2pi
#===============================================================================
# defining class
#===============================================================================
class TimerStim(ImageStim):
    '''
    Countdown during the break
    '''
    def __init__(self, *args, **kwargs):
        '''
        Create a circle image to serve as a counter
        '''
        super(TimerStim, self).__init__(*args, **kwargs)
        xys = np.indices([self.texRes, self.texRes])
        xys_cart = 2 * xys / xys.max() - 1
        xys_cmplx = xys_cart[0] + xys_cart[1] * 1j
        self.theta = wrapTo2pi(np.angle(xys_cmplx))
        self.abs = np.abs(xys_cmplx)
        image = np.ones([self.texRes, self.texRes, 4])
        image[:, :, 3] = ((self.abs <= 1) & (self.abs >= .25)).astype('int')
        self.image = image

    def setMark(self, progress = .5):
        '''
        Set mark reflecting how much time has passed relative to total waiting time
        Params:
            - progress: proportion of total waiting time
        '''
        progress = round(progress, 2)
        mask = (self.theta > progress * 2 * np.pi).astype('int')
        mask[mask == 0] = -1
        self.mask = mask
