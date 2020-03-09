from datetime import datetime,timedelta
import os,socket,json,threading,random
import pygame
from classes import *
from assets import *
import tkinter
# print(datetime.fromtimestamp(0))
# print(round(datetime.utcnow().timestamp()))
# d=datetime.fromtimestamp(60*60*24*365*50+60*60*24*11+60*60*18.5)
# print(d)
# print(60*60*24*365*50+60*60*24*11+60*60*18.5)
pygame.mixer.pre_init(44100, 16, 2, 4096)
pygame.init()
screen=pygame.display.set_mode([1200,600])
width,height=screen.get_size()
running=False
jumping=0
pressed=False
flip=False
colliding=False
temperzone=False
gameover=False
clock=pygame.time.Clock()
font=pygame.font.Font(None,30)
pygame.mixer.init()
coingain=pygame.mixer.Sound("coin.wav")
all_blocks=pygame.sprite.Group()
camera=[width/2,height/2]
sendimgpos=-1
sendimgtype=-1

cloudposition=[1000,500]
shopposition=[0,0]
player=Player("main",(255,0,0),60,100)
all_blocks.add(player)
class Friend():
	def __init__(self):
		self.x=0
		self.y=0
		self.img=0
		self.imgnum=0
		self.time=0
		self.holepos=0
		self.name=''
		self.temper=False
		self.flip=False
friend=Friend()
def resume_old():
	global cloudposition,shopposition,timenow
	leveldata=open('level1.data','r').read().split()
	objtype=""
	idx=0
	for l in leveldata:
		try:
			l.index(',')
			l=list(map(int,l.split(',')))
			if objtype=="cloud":
				cloudposition=l
			if objtype=="shop":
				shopposition=l
			elif objtype=="coins" or objtype=="diamonds":
				pass
		except ValueError:
			objtype=l
			idx=0

	otherdata=json.load(open('other.data','r'))
	for x in all_blocks:
		if isinstance(x,Other):
			all_blocks.remove(x)
	for o in otherdata['other']:
		obj=Other(o['n'],(0,0,0),o['x'],o['y'],coinsize,assets[o['n'].split(":")[0]])
		obj.starttime=o['s']
		obj.endtime=o['e']
		all_blocks.add(obj)
	playerdata=open('player.data','r').read()
	playerdata=playerdata.split()
	player.name,connectiontype=playerdata[0].split(',')
	player.time=int(playerdata[2])
	player.blood=int(playerdata[3])
	player.time_energy=int(playerdata[4])
	player.coins=int(playerdata[5])
	friend.name=playerdata[6]
	playerdata[1]=list(map(int,playerdata[1].split(',')))
	player.rect.x=playerdata[1][0]
	player.rect.y=playerdata[1][1]
	if connectiontype=='server':
		start_sever(friend.name)
	else:
		start_client(connectiontype,friend.name)
def newgame_load():
	global cloudposition,shopposition
	leveldata=open('level1.data','r').read().split()
	objtype=""
	timenow=datetime.utcnow().timestamp()
	for x in all_blocks:
		if isinstance(x,Other):
			all_blocks.remove(x)
	idx=0
	for l in leveldata:
		try:
			l.index(',')
			l=list(map(int,l.split(',')))
			if objtype=="cloud":
				cloudposition=l
			if objtype=="shop":
				shopposition=l
			elif objtype=="coins" or objtype=="diamonds":
				if timenow>l[0]:
					idx+=1
				obj=Other(objtype+":"+str(idx),(0,0,0),l[1],l[2],coinsize,assets[objtype])
				obj.starttime=l[0]
				if len(l)>3:
					obj.endtime=l[3]
				else:
					obj.endtime=9223372036854775
				all_blocks.add(obj)
		except ValueError:
			objtype=l
			idx=0
	player.time=60*60*24*365*50+60*60*24*11+60*60*18.5-timenow
	player.time_energy=0
	player.blood=1000
	player.rect.x=10
	player.rect.y=500

flowerimgrect.x=1050
flowerimgrect.y=570

energyrect.x=width-250
energyrect.y=30

earth=open("earth.data").read().split()
earth=[list(map(int,x.split(','))) for x in earth]
for m in earth:
	block=Wall((0,255,0),m,bricksize)
	all_blocks.add(block)

a=0.2
friction=0.6
def face(im):
	if flip:
		return pygame.transform.flip(im,True,False)
	else:
		return im
def frndface(im,fl):
	if fl:
		return pygame.transform.flip(im,True,False)
	else:
		return im
