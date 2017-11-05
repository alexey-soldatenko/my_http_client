from PyQt5 import QtCore, QtWidgets, QtGui
import sys
import re
from dom_tree.parser import *
from dom_tree.dom_tree import *
from css_tree.parser_css import *
from render_tree.render_tree import *
from query.new_query import new_query
from win_qt.flow_layout import NewFlowLayout
import itertools


class MyLabel(QtWidgets.QLabel):
	def __init__(self, string, main_window, parent=None):
		super(MyLabel, self).__init__(string, parent)
		self.main_window = main_window
		
		
	def setLink(self, address):
		self.link = address
		
	def show_click(self, event):
		new_link = self.link
		self.main_window.jump_to_link(new_link)
		#print(self.link)


STRING_TAGS = ['a', 'img', 'strong', 'sup', 'abbr', 'textarea', 'acronym']

HEADERS_TAGS = ['h1', 'h2', 'h3']

SPECIAL_CHAR = {'&copy;':'\u00A9','&copy':'\u00A9','&lt;':'<', '&gt;':'>', 					'&#34;':'"', '&#39;':"'", '&trade;':'\u2122', '&#xD6;':					'\u00d6', '&#x56FD;':'\u56FD', '&#x3BB;':'\u03bb', 
				'&#xA0;':'\u00a0', '&#xA9;':'\u00a9', '&#xAE;':'\u00ae', '&#x2013;':'\u2013', '&#x201D;':'\u201d',
				'&#x201C;':'\u201c', '&#xE9;':'\u00e9', '&#x2019;':'\u2019',
				'&ndash;':'-'}
				
UNICODE_CODE = {'208b':'\u208b', '2da0':'\u2da0', 'b7c':'\u0b7c', 'b68':'\u0b68', '16d0':'\u16d0', 'b46':'\u0b46'}


def convert_dict_in_str(tag_dict):
	attr = ''
	for k, v in tag_dict.items():
		if k == 'color':
			attr += ' '+k+':'+v+';'
	return attr

def delete_scretch(lay):
	if isinstance(lay, QtWidgets.QLayout):
		num = lay.count()
		for i in range(num-1):
			if lay.itemAt(i):
				if lay.itemAt(i).spacerItem():
					lay.removeItem(lay.itemAt(i))
					delete_scretch(lay)
				elif isinstance(lay.itemAt(i).widget(), QtWidgets.QWidget):
					delete_scretch(lay.itemAt(i).layout())
				elif lay.itemAt(i).layout():
					delete_scretch(lay.itemAt(i))
		return lay



def search_flow_box(lay):
	''' функция для поиска в дочерних элементах растягивающегося блока 
		NewFlowLayout'''
	new_ls = []
	if isinstance(lay, NewFlowLayout):
		new_ls.append(lay.itemList)
	x = lay.findChildren(NewFlowLayout)
	for i in x:
		new_ls.append(i.itemList)
	new_ls = list(itertools.chain.from_iterable(new_ls))
	return new_ls
	

	
def create_container_block(element):
	''' функция для создания основного виджета элемента render-tree'''
	box = QtWidgets.QVBoxLayout()
	box.setSpacing(5)
	box.setContentsMargins(0,0,0,0)
	widget = QtWidgets.QWidget()
	widget.setLayout(box)
	return widget
	

def getLink(elem):
	''' функция для извлечения из элемента render-tree значения 
		аттрибута href'''
	for i in elem.attributes:
		#print(i.attr_name, i.attr_value)
		if i.attr_name == 'href':
			return i.attr_value
	
	
def search_unicode_char(word):
	''' функция определения соответствия слова юникод-символу.
		Входной параметр строка(str). Возвращает строку. Например строка "&lt;" будет заменена на симиол "<" '''
	start = word.find('&')
	end = -1
	if start != -1:
		end = word.find(';', start)
		if end == -1:
			end = len(word)-1
	if end != -1:
		unicode_char = word[start: end+1]
		if unicode_char in SPECIAL_CHAR.keys():
			new_word = word[:start]+SPECIAL_CHAR[unicode_char]+word[end+1:]
			new_word = search_unicode_char(new_word)
			return new_word
		else:
			new_word = word[:start]+word[end+1:]
			new_word = search_unicode_char(new_word)
			if new_word:
				return new_word
			else:
				return None
	else:
		return word
	
