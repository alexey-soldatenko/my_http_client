		
def find_parents(dom_obj, parent_name, prior):
	''' рекурсивная функция поиска требуемого родительского элемента.
		Возвращается флаг поиска(True/False), приоритет и искомый родитель'''
	if dom_obj.name != 'body':
		parent = dom_obj.parent
		if parent.name == parent_name:
			return True, prior+1, parent
		else:
			flag, prior, parent = find_parents(dom_obj.parent, parent_name, prior)
	else:
		if dom_obj.name == parent_name:
			return True, prior+1, 'body'
		else:
			return False, prior-1, 'body'
	return flag, prior, parent


def search_name_in_css_tags(dom_elem, kind, css_style, css_tags):
	flag = True
	prior = 0
	if kind in css_tags:	
		
		for css in css_style:
			for css_name, css_value in css.items():
				#ищем в списке css-объектов элемент с тем же именем что и объект dom
				if css_name == kind:
					#если у элемента css есть список родителей, ищем соответствие у dom-элемента
					if css_value.parents:
						for parent in css_value.parents:
							if flag:	
								key = ''
								parent_name = ''
								for k, v in parent.items():
									key = k
									parent_name = v
								#если родитель имеет статус "тег", ищем родитель-тег с тем же именем
								if key == 'tag':
									flag, prior, parent = find_parents(dom_elem, parent_name, 1)
									#если нашли соответствие вернули в flag True, иначе False
									if not flag:
										break							
						if flag:	
							css_property = css_value.attr
							dom_elem.setAttributes(css_property, prior)
	return dom_elem

	
def combine(dom_elem, css_style, css_tags):
	''' функция комбинирования элемента dom с соответствующим ему css-элементом '''
	flag = True
	prior = 0
	if type(dom_elem) == str:
		return dom_elem
	else:
		kinds = [dom_elem.name]
		if dom_elem.attributes:
			for name in dom_elem.attributes:
				if name.attr_name == 'class':
					kinds.append('.'+name.attr_value)
				if name.attr_name == 'id':
					kinds.append('#'+name.attr_value) 
		for kind in kinds:
			search_name_in_css_tags(dom_elem, kind, css_style, css_tags)
														
	return dom_elem
	
	
def loop_combine_css_dom(dom_elem, css_style, css_tags):
	''' рекурсивная функция для комбинирования дерева dom и сss-дерева.
		Входные параметры - корневой элемент body dom-tree, сss-tree, набор тегов в css-дереве'''
	dom_elem = combine(dom_elem, css_style, css_tags)
	if type(dom_elem) == str:
		return dom_elem
	else:
		if dom_elem.childs:
			for child in dom_elem.childs:
				loop_combine_css_dom(child, css_style, css_tags)
		return dom_elem


def validate_display_none_objects(elem):
	attr = elem.getAttributess()
	for k, v in attr.items():
		if k == 'display' and v == 'none':
			return None
	return elem
	
def show_all_attr(elem):
	for i in elem.attributes:
		print(i.attr_name, i.attr_value)	
	
	
def loop_delete_display_none_objects(elem):
	if type(elem) == str:
		return elem
	else:
		elem = validate_display_none_objects(elem)
		if elem:
			if elem.childs:
				for i in elem.childs:				
					child = loop_delete_display_none_objects(i)
					if not child:
						elem.childs.remove(i)
		return elem
			
			
		

		