def playerpos():
	return (player.rect.x-camera[0],player.rect.y-5-camera[1],player.rect.width,player.rect.height)
def frndpos(fr):
	return (fr.x-camera[0],fr.y-5-camera[1],player.rect.width,player.rect.height)
def collisions():
	collide_list=pygame.sprite.spritecollide(player,all_blocks,False)
	global colliding,socks
	colliding=False
	for b in collide_list:
		if isinstance(b,Wall):
			if player.rect.x+player.rect.width-5>b.rect.x and player.rect.x+5<b.rect.x+b.rect.width:
				if player.rect.y+player.rect.height/2<b.rect.y+b.rect.height/2 and player.vy>0:
					colliding=True
					player.vy=0
					player.rect.y=b.rect.y-player.rect.height+1
					if not pressed:
						player.vx=player.vx*friction
						if abs(player.vx)<0.6:
							player.vx=0
				elif player.rect.y+player.rect.height/2>b.rect.y+b.rect.height/2:
					player.vy=abs(player.vy)
					player.rect.y=b.rect.y+b.rect.height
					if not pressed:
						player.vx=player.vx*friction
						if abs(player.vx)<0.6:
							player.vx=0
			elif player.rect.y+player.rect.height>b.rect.y and player.rect.y<b.rect.y+b.rect.height:
				if player.rect.x<b.rect.x and player.vx>0:
					player.vx=0
					# player.rect.x=b.rect.x-player.rect.width
				elif player.rect.x>b.rect.x and player.vx<0:
					player.vx=0
					# player.rect.x=b.rect.x+b.rect.width
		elif isinstance(b,Other):
			s=b.name.split(":")[0]
			dt=datetime.utcnow().timestamp()+player.time
			if dt>b.starttime and dt<b.endtime:
				if s=="coins" or s=="diamonds":
					b.endtime=dt
					coingain.play()
					if not isinstance(socks[0],str):
						try:
							socks[0].send(bytes('<'+b.name+';'+str(dt)+'>','utf-8'))
						except Exception as e:
							print('unable to send!',e)
					if s=="coins":
						player.coins+=1
					elif s=="diamonds":
						player.time_energy+=3600*24*365


cloudirect.x=1000
cloudirect.y=200

mainboardrect.x=width/2-150
mainboardrect.y=height/2-150

menu=True
windo=''
en=''
lb=''
startbtn=''
joinbtn=''
socks=['']
trd=['']
mytime=0
def reading(sock):
	global running,screen,player,camera,friend,all_blocks,mytime,holerect,holepos,showhole
	while running:
		d=str(sock.recv(1024),'utf-8')
		if '\n' in d and 'exit' in d.split():
			break
		frnd=''
		if '<' in d and '>' in d:
			s=d.find('<')
			e=d.find('>')
			d=d[s+1:e]
			if d=="temper":
				friend.temper=True
			if ',' in d:
				frnd=d.split(',')
				friend.flip=frnd[5]=='True'
				frnd=list(map(int,frnd[0:5]))
				if len(frnd)==5:
					friend.x=frnd[0]
					friend.y=frnd[1]
					friend.img=frnd[2]
					friend.imgpos=frnd[3]
					friend.time=frnd[4]-datetime.utcnow().timestamp()
					friend.temper=False
				else:
					print('recieved:',d)
			elif '_' in d:
				data=d.split('_')
				if data[0]=='hole':
					holerect.x=int(data[1])
					holerect.y=int(data[2])
					if flip:
						friend.holepos=-1
					else:
						friend.holepos=1
					holepos=1
					showhole=datetime.utcnow().timestamp()
			elif ':' in d:
				data=d.split(';')
				for b in all_blocks:
					if isinstance(b,Other) and b.name==data[0]:
						b.endtime=float(data[1])
	print('reading end')
serversock=''
def start_sever(n):
	global player,running,serversock,socks,trd
	serversock=socket.socket()
	serversock.bind(('',5554))
	serversock.listen(1)
	socks[0],addr=serversock.accept()
	running=True
	socks[0].send(bytes(player.name,'utf-8'))
	friend.name=str(socks[0].recv(1024),'utf-8')
	trd[0]=threading.Thread(target=reading,args=[socks[0]])
	trd[0].start()
	if n=='':
		newgame_load()
		start_game()
