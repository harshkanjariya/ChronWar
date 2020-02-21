from datetime import datetime
import os
import pygame
import json
from classes import *
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
coinsize=30
bricksize=60
clock=pygame.time.Clock()
font=pygame.font.Font(None,30)
pygame.mixer.init()
coingain=pygame.mixer.Sound("coin.wav")
all_blocks=pygame.sprite.Group()
camera=[width/2,height/2]
mytime=0

player=Player("main",(255,0,0),60,100)
all_blocks.add(player)
idle=pygame.image.load('character'+os.path.sep+'idle.png')
# idle=pygame.transform.scale(idle,(player.rect.width,player.rect.height))
boy=[]
imgcount=0
for i in range(10):
	im=pygame.image.load('character'+os.path.sep+'run'+str(i+1)+'.png')
	# im=pygame.transform.scale(im,(player.rect.width,player.rect.height))
	boy.append(im)
jump=[]
for i in range(7):
	im=pygame.image.load('character'+os.path.sep+'jump'+str(i+1)+'.png')
	# im=pygame.transform.scale(im,(player.rect.width,player.rect.height))
	jump.append(im)

assets={}
assets["coins"]=[]
for i in range(5):
	im=pygame.image.load('coins'+os.path.sep+str(i)+'.png')
	im=pygame.transform.scale(im,(coinsize,coinsize))
	assets["coins"].append(im)

assets["diamonds"]=[]
for i in range(5):
	im=pygame.image.load('diamonds'+os.path.sep+str(i)+'.png')
	im=pygame.transform.scale(im,(coinsize*2,coinsize*2))
	assets["diamonds"].append(im)

def resume_old():
	global timenow,mytime
	otherdata=json.load(open('other.data','r'))
	for x in all_blocks:
		if isinstance(x,Other):
			all_blocks.remove(x)
	for o in otherdata['other']:
		if o['v']:
			obj=Other(o['n'],(0,0,0),o['x'],o['y'],coinsize,assets[o['n'].split()[0]])
			all_blocks.add(obj)
	playerdata=open('player.data','r').read()
	playerdata=playerdata.split()
	mytime=int(playerdata[1])
	playerdata[0]=list(map(int,playerdata[0].split(',')))
	player.rect.x=playerdata[0][0]
	player.rect.y=playerdata[0][1]
def newgame_load():
	global mytime
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
			if timenow>l[0]:
				idx+=1
				obj=Other(objtype+" "+str(idx),(0,0,0),l[1],l[2],coinsize,assets[objtype])
				all_blocks.add(obj)
		except ValueError:
			objtype=l
			idx=0
	mytime=60*60*24*365*50+60*60*24*11+60*60*18.5-timenow
	player.rect.x=10
	player.rect.y=500

flowerimg=pygame.image.load('flower.png')
flowerimg=pygame.transform.scale(flowerimg,(30,30))
flowerimgrect=flowerimg.get_rect()
flowerimgrect.x=1050
flowerimgrect.y=570

showhole=0
holepos=0
hole=pygame.image.load('hole.png')
hole=pygame.transform.scale(hole,(45,150))
holerect=hole.get_rect()

brickimgs=[]
for i in range(16):
	brickimg=pygame.image.load('bricks/brick'+str(i)+'.png')
	brickimg=pygame.transform.scale(brickimg,(bricksize,bricksize))
	brickimgs.append(brickimg)

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
def playerpos():
	return (player.rect.x-camera[0],player.rect.y-5-camera[1],player.rect.width,player.rect.height)
def collisions():
	collide_list=pygame.sprite.spritecollide(player,all_blocks,False)
	global colliding
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
			s=b.name.split()[0]
			if s=="coins" or s=="diamonds":
				b.visible=False
				all_blocks.remove(b)
				del b
				coingain.play()

