import re
import copy

ATTR_BODY_DEFAULT = [[{'display':'block'}, 0], [{'color':'black'}, 0], [{'width':'100%'}, 0], [{'padding':'0'}, 0], [{'margin':'2'}, 0], [{'text-align':'left'}, 0]]

class GeneralObjectCSS():
	def __init__(self, name, attr, text, all_attr):
		self.name = name
		self.text = text
		self.attributes = all_attr
		prior=20
		self.own_attr = ATTR_BODY_DEFAULT
		if attr:
			self.setAttributes(attr, prior)
		self.childs = []
		
	def setAttributes(self, attr, prioritet):
		flag = False
		if attr:
			i = 0
			for k, v in attr.items():
				if self.own_attr:				
					for dict_attr in self.own_attr:
						if k in dict_attr[0].keys():
							flag = True	
							if prioritet > dict_attr[1]:
								self.own_attr[i][0] = {k:v}
								self.own_attr[i][1] = prioritet
								break
						i = i+1
					if not flag:
						self.own_attr.append([{k:v}, prioritet])
				else:
					self.own_attr.append([{k:v}, prioritet])
				flag = False
				i = 0
				
				
	def getAttributes(self):			
		return self.own_attr
		
	def getAttributess(self):
		dc = self.getAttributes()
		out_dict = {}
		for i in dc:
			for k, v in i[0].items():
				out_dict[k] = v						
		return out_dict

class ObjectCSS():
	def __init__(self, name, attr, parent, text, all_attr):
		self.name = name
		self.text = text
		self.parent = parent
		self.attributes = all_attr
		self.parent_attr = parent.own_attr
		prior = 20
		self.own_attr = []
		if attr:
			self.setAttributes(attr, prior)
		self.childs = []
		
	def setAttributes(self, attr, prioritet):
		flag = False
		if attr:
			i = 0
			for k, v in attr.items():
				if self.own_attr:
					for dict_attr in self.own_attr:
						
						if k in dict_attr[0].keys():
							flag = True
							if prioritet > dict_attr[1]:
								self.own_attr[i][0] = {k:v}
								self.own_attr[i][1] = prioritet
								flag = True
								break
						i = i + 1
					if not flag:
						self.own_attr.append([{k:v}, prioritet])
				else:	
					self.own_attr.append([{k:v}, prioritet])
				flag = False
				i = 0
		

		
			
	def getAttributes(self):
		parent = copy.deepcopy(self.parent_attr)
		for parent_property in parent:
			for own_property in self.own_attr:
				if parent_property[0].keys() == own_property[0].keys():
					break
			else:
				self.own_attr.append(parent_property)				
		return self.own_attr
			
	def __repr__(self):
		return self.name
		
	def getAttributess(self):
		dc = self.getAttributes()
		out_dict = {}
		for i in dc:
			for k, v in i[0].items():
				out_dict[k] = v						
		return out_dict
		
class CssFileElement():
	def __init__(self, name, attr, parents):
		self.name = name
		self.attr = attr 
		self.parents = parents
		

def create_property_dict(elem_name,  style_string, text, all_attr, parent=None):
	''' функция для создания объекта ObjectCSS по имени элемента и строке, описывающей стиль элемента '''
	attr_dict = dict()
	#отделяем свойства и их значения, возвращаем список кортежей (property, value)
	if style_string:
		attr = re.findall(r'\s?([\w,-]+)\s?:\s?([\w,\d,-,%,]+);?', style_string)
		#переводим кортежи в один словарь
		for i in attr:
			if i[0].strip() == 'display' and i[1].strip() == 'none':
				return None
				
			attr_dict[i[0]] = i[1]
		#создаем объект ObjectCSS, который хранит имя элемента и словарь свойств и их значений
		if elem_name.strip() == 'body':
			css_object = GeneralObjectCSS(elem_name.strip(), attr_dict, text, all_attr)
		else:
			css_object = ObjectCSS(elem_name.strip(), attr_dict, parent, text, all_attr)
		return css_object
	else:
		if elem_name.strip() == 'body':
			css_object = GeneralObjectCSS(elem_name.strip(), attr_dict, text, all_attr)
		else:
			css_object = ObjectCSS(elem_name.strip(), None, parent, text, all_attr)
		return css_object
	