def start_client(ip,n):
	global player,running,socks,trd
	s=socket.socket()
	s.connect((ip,5554))
	socks[0]=s
	running=True
	friend.name=str(socks[0].recv(1024),'utf-8')
	socks[0].send(bytes(player.name,'utf-8'))
	trd[0]=threading.Thread(target=reading,args=[socks[0]])
	trd[0].start()
	if n=='':
		newgame_load()
		start_game()
def get_text_and_new():
	global windo,en
	player.name=en.get()
	windo.destroy()
	windo=''
	en=''
	start_sever('')
def connect_to_ip():
	global windo,en,serversock
	serversock=en.get()
	windo.destroy()
	windo=''
	en=''
	start_client(serversock,'')
def get_text_and_select_ip():
	global windo,en,lb,startbtn,joinbtn
	player.name=en.get()
	en.delete(0,tkinter.END)
	en.insert(0,'192.168.')
	joinbtn.grid_forget()
	startbtn.grid_forget()
	lb.configure(text="Enter Ip")
	tkinter.Button(windo,command=connect_to_ip,text="Connect").grid(row=2,column=0,columnspan=2)
def open_menu():
	global menu,running,menuview,windo,en,lb,startbtn,joinbtn,gameover
	f=pygame.font.Font(None,50)
	newtext=f.render('New Game',1,(0,0,0))
	options=f.render('Options',1,(0,0,0))
	exitm=f.render('Exit',1,(0,0,0))
	resumegame=f.render('Resume',1,(0,0,0))
	newtextrect=newtext.get_rect(centerx=width/2,centery=height/2+15)
	optionsrect=options.get_rect(centerx=width/2,centery=height/2+85)
	exitrect=exitm.get_rect(centerx=width/2,centery=height/2+160)
	resumegamerect=resumegame.get_rect(centerx=width/2,centery=height/2-50)
	resumable=True
	if open('player.data','r').read()=='':
		resumable=False
		newtextrect=newtext.get_rect(centerx=width/2,centery=height/2-50)
		optionsrect=options.get_rect(centerx=width/2,centery=height/2+50)
		exitrect=exitm.get_rect(centerx=width/2,centery=height/2+150)
	gameovr=f.render('Game Over',1,(0,255,0))
	gameovrrect=gameovr.get_rect(centerx=width/2,centery=height/2)
	titlesize=0
	titleboard=pygame.image.load('logo.png')
	titleboard=pygame.transform.scale(titleboard,(400,100))
	titleboardrect=titleboard.get_rect(centerx=width/2,centery=75)
	gameovershowing=datetime.utcnow().timestamp()
	while menu:
		if gameover:
			for e in pygame.event.get():
				if e.type == pygame.MOUSEBUTTONDOWN:
					if e.button==1:
						pass
				if e.type == pygame.QUIT:
					menu=False
			if datetime.utcnow().timestamp()-gameovershowing>2:
				gameover=False
				resumable=False
				optionsrect=options.get_rect(centerx=width/2,centery=height/2+50)
				newtextrect=newtext.get_rect(centerx=width/2,centery=height/2-50)
			screen.fill((100,255,255))
			screen.blit(gameovr,gameovrrect)
			pygame.display.update()
			clock.tick(60)
		elif not running:
			for e in pygame.event.get():
				if e.type == pygame.MOUSEBUTTONDOWN:
					if e.button==1:
						if exitrect.collidepoint(e.pos):
							menu=False
							save_game()
							return
						elif newtextrect.collidepoint(e.pos):
							windo=tkinter.Tk()
							windo.geometry("168x75")
							en=tkinter.Entry(windo)
							en.grid(row=1,column=0,columnspan=2)
							lb=tkinter.Label(windo,text="Enter Your Name")
							lb.grid(row=0,column=0,columnspan=2)
							joinbtn=tkinter.Button(windo,command=get_text_and_select_ip,text="Join")
							joinbtn.grid(row=2,column=0)
							startbtn=tkinter.Button(windo,command=get_text_and_new,text="Start New")
							startbtn.grid(row=2,column=1)
							windo.mainloop()
							gameovershowing=datetime.utcnow().timestamp()
							if not gameover:
								newtextrect=newtext.get_rect(centerx=width/2,centery=height/2+15)
								optionsrect=options.get_rect(centerx=width/2,centery=height/2+85)
								exitrect=exitm.get_rect(centerx=width/2,centery=height/2+160)
								resumegamerect=resumegame.get_rect(centerx=width/2,centery=height/2-50)
								resumable=True
						elif resumegamerect.collidepoint(e.pos):
							running=True
							resume_old()
							start_game()
							gameovershowing=datetime.utcnow().timestamp()
				if e.type == pygame.QUIT:
					menu=False
			screen.fill((100,255,255))
			cloudirect.x-=3
			if cloudirect.x<-400:
				cloudirect.x=1200
			screen.blit(cloudi,cloudirect)
			if titlesize<100:
				titlesize+=5
				tempboard=pygame.image.load('logo.png')
				tempboard=pygame.transform.scale(tempboard,(titlesize*4,titlesize))
				tempboardrect=tempboard.get_rect(centerx=width/2,centery=75)
				screen.blit(tempboard,tempboardrect)
			else:
				screen.blit(titleboard,titleboardrect)
			screen.blit(mainboard,mainboardrect)
			screen.blit(newtext,newtextrect)
			screen.blit(options,optionsrect)
			screen.blit(exitm,exitrect)
			if resumable:
				screen.blit(resumegame,resumegamerect)
			pygame.display.update()
			clock.tick(60)
