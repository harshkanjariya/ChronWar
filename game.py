from datetime import datetime
import os
import pytz
import pygame
import json
pygame.mixer.pre_init(44100, 16, 2, 4096)
pygame.init()
screen=pygame.display.set_mode([1200,600])
width,height=screen.get_size()
running=False
jumping=0
pressed=False
flip=False
colliding=False
coinsize=30
bricksize=60
clock=pygame.time.Clock()
font=pygame.font.Font(None,30)
pygame.mixer.init()
coingain=pygame.mixer.Sound("coin.wav")
all_blocks=pygame.sprite.Group()
camera=[width/2,height/2]

class Player(pygame.sprite.Sprite):
	def __init__(self,name,color,width,height):
		super().__init__()
		self.image=pygame.Surface([width,height])
		self.image.fill(color)
		self.image.set_colorkey(color)
		self.color=color
		self.name=name
		self.rect=self.image.get_rect()
		self.vx=0
		self.vy=0
	def show(self):
		global screen,camera
		pygame.draw.rect(screen,self.color,(self.rect.x-camera[0],self.rect.y-camera[1],self.rect.width,self.rect.height))
	def update(self):
		self.rect.x+=self.vx
		self.rect.y+=self.vy
class Other(pygame.sprite.Sprite):
	def __init__(self,name,color,x,y,coinsize,imgs):
		super().__init__()
		self.image=pygame.Surface([coinsize,coinsize])
		self.image.fill(color)
		self.image.set_colorkey(color)
		self.color=color
		self.rect=self.image.get_rect()
		self.rect.x=x
		self.rect.y=y
		self.count=0
		self.name=name
		self.visible=True
		self.imgs=imgs
	def update(self):
		self.count=(self.count+2)%60
	def show(self):
		if self.visible:
			global screen,camera
			screen.blit(self.imgs[int(self.count*len(self.imgs)/60)],(self.rect.x-camera[0],self.rect.y-camera[1],50,50))
class Wall(pygame.sprite.Sprite):
	def __init__(self,color,blocks,bricksize):
		super().__init__()
		self.image=pygame.Surface([bricksize*blocks[2],bricksize*blocks[3]])
		self.image.fill(color)
		self.image.set_colorkey(color)
		self.color=color
		self.rect=self.image.get_rect()
		self.rect.x=blocks[0]*bricksize
		self.rect.y=blocks[1]*bricksize
		self.blocks=blocks
	def show(self):
		global screen,camera,bricksize,brickimgs
		if self.blocks[3]==1:
			if self.blocks[2]==1:
				screen.blit(brickimgs[14],(self.rect.x-camera[0],self.rect.y-camera[1],bricksize,bricksize))
			else:
				for i in range(self.blocks[2]):
					if i==0:
						img=brickimgs[13]
						for b in earth:
							if self.blocks[0]==b[0]+b[2]:
								img=brickimgs[14]
					elif i==self.blocks[2]-1:
						img=brickimgs[15]
						for b in earth:
							if self.blocks[0]+self.blocks[2]==b[0]:
								img=brickimgs[14]
					else:
						img=brickimgs[14]
					screen.blit(img,(self.rect.x+i*bricksize-camera[0],self.rect.y-camera[1],bricksize,bricksize))
		else:
			for i in range(self.blocks[3]):
				for j in range(self.blocks[2]):
					img=brickimgs[4]
					if i==0:
						img=brickimgs[1]
						if j==0:
							img=brickimgs[0]
							for b in earth:
								if self.blocks[0]==b[0]+b[2]:
									if self.blocks[1]==b[1]:
										img=brickimgs[1]
									elif self.blocks[1]<b[1]:
										img=brickimgs[0]
									elif self.blocks[1]>b[1] and self.blocks[1]<b[1]+b[3]:
										img=brickimgs[12]
									break
						elif j==self.blocks[2]-1:
							img=brickimgs[2]
							for b in earth:
								if self.blocks[0]+self.blocks[2]==b[0]:
									if self.blocks[1]==b[1]:
										img=brickimgs[1]
									elif self.blocks[1]<b[1]:
										img=brickimgs[2]
									else:
										img=brickimgs[9]
									break
					elif i==self.blocks[3]-1:
						if j==0:
							img=brickimgs[6]
							for b in earth:
								if self.blocks[0]==b[0]+b[2]:
									if self.blocks[1]+self.blocks[3]==b[1]+b[3]:
										img=brickimgs[7]
									elif self.blocks[1]+self.blocks[3]>b[1]+b[3]:
										img=brickimgs[6]
									elif self.blocks[1]+self.blocks[3]<b[1]+b[3] and self.blocks[1]+self.blocks[3]>b[1]:
										img=brickimgs[7]
						elif j==self.blocks[2]-1:
							img=brickimgs[8]
							for b in earth:
								if self.blocks[0]+self.blocks[2]==b[0]:
									if self.blocks[1]+self.blocks[3]==b[1]+b[3]:
										img=brickimgs[7]
									elif self.blocks[1]+self.blocks[3]>b[1]+b[3]:
										img=brickimgs[8]
									elif self.blocks[1]+self.blocks[3]<b[1]+b[3] and self.blocks[1]+self.blocks[3]>b[1]:
										img=brickimgs[7]
						else:
							img=brickimgs[7]
					else:
						if j==0:
							img=brickimgs[3]
							for b in earth:
								if self.blocks[0]==b[0]+b[2]:
									if self.blocks[1]+i==b[1]:
										img=brickimgs[10]
										break
									elif self.blocks[1]+i>b[1] and self.blocks[1]+i<b[1]+b[3]:
										img=brickimgs[4]
										break
						elif j==self.blocks[2]-1:
							img=brickimgs[5]
							for b in earth:
								if self.blocks[0]+self.blocks[2]==b[0]:
									if self.blocks[1]+i==b[1]:
										img=brickimgs[11]
										break
									elif self.blocks[1]+i>b[1] and self.blocks[1]+i<b[1]+b[3]:
										img=brickimgs[4]
										break
					screen.blit(img,(self.rect.x+j*bricksize-camera[0],self.rect.y+i*bricksize-camera[1],bricksize,bricksize))
		# pygame.draw.rect(screen,self.color,[self.rect.x-camera[0],self.rect.y-camera[1],self.rect.width,self.rect.height])

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

