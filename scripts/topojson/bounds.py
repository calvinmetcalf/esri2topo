from mytypes import types

def bound(objects):
	class boundit(types):
		def __init__(self):
			self.x0=self.y0=float('inf')
			self.x1=self.y1=-float('inf')
		def point (self,point):
			x = point[0]
			y = point[1]
			if x < self.x0:
				self.x0 = x
			if x > self.x1:
				self.x1 = x
			if y < self.y0:
				self.y0 = y
			if y > self.y1:
				self.y1 = y
	b=boundit()
	b.obj(objects)
	return [b.x0,b.x1,b.y0,b.y1]