def bord(n):
	if n:
		return 2
	else:
		return 0
def goto_shop():
	global player,inshop
	inshop=True
	shoptitle=font.render('Time Shop',1,(0,0,0))
	shoptitlerect=shoptitle.get_rect(centerx=width/2,centery=50)
	while inshop:
		for e in pygame.event.get():
			if e.type == pygame.KEYDOWN:
				if e.key==pygame.K_ESCAPE:
					inshop=False
			if e.type == pygame.QUIT:
				inshop=False
		screen.fill((255,100,0))
		screen.blit(shoptitle,shoptitlerect)
		pygame.display.update()
		clock.tick(60)
def goto_temperzone():
	global player,temperzone,mytime
	player.vx=0
	if not isinstance(socks[0],str):
		try:
			socks[0].send(bytes('<temper>','utf-8'))
		except Exception as e:
			print('unable to send!',e)
	temperzone=True
	bigfont=pygame.font.Font(None,90)
	myname=font.render(player.name,1,(0,0,0))
	mynamerect=myname.get_rect()
	mynamerect.x=10
	mynamerect.y=10
	temperz=font.render('Temper Zone',1,(0,0,0))
	temperzrect=temperz.get_rect(centerx=width/2,centery=30)
	day=font.render('day',1,(0,0,0))
	daypos=day.get_rect(centerx=width/2-350,centery=height-220)
	month=font.render('month',1,(0,0,0))
	monthpos=month.get_rect(centerx=width/2-250,centery=height-220)
	year=font.render('year',1,(0,0,0))
	yearpos=year.get_rect(centerx=width/2-100,centery=height-220)
	hour=font.render('hour',1,(0,0,0))
	hourpos=hour.get_rect(centerx=width/2+150,centery=height-220)
	minute=font.render('minute',1,(0,0,0))
	minutepos=minute.get_rect(centerx=width/2+250,centery=height-220)
	second=font.render('second',1,(0,0,0))
	secondpos=second.get_rect(centerx=width/2+350,centery=height-220)

	inittime=datetime.utcnow().timestamp()
	time=inittime+player.time
	dd=datetime.fromtimestamp(time).day
	mm=datetime.fromtimestamp(time).month
	yyyy=datetime.fromtimestamp(time).year
	hh=datetime.fromtimestamp(time).hour
	MM=datetime.fromtimestamp(time).minute
	ss=datetime.fromtimestamp(time).second
	pos=6
	val=0
	while temperzone:
		for e in pygame.event.get():
			if e.type == pygame.KEYDOWN:
				if e.key==pygame.K_ESCAPE:
					temperzone=False
				elif e.key==pygame.K_RETURN:
					if pos==6:
						tmp=time-inittime
						if abs(tmp-player.time)>player.time_energy:
							val=255
						else:
							player.time_energy-=abs(tmp-player.time)
							player.time=tmp
							temperzone=False
				elif e.key==pygame.K_RIGHT:
					pos=(pos+1)%7
				elif e.key==pygame.K_LEFT:
					pos=(pos+6)%7
				elif e.key==pygame.K_UP:
					if pos==0:
						time+=60*60*24
					if pos==1:
						time+=60*60*24*30
					if pos==2:
						time+=60*60*24*365
					if pos==3:
						time+=60*60
					if pos==4:
						time+=60
					if pos==5:
						time+=1
					dd=datetime.fromtimestamp(time).day
					mm=datetime.fromtimestamp(time).month
					yyyy=datetime.fromtimestamp(time).year
					hh=datetime.fromtimestamp(time).hour
					MM=datetime.fromtimestamp(time).minute
					ss=datetime.fromtimestamp(time).second
				elif e.key==pygame.K_DOWN:
					if pos==0:
						time-=60*60*24
					if pos==1:
						time-=60*60*24*31
					if pos==2:
						time-=60*60*24*365
					if pos==3:
						time-=60*60
					if pos==4:
						time-=60
					if pos==5:
						time-=1
					dd=datetime.fromtimestamp(time).day
					mm=datetime.fromtimestamp(time).month
					yyyy=datetime.fromtimestamp(time).year
					hh=datetime.fromtimestamp(time).hour
					MM=datetime.fromtimestamp(time).minute
					ss=datetime.fromtimestamp(time).second
			if e.type == pygame.QUIT:
				temperzone=False
		screen.fill((0,255,0))

		if val>0:
			text=font.render('Not Enough Time Energy!',1,(255,0,0))
			textpos=text.get_rect(centerx=width/2,centery=100)
			surf=pygame.Surface((textpos.width,textpos.height))
			surf.fill((0,255,0))
			surf.blit(text,(0,0,textpos.width,textpos.height))
			surf.set_alpha(val)
			screen.blit(surf,textpos)
			val-=2

		text=font.render(str(timedelta(seconds=player.time_energy)),1,(0,0,0))
		textpos=text.get_rect(centerx=energyrect.x+energyrect.width/2,centery=80)
		screen.blit(text,textpos)
		screen.blit(myname,mynamerect)
		screen.blit(temperz,temperzrect)
		screen.blit(day,daypos)
		screen.blit(month,monthpos)
		screen.blit(year,yearpos)
		screen.blit(hour,hourpos)
		screen.blit(minute,minutepos)
		screen.blit(second,secondpos)

		pygame.draw.rect(screen,(255,255,255),(width/2-400,height-200,99,99),bord(pos==0))
		text=bigfont.render(str(dd),1,(0,0,0))
		textpos=text.get_rect(centerx=width/2-350,centery=height-150)
		screen.blit(text,textpos)

		pygame.draw.rect(screen,(255,255,255),(width/2-300,height-200,99,99),bord(pos==1))
		text=bigfont.render(str(mm),1,(0,0,0))
		textpos=text.get_rect(centerx=width/2-250,centery=height-150)
		screen.blit(text,textpos)

		pygame.draw.rect(screen,(255,255,255),(width/2-200,height-200,199,99),bord(pos==2))
		text=bigfont.render(str(yyyy),1,(0,0,0))
		textpos=text.get_rect(centerx=width/2-100,centery=height-150)
		screen.blit(text,textpos)

		pygame.draw.rect(screen,(255,255,255),(width/2+100,height-200,99,99),bord(pos==3))
		text=bigfont.render(str(hh),1,(0,0,0))
		textpos=text.get_rect(centerx=width/2+150,centery=height-150)
		screen.blit(text,textpos)

		pygame.draw.rect(screen,(255,255,255),(width/2+200,height-200,99,99),bord(pos==4))
		text=bigfont.render(str(MM),1,(0,0,0))
		textpos=text.get_rect(centerx=width/2+250,centery=height-150)
		screen.blit(text,textpos)

		pygame.draw.rect(screen,(255,255,255),(width/2+300,height-200,99,99),bord(pos==5))
		text=bigfont.render(str(ss),1,(0,0,0))
		textpos=text.get_rect(centerx=width/2+350,centery=height-150)
		screen.blit(text,textpos)

		pygame.draw.rect(screen,(255,255,255),(width/2-100,height-99,199,99),bord(pos==6))
		text=bigfont.render('Jump',1,(0,0,0))
		textpos=text.get_rect(centerx=width/2,centery=height-50)
		screen.blit(text,textpos)

		screen.blit(energy,(energyrect.x,energyrect.y),(0,0,player.time_energy/(360*24*365),energyrect.height))
		pygame.draw.rect(screen,(0,0,0),energyrect,1)
		screen.blit(idle,(100,100,player.rect.width,player.rect.height))
		pygame.display.update()
		clock.tick(60)
