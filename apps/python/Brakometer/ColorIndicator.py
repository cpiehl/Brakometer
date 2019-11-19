
import ac

class ColorIndicator:

	def __init__(self, app, color, x, y, w, h):

		self.x = x
		self.y = y
		self.h = h
		self.w = w
		self.color = color # {'r':1,'g':0,'b':0,'a':1}
		self.saturation = 1


	def setVisible(self, enabled=True):
		self.color['a'] = 1 if enabled else 0


	def setEnabled(self, enabled=True):
		self.saturation = 1 if enabled else 0.4


	def render(self):
		ac.glColor4f(
			self.color['r'] * self.saturation, 
			self.color['g'] * self.saturation, 
			self.color['b'] * self.saturation, 
			self.color['a']
		)
		ac.glQuad(self.x, self.y, self.w, self.h)