def string_object(text, main_window):
	''' функция для создания строкового объекта. Входные параметры:
		текст и ссылка на окно приложения. Функция дробит текст по словам,
		каждому слову соответствует свой QLabel. Возвращает список Qlabel.'''
	ls = []	
	for word in text.split(' '):
		if not (word == ''):
			if word in UNICODE_CODE.keys():
				word = UNICODE_CODE[word]
			else:
				new_word = search_unicode_char(word)
				if new_word:
					word = new_word
				else:
					continue					
			label = MyLabel(word+' ', main_window)
			label.setTextFormat(QtCore.Qt.PlainText)
			label.setFont(QtGui.QFont('Arial', 14))
			label.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)	
			ls.append(label)

	
	return ls

	
def loop_set_elem_in_window(element, main_window):
	''' рекурсивная функция обработки render-tree элементов, создания соответствующих виджетов для отображения на экране. Входные параметры:
	body-элемент render-tree и виджет главного окна.'''
	
	child_is_string = False
	
	if element.childs:
		widget = create_container_block(element)
		lay = widget.layout()
		horiz_layout = None
		for i in element.childs:
			if isinstance(i, str):
				if horiz_layout and child_is_string:
					new_label = string_object(i, main_window)	
					if new_label:
						for lab in new_label:				
							horiz_layout.addWidget(lab)	
				else:
					horiz_layout = NewFlowLayout()
					horiz_layout.setContentsMargins(0,0,0,0)
					lay.addLayout(horiz_layout)
					new_label = string_object(i, main_window)
					if new_label:
						for lab in new_label:				
							horiz_layout.addWidget(lab)
				child_is_string = True		
			elif i.name == 'p':
				graf_elem = loop_set_elem_in_window(i, main_window)	
				
				lay.addWidget(graf_elem)
				child_is_string = False
				
			elif i.name in HEADERS_TAGS:
				graf_elem = loop_set_elem_in_window(i, main_window)
				
				lay.addWidget(graf_elem)
				graf_elem.setStyleSheet('font-weight:bold;')
				child_is_string = False
					
			elif i.name in STRING_TAGS:
				if horiz_layout and child_is_string:
					graf_elem = loop_set_elem_in_window(i, main_window)
					x = search_flow_box(graf_elem.layout())
					if x:
						for j in x:
							new_widget = j.widget()
							horiz_layout.addWidget(new_widget)
							if i.name == 'a':
								href = getLink(i)
								new_widget.setLink(href)
								new_widget.setToolTip(href)
								new_widget.setStyleSheet('text-decoration: underline; color: blue;')
								new_widget.mousePressEvent = new_widget.show_click
				else:
					horiz_layout = NewFlowLayout()
					horiz_layout.setContentsMargins(0,0,0,0)
					graf_elem = loop_set_elem_in_window(i, main_window)
					lay.addLayout(horiz_layout)
					
					x = search_flow_box(graf_elem.layout())
					if x:
						
						for j in x:
							new_widget = j.widget()
							horiz_layout.addWidget(new_widget)
							
							if i.name == 'a':
								href = getLink(i)
								new_widget.setLink(href)
								new_widget.setToolTip(href)
								new_widget.setStyleSheet('text-decoration: underline; color: blue;')
								new_widget.mousePressEvent = new_widget.show_click
										
				child_is_string = True		
			else:
				graf_elem = loop_set_elem_in_window(i, main_window)
				lay.addWidget(graf_elem)
				child_is_string = False

		return widget
		
	else:
		widget = create_container_block(element)
		return widget	
	
history_list=[]


