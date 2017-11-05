import re
from dom_tree.dom_tree import *

	
DONT_CLOSED_TAGS = ['area', 'base', 'br', 'col', 'command', 'embed', 'hr', 'img', 'input', 'keygen', 'link', 'meta', 'param', 'source', 'track', 'wbr']


	
def name_tag(tag):	
	''' функция определения имени и аттрибутов тега.
		Возвращает имя тега, список аттрибутов, тип(открыт/закрыт)'''
	if re.findall(r'<\s?/\s?([\w,0-9]+)>', tag):
		name = re.findall(r'<\s?/\s?([\w,0-9]+)>', tag)[0]
		return name.lower(), [], 'closed'
	if tag[1] == '!':
		end = tag.find('-->')+2
		name = tag[4:end]
		return name.lower(), [], 'comment'
	#ищем пробельный символ, после определяем есть ли у тега атрибуты
	pattern_sp = re.compile(r'\s')
	space = pattern_sp.search(tag)
	sp = -1
	if space:
		sp = space.span()[0]
	if sp != -1:
		name = re.findall(r'<([\w,\s,\d]+)\s+(?:[\w,\-,\s]+)?[a-z,\:,\-]+\s?=\s?', tag)
		if not name:
			name = tag[1:-1].replace(' ', '').replace('/', '')
		else:
			name = name[0].strip().replace(' ', '').replace('/', '')
		attr = re.findall(r'([\w,\:,\-]+)\s?=\s?[",\']([\w,\d,:,;,\.,/,\s,&,\-,%,_,?,=]+)[",\']', tag[sp:-1])
		if name == 'scriptasync':
			name = 'script'
		return name.lower(), attr, 'open'
	else:
		name = tag[1:-1].strip().replace('/', '')
		return name.lower(), [], 'open'	
	
		
def search_pair_tag(tag_name, string, index_start):
	''' функция поиска парного закрывающегося тега.
		Возвращает индекс начала и конца содержимого тега, если найден закрывающийся тег, или None в обратном случае'''
	j = 0
	for index in range(index_start, index_start+len(string[index_start:])):
		
		if string[index] == '<':
			end = string.find('>', index)
			tag_pair, attr, pair_type  = name_tag(string[index:end+1])
			#если мы определили закрывающий тег, проверяем есть ли у нас дочерние элементы с тем же именем, если нет или они уже закрыты, считаем что нашли парный тег
			if tag_name == tag_pair and pair_type == 'closed' and j == 0:
				return index_start, index, end
			#если мы определили еще один подобный тег, пропускаем его, он - дочерний 
			elif tag_name == tag_pair and pair_type == 'open':
				j = j + 1
			#если мы определили закрывающий тег, проверяем есть ли у нас дочерние элементы с тем же именем, считаем, что закрыли дочерний элемент
			elif tag_name == tag_pair and pair_type == 'closed' and j > 0:
				j = j - 1
	return None
	
	
def search_child(parent, string, start, end):
	''' функция поиска и установки дочерних элементов родительскому'''
	index = start
	if parent.getTagName() == 'script':
		return parent
	#ищем тег
	for i in range(start, start+len(string[start:end])-1):
		index_start = string.find('<', index)
		if index_start == -1:
			break
		
		if string[index_start+1] == '!':
			
			index_end = string.find('-->', index_start)+3
			tag_name, attr, tag_type = name_tag(string[index_start:index_end+1])
			parent.setComment(Comment(tag_name, index_start, index_end))
			#print(string[index_start:index_end])
			index = index_end
			
		else:
			index_end = string.find('>', index_start)
			#проверяем что тег типа 'open'
			tag_name, attr, tag_type = name_tag(string[index_start:index_end+1])
			#print(tag_name)
			if tag_type == 'open':	
				#ищем парный закрывающийся тег
				if tag_name in DONT_CLOSED_TAGS:
					parent.append_child(HtmlElement(parent, tag_name, index_start, index_end))
					index = index_end
				else:
					#print(tag_name)
					if search_pair_tag(tag_name, string, index_end):
						enternal_start, enternal_end, external_end = search_pair_tag(tag_name, string, index_end)
						index = external_end
						#создаем новый HtmlElement и добавляем его в список дочерних элементов
						child = HtmlElement(parent, tag_name, index_start, external_end, enternal_start, enternal_end)
						parent.append_child(child)
						if attr:
							for j in attr:
								#print(tag_name, j[0], j[1])
								child.appendAttributes(j[0], j[1])				
	
	return parent
			
