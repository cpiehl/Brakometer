
import ac
import acsys
import collections
import os
import platform
import sys

from bisect import bisect_left, insort_left
from ColorIndicator import ColorIndicator

if platform.architecture()[0] == "64bit":
    libdir = 'third_party/lib64'
else:
    libdir = 'third_party/lib'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), libdir))
os.environ['PATH'] = os.environ['PATH'] + ";."

from third_party.sim_info import info


YELLOW = {'r':1,'g':1,'b':0,'a':1}
RED    = {'r':1,'g':0,'b':0,'a':1}

SECONDS_PER_LIGHT = 0.5
BRAKE_THRESHOLD = 0.1

class BrakePointIndicator:

	def __init__(self, app, x, y, w, h):

		self.x = x
		self.y = y
		self.h = h
		self.w = w
		self.distanceToBrakePoint = 0
		self.fontSize = 24
		self.pointIndex = 0
		self.readyForNewPoint = False

		self.deltaLabel = ac.addLabel(app, "0m")
		ac.setPosition(self.deltaLabel, x, y)
		ac.setFontSize(self.deltaLabel, self.fontSize)
		ac.setVisible(self.deltaLabel, 0)
		self.labelTTL = 0.0

		self.indicators = []
		self.indicators.append(ColorIndicator(app,    RED, 0,   0, 40, 40))
		self.indicators.append(ColorIndicator(app, YELLOW, 0,  50, 40, 40))
		self.indicators.append(ColorIndicator(app, YELLOW, 0, 100, 40, 40))
		self.indicators.append(ColorIndicator(app, YELLOW, 0, 150, 40, 40))

		self.distanceLabel = ac.addLabel(app, "0m")
		ac.setPosition(self.distanceLabel, x, y + h - self.fontSize)
		ac.setFontSize(self.distanceLabel, self.fontSize)

	
	def setBrakePoints(self, brakePoints):
		self.brakePoints = brakePoints


	def setReadyForNewPoint(self, ready=True):
		self.readyForNewPoint = ready


	def update(self, deltaT):
		kmh, mph, ms = ac.getCarState(0, acsys.CS.SpeedTotal)
		nsp = ac.getCarState(0, acsys.CS.NormalizedSplinePosition)
		distance = nsp * info.static.trackSPlineLength

		if self.readyForNewPoint:
			_isBraking = ac.getCarState(0, acsys.CS.Brake) > BRAKE_THRESHOLD
			if _isBraking:
				self.readyForNewPoint = False
				_distance = distance
				if _distance <= 0.0:
					_distance += info.static.trackSPlineLength
				sorted_insert(self.brakePoints, int(_distance))

		if not self.brakePoints:
			return

		nextTurn, self.pointIndex = get_next(self.brakePoints, distance - (SECONDS_PER_LIGHT * ms))

		# deal with distance resetting to 0 at start/finish
		if nextTurn == self.brakePoints[0] and distance > self.brakePoints[-1]:
			distance = distance - info.static.trackSPlineLength

		ac.setText(self.distanceLabel, "{0:.0f} / {1:.0f}m".format(distance, nextTurn))

		count = len(self.indicators)
		visible = nextTurn - (SECONDS_PER_LIGHT * ms * (count + 1)) < distance

		if visible:
			self.readyForNewPoint = False # if there's already a point at this corner, cancel looking for a new point

		for i in range(count):
			self.indicators[i].setEnabled(nextTurn - (SECONDS_PER_LIGHT * ms * i) < distance)
			self.indicators[i].setVisible(visible)

		self.labelTTL -= deltaT
		if self.labelTTL <= 0.1:
			self.labelTTL = 0.0
			ac.setVisible(self.deltaLabel, 0)
		else:
			ac.setVisible(self.deltaLabel, 1)

	
	def increaseLastPoint(self, amount=1):
		if not self.brakePoints:
			return
		_length = len(self.brakePoints)
		_index = (self.pointIndex - 1 + _length) % _length
		self.brakePoints[_index] += amount
		ac.setText(self.deltaLabel, "{0:.0f}m".format(self.brakePoints[_index]))
		self.labelTTL = 2.0


	def decreaseLastPoint(self, amount=1):
		if not self.brakePoints:
			return
		_length = len(self.brakePoints)
		_index = (self.pointIndex - 1 + _length) % _length
		self.brakePoints[_index] -= amount
		ac.setText(self.deltaLabel, "{0:.0f}m".format(self.brakePoints[_index]))
		self.labelTTL = 2.0


	def render(self):
		for indicator in self.indicators:
			indicator.render()

	def getBrakePoints(self):
		return sorted(self.brakePoints)


def get_next_index(myList, myNumber):
	return bisect_left(myList, myNumber)


def get_next(myList, myNumber):
	"""
	Assumes myList is sorted. Returns next value to myNumber.
	"""
	pos = get_next_index(myList, myNumber)
	if pos == len(myList):
		pos = 0
	return (myList[pos], pos)


def sorted_insert(myList, myNumber):
	insort_left(myList, myNumber)
