
import ac
import acsys
import colorsys
import json
import math
import pickle
import traceback
import threading
import os
import sys
import platform

import ACUtils
from BrakePointIndicator import BrakePointIndicator

doRender = True
appWindow = 0
indicators = {}
customFont = "Consolas"
shutdown = False
tyreCompound = None

KEY_CTRL = 17 # CTRL
KEY_BRAKE_INC = 87 # W
KEY_BRAKE_DEC = 83 # S
KEY_NEW_POINT = 88 # X

def acMain(ac_version):
	global tyreCompound

	appWindow = ac.newApp("Brakometer")
	ac.setSize(appWindow, 40, 200)
	ac.drawBorder(appWindow, 0)
	ac.setBackgroundOpacity(appWindow, 0)
	ac.drawBackground(appWindow, 0)
	ac.setIconPosition(appWindow, 0, -10000)
	ac.setTitle(appWindow, "")

	# Only enable rendering if app is activated
	ac.addOnAppActivatedListener(appWindow, onAppActivated)
	ac.addOnAppDismissedListener(appWindow, onAppDismissed)

	# Custom monospace font
	ac.initFont(0, customFont, 0, 0)

	try:
		indicators["1"] = BrakePointIndicator(appWindow, 0, 0, 40, 200)
		tyreCompound = ac.getCarTyreCompound(0)
		indicators["1"].setBrakePoints(loadBrakePoints())
	except Exception:
		ac.log("Brakometer ERROR: Indicator.__init__(): %s" % traceback.format_exc())

	ac.addRenderCallback(appWindow, onFormRender)
	
	t_kh = threading.Thread(target=keyhook)
	t_kh.start()

	return "Brakometer"


def acUpdate(deltaT):
	global tyreCompound

	try:
		if not doRender:
			return

		# Check if tyre compound changed
		_tyreCompound = ac.getCarTyreCompound(0)
		if _tyreCompound != tyreCompound:
			saveBrakePoints(tyreCompound) # save old compound data
			indicators["1"].setBrakePoints(loadBrakePoints())
			tyreCompound = _tyreCompound

		indicators["1"].update(deltaT)

	except Exception:
		ac.log("Brakometer ERROR: acUpdate(): %s" % traceback.format_exc())


def onFormRender(deltaT):
	try:
		if not doRender:
			return

		indicators["1"].render()

	except Exception:
		ac.log("Brakometer ERROR: onFormRender(): %s" % traceback.format_exc())


def onAppActivated(self):
	global doRender
	doRender = True


def onAppDismissed(self):
	global doRender
	doRender = False


def acShutdown():
	global shutdown
	shutdown = True
	saveBrakePoints()


def getSaveFilePath(_tyreCompound=None):
	if _tyreCompound is None:
		_tyreCompound = ac.getCarTyreCompound(0)
	bpDataPath = os.path.join(os.path.dirname(__file__), "bp_data")

	if not os.path.exists(bpDataPath):
		os.makedirs(bpDataPath)

	fileName = "{}-{}-{}.json".format(ac.getTrackName(0), ac.getCarName(0), _tyreCompound)
	return os.path.join(bpDataPath, fileName)


def loadBrakePoints():
	fullPath = getSaveFilePath()
	ac.console("Brakometer LOADING: %s" % fullPath)
	ac.log("Brakometer LOADING: %s" % fullPath)

	if os.path.exists(fullPath):
		with open(fullPath, 'r') as f:
			try:
				return sorted(json.load(f))
			except Exception:
				ac.log("Brakometer ERROR: loadBrakePoints(): %s" % traceback.format_exc())

	return []


def saveBrakePoints(_tyreCompound=None):
	if _tyreCompound is None:
		_tyreCompound = ac.getCarTyreCompound(0)
	fullPath = getSaveFilePath(_tyreCompound)
	ac.console("Brakometer SAVING: %s" % fullPath)
	ac.log("Brakometer SAVING: %s" % fullPath)

	with open(fullPath, 'w+') as f:
		try:
			json.dump(indicators["1"].getBrakePoints(), f)
		except Exception:
			ac.log("Brakometer ERROR: saveBrakePoints(): %s" % traceback.format_exc())



def keyhook():
	global shutdown
	global KEY_CTRL, KEY_BRAKE_INC, KEY_BRAKE_DEC, KEY_NEW_POINT
	
	keysDown = {}
	keysDown[KEY_BRAKE_INC] = False
	keysDown[KEY_BRAKE_DEC] = False
	keysDown[KEY_NEW_POINT] = False

	while not shutdown:
		if ACUtils.getKeyState(KEY_CTRL):
			try:
				if ACUtils.getKeyState(KEY_BRAKE_INC) and not keysDown[KEY_BRAKE_INC]:
					keysDown[KEY_BRAKE_INC] = True
					indicators["1"].increaseLastPoint(1)
				elif keysDown[KEY_BRAKE_INC] and not ACUtils.getKeyState(KEY_BRAKE_INC):
					keysDown[KEY_BRAKE_INC] = False

				if ACUtils.getKeyState(KEY_BRAKE_DEC) and not keysDown[KEY_BRAKE_DEC]:
					keysDown[KEY_BRAKE_DEC] = True
					indicators["1"].decreaseLastPoint(1)
				elif keysDown[KEY_BRAKE_DEC] and not ACUtils.getKeyState(KEY_BRAKE_DEC):
					keysDown[KEY_BRAKE_DEC] = False

				if ACUtils.getKeyState(KEY_NEW_POINT) and not keysDown[KEY_NEW_POINT]:
					keysDown[KEY_NEW_POINT] = True
					indicators["1"].setReadyForNewPoint()
				elif keysDown[KEY_NEW_POINT] and not ACUtils.getKeyState(KEY_NEW_POINT):
					keysDown[KEY_NEW_POINT] = False

			except Exception:
				ac.console("Brakometer ERROR: keyhook(): %s" % traceback.format_exc())
				ac.log("Brakometer ERROR: keyhook(): %s" % traceback.format_exc())

