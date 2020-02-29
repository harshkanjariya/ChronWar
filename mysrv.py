import socket,threading
s = socket.socket()
s.bind(('',5554))
s.listen(5)
c,addr=s.accept()
ex=True
def reading():
	global c,ex
	while ex:
		d=str(c.recv(1024),'utf-8')
		if d=='exit':
			print(d)
			ex=False
		else:
			print(d)
	print('reading end server')
def writting():
	global c,ex
	while ex:
		d=input()
		if d=='exit':
			c.send(bytes('exit','utf-8'))
			ex=False
		else:
			c.send(bytes(d,'utf-8'))
	print('writting end server')
t1=threading.Thread(target=reading)
t2=threading.Thread(target=writting)
t1.start()
t2.start()
t1.join()
t2.join()
c.close()
s.close()
print('server closed')