class WebPage(QtWidgets.QFrame):
	''' основной класс для отображения Web-страницы на экране '''
	def __init__(self, address, parent=None):
		super(WebPage, self).__init__(parent)
		self.setWindowTitle('Very Simple Browser')
		if (not history_list or 
				history_list[len(history_list)-1] != address):
			history_list.append(address)
		request = re.match(r'([a-z]+://)?(?P<host>[\w,\d,\.,\-,_]+\.[\w]{0,4})?/?(?P<address>[\w,\d,\.,\-,_,#,%,/,?,=,&,;]+)?', address)
		if request:
			host = request.groupdict()['host']
			if not re.match('^www.', host):
				host = 'www.'+host
		self.host = host
		self.resize(550, 350)
		self.setMinimumSize(300, 150)
		self.window_position()
		self.setStyleSheet("background:white")
		
		#главный виджет, общая область
		self.all_box = QtWidgets.QVBoxLayout()
		self.all_box.setSpacing(0)
		self.all_box.setContentsMargins(0,0,0,0)
		
		#комплектующие для верхней панели
		self.address_line = QtWidgets.QLineEdit(address)

		self.search_button = QtWidgets.QPushButton()
		self.search_button.clicked.connect(self.search_new_address)
		self.search_button.setFixedSize(30, 25)
		ImgRef = QtGui.QPixmap('img/refresh.png')
		self.search_button.setIcon(QtGui.QIcon(ImgRef))
		self.search_button.setIconSize(QtCore.QSize(24,24))
		
		
		self.back_button = QtWidgets.QPushButton()
		self.back_button.setFixedSize(30, 25)
		self.back_button.clicked.connect(self.jump_to_back)
		ImgBack = QtGui.QPixmap('img/back_black.png')
		self.back_button.setIcon(QtGui.QIcon(ImgBack))
		self.back_button.setIconSize(QtCore.QSize(24,24))
		

		self.search_button.setStyleSheet('background: #DCDCDC;')
		self.back_button.setStyleSheet('background: #DCDCDC;')

		#непосредственно верхняя панель
		self.search_box = QtWidgets.QVBoxLayout()
		self.search_box.setSpacing(0)
		self.top = QtWidgets.QWidget()
		self.top_layout = QtWidgets.QHBoxLayout()
		self.top_layout.setSpacing(0)
		
		self.top_layout.addWidget(self.back_button)
		self.top_layout.addWidget(self.address_line)
		self.top_layout.addWidget(self.search_button)
		
		self.top.setLayout(self.top_layout)
		self.top.setStyleSheet('border-bottom: 1px solid gray;')
		
		self.search_box.addWidget(self.top)
	
		#виджет для области просмотра
		self.body_box = QtWidgets.QHBoxLayout()
		self.body_box.setSpacing(0)
		self.widget = QtWidgets.QWidget()
		
		
		
		self.scrollArea = QtWidgets.QScrollArea()
		self.scrollArea.setStyleSheet('border: none;')
		self.scrollArea.verticalScrollBar().setStyleSheet('border: none; background:#DCDCDC;')
		self.scrollArea.setWidget(self.widget)
		self.scrollArea.setWidgetResizable(True)
		self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
		self.scrollArea.setFrameShape(self.scrollArea.NoFrame)
		
		self.body_box.addWidget(self.scrollArea)

		self.all_box.addLayout(self.search_box)
		self.all_box.addLayout(self.body_box)
		self.setLayout(self.all_box)
		self.scrollArea.setFocus()

	def window_position(self):
		''' функция для определения положения окна на экране '''
		sizeScreen = QtWidgets.QDesktopWidget().screenGeometry()
		self.move(sizeScreen.width()/2-self.width()/2, sizeScreen.height()/2-self.height()/2)

	def create_scroll(self, widget):
		''' функция для установки в виджет scrollArea блока 
			с информацией '''
		new_layout = QtWidgets.QVBoxLayout()
		new_layout.addWidget(widget)
		new_layout.setSpacing(0)
		self.widget.setLayout(new_layout)
	
	def jump_to_back(self):
		''' функция для перехода на предыдущую посещенную страницу '''
		num = len(history_list)
		if num > 1:
			history_list.pop()
			self.jump_to_link(history_list.pop())	
			
	def search_new_address(self):
		''' функция для перехода на новую или для перезагрузки 
			текущей страницы '''
		new_link = self.address_line.text()
		if new_link:
			self.jump_to_link(new_link)
			
	def jump_to_link(self, active_link):
		''' функция для перехода по ссылке. Входной параметр - 
		непосредственно ссылка '''
		if active_link:
			request = re.match(r'([a-z]+://)?(?P<host>[\w,\d,\.,\-,_]+\.[\w]{0,4})?/?(?P<address>[\w,\d,\.,\-,_,#,%,/,?,=,&,;]+)?', active_link)
			if request:
				host = request.groupdict()['host']
				if not host:
					host = self.host
				else:
					if not re.match('^www.', host):
						host = 'www.'+host
				query = request.groupdict()['address']
				if query:
					query = '/' + query
				else:
					query = '/'
				
				try:
					#отправляем новый запрос
					new_query(host, query, 'html')
				except:
					msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning,
					"Search address not found!", "Verify that the address is correct!")
					msg.resize(100, 100)
					msg.exec()
					return None
				with open('site.html', 'r') as file:
					data = file.read()
					
				#формируем дерево-dom
				html = search_html(data)
				search_child(html, data, html.enternal_start, html.enternal_end)
				set_children(html, data)
				
				#извлекаем элемент body с вместе с дочерними элементами
				body = html.getElementsByTagName('body')[0]
				
				#создаем новое дерево-dom, но уже с учётом аттрибутов
				css_body = create_CSSOM_tree(body)
				search_child_cssom(body, css_body)
				
				''' Далее создаем дерево-css
					with open('site.css', 'r') as css:
						css_file = css.read()
				Комбинируем dom- и css-деревья
				css_style, css_tags = separate_on_tags(css_file)
				body = loop_combine_css_dom(css_body, css_style, css_tags)
				Удаляем объекты, которые имеют атрибут display:none;
				body = loop_delete_display_none_objects(body) '''
				
				#в данном случае не используем css-стили
				body = loop_combine_css_dom(css_body, [], [])
				body = loop_delete_display_none_objects(body)
					
				self.new_window = WebPage('http://'+host+query)
				box = loop_set_elem_in_window(body, self.new_window)
				self.new_window.create_scroll(box)
				self.new_window.show()
				self.close()		
			else:
				msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information,
					"Link is broken!", "Link is broken!")
				msg.resize(100, 100)
				msg.exec()
				return None	
		else:
			pass


