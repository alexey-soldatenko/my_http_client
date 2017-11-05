from PyQt5 import QtCore, QtGui, QtWidgets


class NewFlowLayout(QtWidgets.QLayout):
	def __init__(self, parent=None, margin=0, spacing=-1):
		super(NewFlowLayout, self).__init__(parent)
		if parent is not None:
			self.setMargin(margin)
		self.setSpacing(spacing)	
		self.itemList = []
		
	def addItem(self, item):
		self.itemList.append(item)
		
	def takeAt(self, index):
		if index >= 0 and index < len(self.itemList):
			return self.itemList.pop(index)
			
	def itemAt(self, index):
		if index >= 0 and index < len(self.itemList):
			return self.itemList[index]
			
	def count(self):
		return len(self.itemList)

					
	def __del__(self):
		item = self.takeAt(0)
		while item:
			item = self.takeAt(0)	
			

	def sizeHint(self):
		return self.minimumSize()

	def minimumSize(self):
		size = QtCore.QSize()

		for item in self.itemList:
			size = size.expandedTo(item.minimumSize())

		return size
		
	def hasHeightForWidth(self):
		return True
			
	def heightForWidth(self, width):
		height = self._doLayout(QtCore.QRect(0, 0, width, 0), True)
		return height
       
	def setGeometry(self, rect):
		super(NewFlowLayout, self).setGeometry(rect)
		self._doLayout(rect, False)    
	
	def _doLayout(self, rect, testOnly):
		x = rect.x()
		y = rect.y()
		lineHeight = 0

		for item in self.itemList:
			if item:
				nextX = x + item.sizeHint().width()
				if nextX > rect.right() and lineHeight > 0:
					x = rect.x()
					y = y + lineHeight
					nextX = x + item.sizeHint().width()
					lineHeight = 0
				if not testOnly:
					item.setGeometry(
						QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))

				x = nextX
				lineHeight = max(lineHeight, item.sizeHint().height())
		
		return y + lineHeight - rect.y()
