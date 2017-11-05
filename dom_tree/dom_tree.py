import re

class Node():
	def __init__(self, type_node, node_name):
		self.type_node = type_node
		self.node_name = node_name
		self.node_value = []
		self.child_nodes = []
		
	def append_child(self, child):
		self.child_nodes.append(child)
		return child
		
	def getNodeName(self):
		return self.node_name
		
	def getNodeValue(self):
		return self.node_value
		
	def getNodeType(self):
		return self.type_node
		
	def getChildNodes(self):
		return self.child_nodes
		
	
		
class Attr(Node):
	type_is = 'Attribute_Node'
	def __init__(self, name, value):
		super(Attr, self).__init__(node_name=name, type_node=self.type_is)
		self.attr_name = self.node_name
		self.node_value = value
		self.attr_value = value
		self.attr_dict = {self.attr_name:self.attr_value}
	def getAttributeName(self):
		return self.name
	def getAttributeValue(self):
		return self.value
	def getAttribute(self):
		return self.attr_dict

class Comment(Node):
	type_is = 'Comment_Node'
	def __init__(self, value, start, end):
		super(Comment, self).__init__(node_name='#comment', type_node=self.type_is,)
		self.value = value
		self.external_start = start
		self.external_end = end
		
	def __str__(self):
		return self.type_is

class Text(Node):
	type_is = 'Text_Node'
	def __init__(self, name, pos):
		super(Text, self).__init__(node_name=name, type_node=self.type_is)
		self.position = pos
		
	def getLength(self):
		return len(self.node_name)
		
	def getData(self):
		return self.node_name
		
	def __str__(self):
		return self.type_is


class Element(Node):
	type_is = 'Element_Node'
	def __init__(self, name):
		super(Element, self).__init__(type_node=self.type_is, node_name=name)
		self.comment = []
		self.attr = []
		self.text = []
		self.childs = []
		
	def setChilds(self, child):
		if type(child) == str:
			child = child.strip()
			child = re.sub('\s+',' ', child)
			if re.match(r'[\S]+', child):
				self.childs.append(child)
		else:
			self.childs.append(child)
		
	def setText(self, text, pos):
		text = text.strip()
		text = re.sub('\s+',' ', text)
		if re.match(r'[\S]+', text):
			self.text.append(Text(text, pos))
		
	def getText(self):	
		return self.text
		
	def setComment(self, comm):
		self.comment.append(comm)
		
	def getTagName(self):
		return self.node_name 
		
	def appendAttributes(self, name, value):
		self.attr.append(Attr(name, value))
		return self.attr
		
	def getAttributes(self):
		return self.attr
		
	def getAttribute(self, name):
		if self.attr:
			for i in self.attr:
				if i[0] == name:
					return i.node_name, i.attr_value
					
	def getAttributess(self):
		attr = self.attr
		out_dict = {}
		for i in attr:
			out_dict[i.node_name] = i.node_value
		return out_dict
		
	'''def getElementsByTagName(self, name):
		self.list_children = []
		for child in self.child_nodes:
			if child.node_name == name:
				self.list_children.append(child)
		return self.list_children'''
		
	def getElementsByTagName(self, name):
		self.list_children = []
		if self.child_nodes:
			for child in self.child_nodes:
				if child.node_name == name:
					self.list_children.append(child)
					child = child.getElementsByTagName(name)
					if child:
						for i in child:
							self.list_children.append(i)
				else:
					child = child.getElementsByTagName(name)
					if child:
						for i in child:
							self.list_children.append(i)
			return self.list_children		
		else:
			return self.list_children	
		
		
	def hasAttributes(self):
		if self.attributes:
			return True
		else:
			return False
			
	def hasAttribute(self, name):
		if self.attributes[name]:
			return True
		else:
			return False
	
	def __str__(self):
		return self.type_is
				
class DocumentElement(Element):
	name_elem = 'html'
	def __init__(self, ex_start, ex_end, en_start, en_end):
		super().__init__(name=self.name_elem)
		self.enternal_start = en_start
		self.enternal_end = en_end
		self.external_start = ex_start
		self.external_end = ex_end
		
	
		
		
		
class HtmlElement(Element):
	def __init__(self, parent, name, ex_start, ex_end, en_start='', en_end=''):
		super().__init__(name=name)
		self.parent_element = parent
		self.enternal_start = en_start
		self.enternal_end = en_end
		self.external_start = ex_start
		self.external_end = ex_end
		
	
		

	
	
	
#	a = Element('a', 'http://google.com')
#	b = Element('div')
#	print(a.getTagName())
#	print(a.text.getData())
#	a.appendAttributes('class', 'name')
#	a.append_child(b)