def search_html(string):
	''' функция поиска в контексте тега <html> и его содержимого.
		Создание объекта типа DocumentElement - корня дерева DOM'''
	index = 0
	index_start = string.find('<html', index)
	if index_start == -1:
		return None
	index_end = string.find('>', index_start)
	tag_name, attr, tag_type = name_tag(string[index_start:index_end+1])
	content_start, content_end, ext_end = search_pair_tag(tag_name, string, index_end)
	html = DocumentElement(index_start, ext_end, content_start, content_end)
	return html


def search_text_in_tag(element, string):
	''' функция поиска текста в содержимом тега и присваивания его 
		атрибуту text элемента типа HtmlElement DocumentElement'''
	#list_child_range - список с данными о расположении внешнего начала и конца дочерних элементов, поиск текста ведется между этими значениями
	list_child_range = [element.enternal_start+1]
	if element.comment:
		for i in element.comment:
			list_child_range.append(i.external_start)
			list_child_range.append(i.external_end+1)
	list_text = []
	#если есть дочерние элементы, следует указать их внешний диапазон, чтобы обойти их внутренне содержимое
	if element.getChildNodes():
		for i in element.getChildNodes():
			list_child_range.append(i.external_start)
			list_child_range.append(i.external_end+1)
		list_child_range.append(element.enternal_end)
		list_child_range.sort()
		#list_child_range имеет четное число значений, делаем шаг цикла 2, чтобы получить начало и конец диапазона для поиска текста
		index_child = 0
		length = len(list_child_range)
		for i in range(0, length-1, 2):
			if i != length-1 :
				text = re.findall(r'[\s\S]+', string[list_child_range[i]:list_child_range[i+1]])
				if text:
					for j in text:
						tags_start = j.find('<')
						if tags_start != -1:
							tags_end = j.find('>')
							if tags_end != -1:
								j = j[:tags_start] + j[tags_end+1:]
						element.setText(j.strip(), i-1)
						element.setChilds(j.strip())
				#else:
				
				if index_child < len(element.getChildNodes()):	
					element.setChilds(element.getChildNodes()[index_child])
				index_child = index_child+1	
					
	# если дочерних элементов нет, ищем текст между внутренними границами самого тега
	else:
		list_child_range.append(element.enternal_end)
		list_child_range.sort()
		text = re.findall(r'[\s\S]+', string[list_child_range[0]:list_child_range[1]])
		if text:
			for j in text:
				element.setText(j, 0)
				element.setChilds(j.strip())
	



def set_children(parent, data):
	''' рекурсивная функция установки дочерних элементов в параметр 
	child_nodes родителя'''
	if parent.getChildNodes():
		for i in parent.getChildNodes():
			if (i.enternal_start != '' and i.enternal_end != ''):
				search_child(i, data, i.enternal_start, i.enternal_end)
				search_text_in_tag(i, data)
				set_children(i, data)
	else:
		pass

def look_tree(document):
	''' рекурсивная функция просмотра содержимого объекта типа DocumentElement или HtmlElement'''
	if document.getChildNodes():
		for i in document.getChildNodes():
			print(i.getTagName(), i.parent_element.getTagName(), i.getText())
			print(i.comment)
			look_tree(i)
	else:
		pass		
