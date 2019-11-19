import os, sys, configparser, platform

if platform.architecture()[0] == "64bit":
    libdir = 'third_party/lib64'
else:
    libdir = 'third_party/lib'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), libdir))
os.environ['PATH'] = os.environ['PATH'] + ";."
from ctypes import windll

def getKeyState(code):
    return bool(windll.user32.GetAsyncKeyState(code) & 32768 is not 0)