cloudi=pygame.image.load('cloud.png')
cloudi=pygame.transform.scale(cloudi,(360,120))
cloudirect=cloudi.get_rect()
cloudirect.x=1000
cloudirect.y=200
mainboard=pygame.image.load('menu/menuboard.png')
mainboard=pygame.transform.scale(mainboard,(300,400))
mainboardrect=mainboard.get_rect()
mainboardrect.x=width/2-150
mainboardrect.y=height/2-200
resumegame=pygame.image.load('menu/resume.png')
resumegame=pygame.transform.scale(resumegame,(160,30))
resumegamerect=mainboard.get_rect()
resumegamerect.x=width/2-80
resumegamerect.y=height/2-15-110
newgame=pygame.image.load('menu/newgame.png')
newgame=pygame.transform.scale(newgame,(200,30))
newgamerect=mainboard.get_rect()
newgamerect.x=width/2-100
newgamerect.y=height/2-15-40
options=pygame.image.load('menu/options.png')
options=pygame.transform.scale(options,(150,30))
optionsrect=mainboard.get_rect()
optionsrect.x=width/2-75
optionsrect.y=height/2-15+40
exitm=pygame.image.load('menu/exit.png')
exitm=pygame.transform.scale(exitm,(90,25))
exitrect=mainboard.get_rect()
exitrect.x=width/2-45
exitrect.y=height/2-12+110
menu=True
def open_menu():
	global menu,running
	while menu:
		for e in pygame.event.get():
			if e.type == pygame.MOUSEBUTTONDOWN:
				if e.button==1:
					p=pygame.mouse.get_pos()
					if p[0]>exitrect.x and p[1]>exitrect.y and p[0]<exitrect.width+exitrect.x and p[1]<exitrect.height+exitrect.y:
						menu=False
						save_game()
						return
					elif p[0]>newgamerect.x and p[1]>newgamerect.y and p[0]<newgamerect.width+newgamerect.x and p[1]<newgamerect.height+newgamerect.y:
						running=True
						newgame_load()
						start_game()
					elif p[0]>resumegamerect.x and p[1]>resumegamerect.y and p[0]<resumegamerect.width+newgamerect.x and p[1]<resumegamerect.height+resumegamerect.y:
						running=True
						resume_old()
						start_game()
			if e.type == pygame.QUIT:
				menu=False
		screen.fill((100,255,255))
		cloudirect.x-=3
		if cloudirect.x<-400:
			cloudirect.x=1200
		screen.blit(cloudi,cloudirect)
		screen.blit(mainboard,mainboardrect)
		screen.blit(newgame,newgamerect)
		screen.blit(options,optionsrect)
		screen.blit(exitm,exitrect)
		screen.blit(resumegame,resumegamerect)
		pygame.display.update()
		clock.tick(60)
def goto_temperzone():
	global temperzone,mytime
	player.vx=0
	temperzone=True
	bigfont=pygame.font.Font(None,90)
	time=datetime.utcnow().timestamp()+mytime
	dd=datetime.fromtimestamp(time).day
	mm=datetime.fromtimestamp(time).month
	yyyy=datetime.fromtimestamp(time).year
	hh=datetime.fromtimestamp(time).hour
	MM=datetime.fromtimestamp(time).minute
	ss=datetime.fromtimestamp(time).second
	pos=0
	while temperzone:
		for e in pygame.event.get():
			if e.type == pygame.KEYDOWN:
				if e.key==pygame.K_ESCAPE:
					temperzone=False
				elif e.key==pygame.K_RIGHT:
					pos=(pos+1)%6
				elif e.key==pygame.K_LEFT:
					pos=(pos+5)%6
				elif e.key==pygame.K_UP:
					if pos==0:
						time+=60*60*24
					if pos==1:
						time+=60*60*24*31
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
				menu=False
		screen.fill((0,255,0))

		text=font.render('day',1,(0,0,0))
		textpos=text.get_rect(centerx=width/2-350,centery=height-220)
		screen.blit(text,textpos)
		text=font.render('month',1,(0,0,0))
		textpos=text.get_rect(centerx=width/2-250,centery=height-220)
		screen.blit(text,textpos)
		text=font.render('year',1,(0,0,0))
		textpos=text.get_rect(centerx=width/2-100,centery=height-220)
		screen.blit(text,textpos)
		text=font.render('hour',1,(0,0,0))
		textpos=text.get_rect(centerx=width/2+150,centery=height-220)
		screen.blit(text,textpos)
		text=font.render('minute',1,(0,0,0))
		textpos=text.get_rect(centerx=width/2+250,centery=height-220)
		screen.blit(text,textpos)
		text=font.render('second',1,(0,0,0))
		textpos=text.get_rect(centerx=width/2+350,centery=height-220)
		screen.blit(text,textpos)

		if pos==0:
			pygame.draw.rect(screen,(255,255,255),(width/2-400,height-200,99,99),2)
		else:
			pygame.draw.rect(screen,(255,255,255),(width/2-400,height-200,99,99))
		text=bigfont.render(str(dd),1,(0,0,0))
		textpos=text.get_rect(centerx=width/2-350,centery=height-150)
		screen.blit(text,textpos)
		if pos==1:
			pygame.draw.rect(screen,(255,255,255),(width/2-300,height-200,99,99),2)
		else:
			pygame.draw.rect(screen,(255,255,255),(width/2-300,height-200,99,99))
		text=bigfont.render(str(mm),1,(0,0,0))
		textpos=text.get_rect(centerx=width/2-250,centery=height-150)
		screen.blit(text,textpos)
		if pos==2:
			pygame.draw.rect(screen,(255,255,255),(width/2-200,height-200,199,99),2)
		else:
			pygame.draw.rect(screen,(255,255,255),(width/2-200,height-200,199,99))
		text=bigfont.render(str(yyyy),1,(0,0,0))
		textpos=text.get_rect(centerx=width/2-100,centery=height-150)
		screen.blit(text,textpos)
		if pos==3:
			pygame.draw.rect(screen,(255,255,255),(width/2+100,height-200,99,99),2)
		else:
			pygame.draw.rect(screen,(255,255,255),(width/2+100,height-200,99,99))
		text=bigfont.render(str(hh),1,(0,0,0))
		textpos=text.get_rect(centerx=width/2+150,centery=height-150)
		screen.blit(text,textpos)
		if pos==4:
			pygame.draw.rect(screen,(255,255,255),(width/2+200,height-200,99,99),2)
		else:
			pygame.draw.rect(screen,(255,255,255),(width/2+200,height-200,99,99))
		text=bigfont.render(str(MM),1,(0,0,0))
		textpos=text.get_rect(centerx=width/2+250,centery=height-150)
		screen.blit(text,textpos)
		if pos==5:
			pygame.draw.rect(screen,(255,255,255),(width/2+300,height-200,99,99),2)
		else:
			pygame.draw.rect(screen,(255,255,255),(width/2+300,height-200,99,99))
		text=bigfont.render(str(ss),1,(0,0,0))
		textpos=text.get_rect(centerx=width/2+350,centery=height-150)
		screen.blit(text,textpos)

		screen.blit(idle,(100,100,player.rect.width,player.rect.height))
		pygame.display.update()
		clock.tick(60)
