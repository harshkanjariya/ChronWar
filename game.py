from datetime import datetime
import os
import pytz
import pygame
pygame.mixer.pre_init(44100, 16, 2, 4096)
pygame.init()
screen=pygame.display.set_mode([1200,600])
width,height=screen.get_size()
running=True
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
			screen.blit(self.imgs[int(self.count/12)],(self.rect.x-camera[0],self.rect.y-camera[1],50,50))
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
		for i in range(self.blocks[2]):
			for j in range(self.blocks[3]):
				# found=False
				# for b in earth:
				# 	if self.blocks[0]-1>b[0] and self.blocks[0]+self.blocks
				screen.blit(brickimgs[1],(self.rect.x+i*bricksize-camera[0],self.rect.y+j*bricksize-5-camera[1],bricksize,bricksize+5))
		# pygame.draw.rect(screen,self.color,[self.rect.x-camera[0],self.rect.y-camera[1],self.rect.width,self.rect.height])

player=Player("main",(255,0,0),60,100)
player.rect.x=20
player.rect.y=20
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

coins=[]
for i in range(5):
	im=pygame.image.load('coins'+os.path.sep+str(i)+'.png')
	im=pygame.transform.scale(im,(coinsize,coinsize))
	coins.append(im)
coin=Other("coin 1",(0,0,0),1035,350,coinsize,coins)
all_blocks.add(coin)
for i in range(5):
	coin=Other("coin "+str(i+3),(0,0,0),3015+bricksize*i,950,coinsize,coins)
	all_blocks.add(coin)

diamonds=[]
for i in range(5):
	im=pygame.image.load('diamonds'+os.path.sep+str(i)+'.png')
	im=pygame.transform.scale(im,(coinsize*2,coinsize*2))
	diamonds.append(im)
diamond=Other("diamond 0",(0,0,0),725,30,coinsize,diamonds)
all_blocks.add(diamond)

flowerimg=pygame.image.load('flower.png')
flowerimg=pygame.transform.scale(flowerimg,(30,30))
flowerimgrect=flowerimg.get_rect()
flowerimgrect.x=740
flowerimgrect.y=85

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

a=0.1
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
					player.rect.x=b.rect.x-player.rect.width
				elif player.rect.x>b.rect.x and player.vx<0:
					player.vx=0
					player.rect.x=b.rect.x+b.rect.width
		elif isinstance(b,Other):
			b.visible=False
			all_blocks.remove(b)
			del b
			coingain.play()
while running:
	for e in pygame.event.get():
		if e.type == pygame.QUIT:
			running=False
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
					player.vy=-5
			elif e.key == pygame.K_SPACE:
				if colliding:
					jumping=0
					player.vy=-6
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
	if player.rect.x-camera[0]<width/4:
		camera[0]=player.rect.x-width/4
	elif player.rect.x-camera[0]>width/2:
		camera[0]=player.rect.x-width/2
	if player.rect.y+player.rect.height-camera[1]>height*3/4:
		camera[1]=player.rect.y+player.rect.height-height*3/4
	elif player.rect.y-camera[1]<height/4:
		camera[1]=player.rect.y-height/4
	collisions()
	screen.blit(flowerimg,(flowerimgrect.x-camera[0],flowerimgrect.y-camera[1],flowerimgrect.width,flowerimgrect.height))
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
quit()
