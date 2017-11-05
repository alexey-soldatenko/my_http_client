from socket import *
import re 

def new_query(host, query, flag):
	''' функция отправки запроса на сервер и записи его ответа в файл.
		Входные параметры: имя хоста, адрес к файлу или директории, флаг
		вида "html" или "css" для определения файла для записи. 
		Возвращает None.'''
	start_string = 'GET %s HTTP/1.1\r\n' %(query)
	headers = 'Host: %s\r\n\r\n' %(host)
	client_message = start_string+headers
	print(client_message)
	
	#сщздаём сокет, устанавливаем соединение, передаем http-сообщение
	tcp_socket = socket(AF_INET, SOCK_STREAM)
	tcp_socket.connect((host, 80))
	tcp_socket.sendall(client_message.encode('utf-8'))
	
	data = b''
	#устанавливаем значение таймаута
	tcp_socket.settimeout(2.5)
	while True:
		try:
			new_data = tcp_socket.recv(1024)
			if not new_data:
				tcp_socket.close()
				break
			data += new_data
		except:
			break
	tcp_socket.close()
	'''если содержание принятых данных не превышает 500 байтов, 
	то вероятно мы получили одни заголовки, без тела сообщения.'''
	if len(data) < 500:
		data = data.decode('utf-8')
		#в заголовках ищем атрибут Content-L(l)ength
		content = re.findall(r'Content-.ength: (\d+)', data)
		if content:
			content_length = content[0]
			'''если размер тела сообщения 0, формируем тело исходя 
			из значения заголовков'''
			if content_length == '0':
				info = re.findall(r'(HTTP/1.1 [\d,\w,\s]+)\n', data)[0]
				location = re.findall(r'(.ocation: [\w,:,/,\.,\-,_]+)', data)[0]
				new_content = "<html>\
								<body>\
								<h1>Error! Look yet and try else.</h1>\
								<p>%s</p>\
								<p>%s</p>\
								</body>\
								</html>" % (info, location)
				data = data + new_content		
			with open('site.html', 'w') as html_file:
				html_file.write(data)	
	else:
		if flag == 'html':
			with open('site.html', 'w') as html_file:
				html_file.write(data.decode('utf-8'))
		elif flag == 'css':
			with open('site.css', 'w') as css_file:
				css_file.write(data.decode('utf-8'))
			