def create_CSSOM_tree(element_body):
	''' функция создания корневого css объекта '''
	attr = element_body.getAttributes()
	elem_name = element_body.getTagName()
	if attr:
		for i in attr:	
			for k, v in i.getAttribute().items():	
				if k.strip() == 'style':
					CSS_Tree = create_property_dict(elem_name, v, element_body.getText(), element_body.attr)
					return CSS_Tree

	CSS_Tree = create_property_dict(elem_name, None, element_body.getText(), element_body.attr)
	return CSS_Tree
	
			
def create_CSSOM_elem(element_dom, parent_cssom):
	''' функция создания css-элемента '''
	attr = element_dom.getAttributes()
	elem_name = element_dom.getTagName()
	if attr:
		for i in attr:	
			for k, v in i.getAttribute().items():	
				if k.strip() == 'style':
					CSS_Obj = create_property_dict(elem_name, v,element_dom.getText(), element_dom.attr, parent_cssom)
					return CSS_Obj
					
	CSS_Obj = create_property_dict(elem_name, None, element_dom.getText(), element_dom.attr, parent_cssom)
	return CSS_Obj
			

def search_child_cssom(element_dom, element_cssom):
	''' рекурсивная функция поиска и создания дочерних css-элементов.
		Принимает 2 аргумента: корневой элемента DOM(элемент body) и соответствующий ему css-объект. Возвращает корневой элемент css - полное дерево с видимыми html-элементами'''
	#childs = element_dom.getChildNodes()
	childs = element_dom.childs
	if childs:
		for i in childs:
			if type(i) == str:
				element_cssom.childs.append(i)
			else:
				if i.getTagName() in ['style', 'meta', 'link', 'script']:
					pass
				else:
					#print(i.node_name)
					cssom = create_CSSOM_elem(i, element_cssom)
					if cssom:
						element_cssom.childs.append(cssom)
						search_child_cssom(i, cssom)					
	else:
		return None


def create_css_object(name_css_element, body_css_element):
	''' функция для создания объекта CssFileElemet '''
	attr_dict = dict()
	parents = []
	if body_css_element:
		attributes = re.findall(r'\s?([\w,-]+)\s?:\s?([\w,\d,-,%,#]+);?', body_css_element)
		name_css_element = re.findall(r'[\w,\.,-,_,#]+', name_css_element.strip())
		#print(name_css_element)
		if name_css_element:
			name_elem = name_css_element[::-1][0]
			length = len(name_css_element) 
			if length > 1:
				for i in name_css_element[length-2::-1]:
					
					if i[0] == '#':
						parents.append({'id':i[1:]})
						continue
					elif i[0] == '.':
						parents.append({'class':i[1:]})
						continue
					else:
						parents.append({'tag':i})
				if parents[-1].keys() != 'body':
		
					parents.append({'tag':'body'})		
			else:
				parents = [{'tag':'body'}]
			if attributes:
				for attr in attributes:
					attr_dict[attr[0].strip()] = attr[1].strip()
			obj = CssFileElement(name_elem, attr_dict, parents)
			return obj
					
					


def separate_on_tags(data):
	'''функция для парсинга css-файла. Возвращает список элементов CssFileElement для сравнения с видимыми DOM-элементами и создания дерева отображения '''
	#ищем все элементы и все их значения
	tags = re.findall(r'([\w,\d,\.,#,-,_,:,\s]+)\{([^\}]+)\}', data)
	out_list = []
	out_name_tags = []
	for i in tags:
		#создаем список из CssFileElement
		obj = create_css_object(i[0], i[1])
		if obj:
			out_name_tags.append(obj.name)
			out_list.append({obj.name:obj})
	return out_list, out_name_tags

'''for i in separate_on_tags(data):
	print(i.name, i.attr)'''
	