# bushes=[]
# im=pygame.image.load('grass0.png')
# im=pygame.transform.scale(im,(coinsize*3,coinsize*2))
# bushes.append(im)
# grass=Other("grass",(0,0,0),990,370,coinsize*3,bushes)
# all_blocks.add(grass)

coins=[]
for i in range(5):
	im=pygame.image.load('coins'+os.path.sep+str(i)+'.png')
	im=pygame.transform.scale(im,(coinsize,coinsize))
	coins.append(im)

diamonds=[]
for i in range(5):
	im=pygame.image.load('diamonds'+os.path.sep+str(i)+'.png')
	im=pygame.transform.scale(im,(coinsize*2,coinsize*2))
	diamonds.append(im)

def resume_old():
	otherdata=json.load(open('other.data','r'))
	for o in otherdata['other']:
		obj=None
		if o['v']:
			if o['n']=="coin":
				obj=Other("coin",(0,0,0),o['x'],o['y'],coinsize,coins)
			else:
				obj=Other("diamond",(0,0,0),o['x'],o['y'],coinsize,diamonds)
			all_blocks.add(obj)
	playerdata=open('player.data','r').read()
	playerdata=playerdata.split()
	playerdata[0]=list(map(int,playerdata[0].split(',')))
	player.rect.x=playerdata[0][0]
	player.rect.y=playerdata[0][1]

def newgame_load():
	coin=Other("coin",(0,0,0),1035,400,coinsize,coins)
	all_blocks.add(coin)
	for i in range(5):
		coin=Other("coin",(0,0,0),3015+bricksize*i,950,coinsize,coins)
		all_blocks.add(coin)
	diamond=Other("diamond",(0,0,0),1030,300,coinsize,diamonds)
	all_blocks.add(diamond)
	player.rect.x=10
	player.rect.y=500

flowerimg=pygame.image.load('flower.png')
flowerimg=pygame.transform.scale(flowerimg,(30,30))
flowerimgrect=flowerimg.get_rect()
flowerimgrect.x=1050
flowerimgrect.y=570

brickimgs=[]
for i in range(16):
	brickimg=pygame.image.load('bricks/brick'+str(i)+'.png')
	brickimg=pygame.transform.scale(brickimg,(bricksize,bricksize))
	brickimgs.append(brickimg)

earth=open("earth.data").read()
earth=[list(map(int,x.split(','))) for x in earth.split()]
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
			if b.name=="coin" or b.name=="diamond":
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
def start_game():
	global running,pressed,colliding,player,flip,jumping,imgcount
	while running:
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
		player.update()
		for block in all_blocks:
			if isinstance(block,Wall):
				block.show()
			elif isinstance(block,Other):
				block.update()
				block.show()
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
			screen.blit(face(idle),playerpos())
			imgcount=0
		else:
			imgcount=(imgcount+1.5)%60
			screen.blit(face(boy[int(imgcount/6)]),playerpos())
		text=font.render('Date and Time : '+datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"),1,(0,0,0))
		textpos=text.get_rect(centerx=screen.get_width()/2)
		screen.blit(text,textpos)
		pygame.display.update()
		clock.tick(60)
	save_game()
def save_game():
	global player,all_blocks
	open('player.data','w').write(str(player.rect.x)+','+str(player.rect.y))
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