rain=[]
for x in range(100):
	rain.append([random.randrange(0,cloudirect.width,1),random.randrange(0,200,1),random.randrange(10,30,1)/10,random.randrange(1,30,1)])
def start_game():
	global running,pressed,colliding,all_blocks,player,flip,jumping,imgcount,showhole,hole,temperzone,holepos,friend,sendimgpos,sendimgtype,cloudposition,shopposition,gameover
	cloudirect.x=cloudposition[0]
	cloudirect.y=cloudposition[1]
	while running and not temperzone:
		for e in pygame.event.get():
			if e.type == pygame.QUIT:
				running=False
				break
			if e.type == pygame.KEYDOWN:
				if e.key == pygame.K_RIGHT:
					pressed=True
					player.vx=5
					if not isinstance(socks[0],str):
						try:
							socks[0].send(bytes('<flip=False>','utf-8'))
						except Exception as e:
							print('unable to send!',e)
					flip=False
				elif e.key == pygame.K_LEFT:
					pressed=True
					if not isinstance(socks[0],str):
						try:
							socks[0].send(bytes('<flip=True>','utf-8'))
						except Exception as e:
							print('unable to send!',e)
					flip=True
					player.vx=-5
				elif e.key == pygame.K_UP:
					if colliding:
						jumping=0
						player.vy=-7
				elif e.key == pygame.K_SPACE:
					if colliding:
						jumping=0
						player.vy=-9
				elif e.key == pygame.K_ESCAPE:
					running=False
					break
				elif e.key == pygame.K_RETURN:
					if shopposition[0]+200<player.rect.x and shopposition[0]+300>player.rect.x+player.rect.width and shopposition[1]+200<player.rect.y and shopposition[1]+310>player.rect.y+player.rect.height:
						goto_shop()
				elif e.key == pygame.K_p:
					if showhole==0:
						if colliding:
							if flip:
								holepos=-1
								holerect.x=player.rect.x-100
							else:
								holepos=1
								holerect.x=player.rect.x+100
							holerect.y=player.rect.y-30
							showhole=datetime.utcnow().timestamp()
							socks[0].send(bytes('<hole_'+str(holerect.x)+'_'+str(holerect.y)+'>','utf-8'))
					else:
						showhole=0
						holepos=0
			elif e.type == pygame.KEYUP:
				if e.key == pygame.K_RIGHT:
					pressed=False
				elif e.key == pygame.K_LEFT:
					pressed=False
		screen.fill((100,255,255))
		if player.vy<0:
			player.vy+=a
		else:
			player.vy+=2*a
		if player.rect.y>5000 or player.blood<=0:
			running=False
			gameover=True
		elif player.rect.x+player.rect.width>cloudirect.x and player.rect.x<cloudirect.x+cloudirect.width:
			for r in rain:
				if r[0]+cloudirect.x>player.rect.x and r[0]+cloudirect.x<player.rect.x+player.rect.width and r[1]+cloudirect.y+r[3]>player.rect.y and r[1]+cloudirect.y<player.rect.y+player.rect.height:
					r[1]=random.randrange(0,cloudirect.height/2,1)
					r[0]=random.randrange(0,cloudirect.width,1)
					player.blood-=100
		if pressed and not colliding:
			if flip:
				player.vx=-5
			else:
				player.vx=5
		if player.rect.x-camera[0]<width/4:
			camera[0]=player.rect.x-width/4
		elif player.rect.x-camera[0]>width/2:
			camera[0]=player.rect.x-width/2
		if player.rect.y+player.rect.height-camera[1]>height*3/4:
			camera[1]=player.rect.y+player.rect.height-height*3/4
		elif player.rect.y-camera[1]<height/4:
			camera[1]=player.rect.y-height/4
		collisions()
		# cloudirect.x-=1
		pygame.draw.rect(screen,(0,255,0),(shopposition[0]-camera[0],shopposition[1]-camera[1],500,300))
		pygame.draw.rect(screen,(250,0,0),(shopposition[0]+200-camera[0],shopposition[1]+190-camera[1],100,110))
		screen.blit(flowerimg,(flowerimgrect.x-camera[0],flowerimgrect.y-camera[1],flowerimgrect.width,flowerimgrect.height))
		for r in rain:
			r[1]+=r[2]
			if r[1]>350:
				r[1]=random.randrange(0,cloudirect.height/2,1)
				r[0]=random.randrange(0,cloudirect.width,1)
			pygame.draw.rect(screen,(0,200,0),(r[0]+cloudirect.x-camera[0],r[1]+cloudirect.y+cloudirect.height/2-camera[1],r[2],r[3]))
		screen.blit(cloudi,(cloudirect.x-camera[0],cloudirect.y-camera[1],cloudirect.width,cloudirect.height))
		if showhole>0:
			now=datetime.utcnow().timestamp()
			if now-showhole>5:
				showhole=0
				holepos=0
				friend.holepos=0
			else:
				screen.blit(hole,(holerect.x-camera[0],holerect.y-camera[1],holerect.width,holerect.height))
		for block in all_blocks:
			if isinstance(block,Wall):
				block.show(brickimgs,screen,camera,earth,bricksize)
			elif isinstance(block,Other):
				block.update()
				block.show(screen,camera,datetime.utcnow().timestamp()+player.time)
			elif isinstance(block,Player):
				block.update()
		if not colliding:
			jumping=jumping+1
			if jumping<10:
				screen.blit(face(jump[0]),playerpos())
				sendimgpos=0
			elif jumping<20:
				screen.blit(face(jump[1]),playerpos())
				sendimgpos=1
			elif jumping<30 or player.vy<0:
				screen.blit(face(jump[2]),playerpos())
				sendimgpos=2
			elif player.vy<1:
				screen.blit(face(jump[3]),playerpos())
				sendimgpos=3
			else:
				screen.blit(face(jump[5]),playerpos())
				sendimgpos=5
			sendimgtype=2
		elif colliding and player.vx==0:
			if holepos==0:
				screen.blit(face(idle),playerpos())
			elif player.rect.x<holerect.x+holerect.width and holepos>0:
				if player.rect.x+player.rect.width<holerect.x+holerect.width/2:
					screen.blit(face(idle),playerpos())
				elif player.rect.x>holerect.x+holerect.width/2:
					player.rect.x=holerect.x
					temptime=datetime.utcnow().timestamp()
					goto_temperzone()
					player.time-=datetime.utcnow().timestamp()-temptime
				else:
					screen.blit(face(idle),(player.rect.x-camera[0],player.rect.y-camera[1]),(0,0,holerect.x+holerect.width/2-player.rect.x,player.rect.height))					
			elif holepos>0:
				holepos=-1
			elif player.rect.x+player.rect.width>holerect.x and holepos<0:
				if player.rect.x>holerect.x+holerect.width/2:
					screen.blit(face(idle),playerpos())
				elif player.rect.x+player.rect.width<holerect.x+holerect.width/2:
					player.rect.x=holerect.x
					temptime=datetime.utcnow().timestamp()
					goto_temperzone()
					player.time-=datetime.utcnow().timestamp()-temptime
				else:
					screen.blit(face(idle),(holerect.x+holerect.width/2-camera[0],player.rect.y-camera[1]),(holerect.x+holerect.width/2-player.rect.x,0,player.rect.width,player.rect.height))
			elif holepos<0:
				holepos=1
			imgcount=0
			sendimgtype=0
		else:
			imgcount=(imgcount+1.5)%60
			sendimgtype=1
			sendimgpos=int(imgcount/6)
			if holepos==0:
				screen.blit(face(boy[int(imgcount/6)]),playerpos())
			elif player.rect.x<holerect.x+holerect.width and holepos>0:
				if player.rect.x+player.rect.width<holerect.x+holerect.width/2:
					screen.blit(face(boy[int(imgcount/6)]),playerpos())
				elif player.rect.x>holerect.x+holerect.width/2:
					player.rect.x=holerect.x
					temptime=datetime.utcnow().timestamp()
					goto_temperzone()
					player.time-=datetime.utcnow().timestamp()-temptime
				else:
					screen.blit(face(boy[int(imgcount/6)]),(player.rect.x-camera[0],player.rect.y-camera[1]),(0,0,holerect.x+holerect.width/2-player.rect.x,player.rect.height))					
			elif holepos>0:
				holepos=-1
			elif player.rect.x+player.rect.width>holerect.x and holepos<0:
				if player.rect.x>holerect.x+holerect.width/2:
					screen.blit(face(boy[int(imgcount/6)]),playerpos())
				elif player.rect.x+player.rect.width<holerect.x+holerect.width/2:
					player.rect.x=holerect.x
					temptime=datetime.utcnow().timestamp()
					goto_temperzone()
					player.time-=datetime.utcnow().timestamp()-temptime
				else:
					screen.blit(face(boy[int(imgcount/6)]),(holerect.x+holerect.width/2-camera[0],player.rect.y-camera[1]),(holerect.x+holerect.width/2-player.rect.x,0,player.rect.width,player.rect.height))
			elif holepos<0:
				holepos=1
		if not isinstance(socks[0],str):
			try:
				socks[0].send(bytes('<'+str(player.rect.x)+','+str(player.rect.y)+','+str(sendimgtype)+','+str(sendimgpos)+','+str(int(player.time+datetime.utcnow().timestamp()))+','+str(flip)+'>','utf-8'))
			except Exception as e:
				print(socks[0])
				print('unable to send!')
				socks[0]=''
		if not friend.temper and int(friend.time)>int(player.time-5) and int(friend.time)<int(player.time+5):
			temp=0
			if friend.img==1:
				temp=boy[friend.imgpos]
				# screen.blit(frndface(boy[friend.imgpos],friend.flip),frndpos(friend))
			elif friend.img==2:
				temp=jump[friend.imgpos]
				# screen.blit(frndface(jump[friend.imgpos],friend.flip),frndpos(friend))
			else:
				temp=idle
				# screen.blit(frndface(idle,friend.flip),frndpos(friend))
			temp=frndface(temp,friend.flip)
			# screen.blit(temp,frndpos(friend))
			if not showhole==0:
				if friend.x>holerect.x+holerect.width:
					friend.holepos=1
				elif friend.x+player.rect.width<holerect.x:
					friend.holepos=-1
			if friend.holepos==0 or friend.img==2:
				screen.blit(temp,frndpos(friend))
			elif friend.holepos<0:
				if friend.x+player.rect.width<holerect.x+holerect.width/2:
					screen.blit(temp,frndpos(friend))
				elif friend.x>holerect.x+holerect.width/2:
					friend.x=holerect.x
				else:
					screen.blit(temp,(friend.x-camera[0],friend.y-camera[1]),(0,0,holerect.x+holerect.width/2-friend.x,player.rect.height))
			elif friend.holepos>0:
				if friend.x>holerect.x+holerect.width/2:
					screen.blit(temp,frndpos(friend))
				elif friend.x+player.rect.width<holerect.x+holerect.width/2:
					friend.x=holerect.x
				else:
					screen.blit(temp,(holerect.x+holerect.width/2-camera[0],friend.y-camera[1]),(holerect.x+holerect.width/2-friend.x,0,player.rect.width,player.rect.height))
		screen.blit(assets["coins"][0],(20,20,50,50))
		text=font.render('x '+str(player.coins),1,(0,0,0))
		textpos=text.get_rect()
		textpos.x=65
		textpos.y=26
		screen.blit(text,textpos)
		screen.blit(energy,(energyrect.x,energyrect.y),(0,0,player.time_energy/(360*24*365),energyrect.height))
		pygame.draw.rect(screen,(0,0,0),energyrect,1)
		# pygame.draw.rect(screen,(0,0,255),(player.rect.x-camera[0],player.rect.y-camera[1],player.rect.width,player.rect.height))
		pygame.draw.rect(screen,(255,0,0),(energyrect.x,energyrect.y+50,energyrect.width*player.blood/1000,energyrect.height))
		pygame.draw.rect(screen,(0,0,0),(energyrect.x,energyrect.y+50,energyrect.width,energyrect.height),1)
		text=font.render('Date and Time : '+datetime.fromtimestamp(datetime.utcnow().timestamp()+player.time).strftime("%d/%m/%Y %H:%M:%S"),1,(0,0,0))
		textpos=text.get_rect(centerx=screen.get_width()/2)
		screen.blit(text,textpos)
		pygame.display.update()
		clock.tick(60)
	save_game()
