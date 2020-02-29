import socket,threading
c = socket.socket()
c.connect(('127.0.0.1',5554))
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
	print('reading end client')

def writting():
	global c,ex
	while ex:
		d=input()
		if d=='exit':
			c.send(bytes('exit','utf-8'))
			ex=False
		else:
			c.send(bytes(d,'utf-8'))
	print('writting end client')

t1=threading.Thread(target=reading)
t2=threading.Thread(target=writting)
t1.start()
t2.start()
t1.join()
t2.join()
c.close()
print('client closed')