class MainWindow(QtWidgets.QWidget):
	''' класс для отображения поискового окна '''
	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)
		self.setWindowTitle('Very Simple Browser')
		self.resize(550, 320)
		self.setStyleSheet("background: white")
		self.window_position()
		self.all_box = QtWidgets.QVBoxLayout()
		self.search_box = QtWidgets.QHBoxLayout()
		self.all_box.insertStretch(1)
		
		self.logo = QtWidgets.QLabel("Мой http-клиент")
		self.logo.setFont(QtGui.QFont('SansSerif', 18))
		self.all_box.addWidget(self.logo, 0, QtCore.Qt.AlignCenter)
		
		
		self.all_box.addLayout(self.search_box)
		self.search_line = QtWidgets.QLineEdit()
		self.search_line.setPlaceholderText("Введите http-запрос") 
		self.search_line.setFixedWidth(self.width()*0.75)
		
		self.search_button = QtWidgets.QPushButton('Старт')
		self.search_button.clicked.connect(self.search_Web)
		self.search_button.setFixedWidth(self.width()*0.2)
		self.search_button.setStyleSheet('background: #4682B4;')
		self.search_box.addWidget(self.search_line)
		self.search_box.addWidget(self.search_button)
		self.all_box.addStretch(-1)
		self.setLayout(self.all_box)
		
	def resizeEvent(self, event):
		self.search_line.setFixedWidth(self.width()*0.75)
		self.search_button.setFixedWidth(self.width()*0.2)
	
	def window_position(self):
		''' функция для определения положения окна на экране '''
		sizeScreen = QtWidgets.QDesktopWidget().screenGeometry()
		self.move(sizeScreen.width()/2-self.width()/2, sizeScreen.height()/2-self.height()/2)
		
	def search_Web(self):
		''' функция для поиска и перехода на страницу указанного 
		в поисковой строке адреса.'''
		if self.search_line.text():
			search_string = ''
			search_string = self.search_line.text()
			request = re.match(r'[a-z]+://(?P<host>[\w,\d,\.,\-,_]+)/?(?P<address>[\w,\d,\.,\-,_,#,%,/]+)?', search_string)
			host = 'www.' + request.groupdict()['host']
			query = request.groupdict()['address']
			if query:
				query = '/' + query
			else:
				query = '/'
			#print(query)
			try:
				new_query(host, query, 'html')
			except:
				msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning,
				"Search address not found!", "Verify that the address is correct!")
				msg.resize(100, 100)
				msg.exec()
				return None
			with open('site.html', 'r') as file:
				data = file.read()
			
			#формируем дерево-dom	
			html = search_html(data)
			search_child(html, data, html.enternal_start, html.enternal_end)
			set_children(html, data)
			
			#извлекаем элемент body с вместе с дочерними элементами
			body = html.getElementsByTagName('body')[0]
			
			#создаем новое дерево-dom, но уже с учётом аттрибутов
			css_body = create_CSSOM_tree(body)
			search_child_cssom(body, css_body)
			
			''' Далее создаем дерево-css
					with open('site.css', 'r') as css:
						css_file = css.read()
				Комбинируем dom- и css-деревья
				css_style, css_tags = separate_on_tags(css_file)
				body = loop_combine_css_dom(css_body, css_style, css_tags)
				Удаляем объекты, которые имеют атрибут display:none;
				body = loop_delete_display_none_objects(body) '''
			
			#в данном случае не используем css-стили
			body = loop_combine_css_dom(css_body, [], [])
			body = loop_delete_display_none_objects(body)
				
			self.new_window = WebPage('http://'+host+query)
			box = loop_set_elem_in_window(body, self.new_window)
			self.new_window.create_scroll(box)
			self.new_window.show()
			self.close()

		else:
			pass