def save_game():
	global player,all_blocks,socks,serversock,gameover
	if not isinstance(socks[0],str):
		try:
			socks[0].send(bytes('\nexit\n','utf-8'))
			print(socks[0])
			socks[0].close()
		except:
			print('unable to send')
		socks[0]=''
	hadserver=False
	if not isinstance(serversock,str):
		serversock.close()
		hadserver=True
	f=open('player.data','w')
	if not gameover:
		f.write(player.name)
		if hadserver:
			f.write(',server\n')
		else:
			f.write(','+serversock+'\n')
		f.write(str(player.rect.x)+','+str(player.rect.y)+'\n')
		f.write(str(round(player.time))+'\n')
		f.write(str(player.blood)+'\n')
		f.write(str(round(player.time_energy))+'\n')
		f.write(str(player.coins)+'\n')
		f.write(friend.name)
	f.close()
	othr=[]
	for o in all_blocks:
		if isinstance(o,Other):
			d={'n':o.name,'x':o.rect.x,'y':o.rect.y,'s':o.starttime,'e':round(o.endtime)}
			othr.append(d)
	data={"other":othr}
	f=open('other.data','w')
	if not gameover:
		f.write(json.dumps(data,indent=1))
	f.close()
open_menu()
pygame.quit()
quit()