def start_game():
	global running,pressed,colliding,player,flip,jumping,imgcount,showhole,hole,temperzone,holepos,mytime
	while running and not temperzone:
		for e in pygame.event.get():
			if e.type == pygame.QUIT:
				running=False
				break
			if e.type == pygame.KEYDOWN:
				if e.key == pygame.K_RIGHT:
					pressed=True
					player.vx=5
					flip=False
				elif e.key == pygame.K_LEFT:
					pressed=True
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
		cloudirect.x-=1
		screen.blit(flowerimg,(flowerimgrect.x-camera[0],flowerimgrect.y-camera[1],flowerimgrect.width,flowerimgrect.height))
		screen.blit(cloudi,(cloudirect.x-camera[0],cloudirect.y-camera[1],cloudirect.width,cloudirect.height))
		if showhole>0:
			now=datetime.utcnow().timestamp()
			if now-showhole>5:
				showhole=0
				holepos=0
			else:
				screen.blit(hole,(holerect.x-camera[0],holerect.y-camera[1],holerect.width,holerect.height))
		for block in all_blocks:
			if isinstance(block,Wall):
				block.show(brickimgs,screen,camera,earth,bricksize)
			elif isinstance(block,Other):
				block.update()
				block.show(screen,camera)
			elif isinstance(block,Player):
				block.update()
		if not colliding:
			jumping=jumping+1
			if jumping<10:
				screen.blit(face(jump[0]),playerpos())
			elif jumping<20:
				screen.blit(face(jump[1]),playerpos())
			elif jumping<30 or player.vy<0:
				screen.blit(face(jump[2]),playerpos())
			elif player.vy<1:
				screen.blit(face(jump[3]),playerpos())
			else:
				screen.blit(face(jump[5]),playerpos())
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
					mytime-=datetime.utcnow().timestamp()-temptime
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
					mytime-=datetime.utcnow().timestamp()-temptime
				else:
					screen.blit(face(idle),(holerect.x+holerect.width/2-camera[0],player.rect.y-camera[1]),(holerect.x+holerect.width/2-player.rect.x,0,player.rect.width,player.rect.height))
			elif holepos<0:
				holepos=1
			imgcount=0
		else:
			imgcount=(imgcount+1.5)%60
			if holepos==0:
				screen.blit(face(boy[int(imgcount/6)]),playerpos())
			elif player.rect.x<holerect.x+holerect.width and holepos>0:
				if player.rect.x+player.rect.width<holerect.x+holerect.width/2:
					screen.blit(face(boy[int(imgcount/6)]),playerpos())
				elif player.rect.x>holerect.x+holerect.width/2:
					player.rect.x=holerect.x
					temptime=datetime.utcnow().timestamp()
					goto_temperzone()
					mytime-=datetime.utcnow().timestamp()-temptime
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
					mytime-=datetime.utcnow().timestamp()-temptime
				else:
					screen.blit(face(boy[int(imgcount/6)]),(holerect.x+holerect.width/2-camera[0],player.rect.y-camera[1]),(holerect.x+holerect.width/2-player.rect.x,0,player.rect.width,player.rect.height))
			elif holepos<0:
				holepos=1
		text=font.render('Date and Time : '+datetime.fromtimestamp(datetime.utcnow().timestamp()+mytime).strftime("%d/%m/%Y %H:%M:%S"),1,(0,0,0))
		textpos=text.get_rect(centerx=screen.get_width()/2)
		screen.blit(text,textpos)
		pygame.display.update()
		clock.tick(60)
	save_game()
def save_game():
	global player,all_blocks
	open('player.data','w').write(str(player.rect.x)+','+str(player.rect.y)+'\n'+str(round(mytime)))
	othr=[]
	for o in all_blocks:
		if isinstance(o,Other):
			d={'n':o.name,'x':o.rect.x,'y':o.rect.y,'v':o.visible}
			othr.append(d)
	data={'cloud':[cloudirect.x,cloudirect.y],"other":othr}
	open('other.data','w').write(json.dumps(data))
open_menu()
pygame.quit()
quit()