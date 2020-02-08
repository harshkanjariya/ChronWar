from pygame import *
init()
screen=display.set_mode([1200,600])
width,height=screen.get_size()
running=True
pressed=False
flip=False
colliding=False
clock=time.Clock()
all_blocks=sprite.Group()
camera=[width/2,height/2]

class Player(sprite.Sprite):
	def __init__(self,color,width,height):
		super().__init__()
		self.image=Surface([width,height])
		self.image.fill(color)
		self.image.set_colorkey(color)
		self.color=color
		self.rect=self.image.get_rect()
		self.vx=0
		self.vy=0
	def update(self):
		self.rect.x+=self.vx
		self.rect.y+=self.vy

class Wall(sprite.Sprite):
	def __init__(self,color,width,height):
		super().__init__()
		self.image=Surface([width,height])
		self.image.fill(color)
		self.image.set_colorkey(color)
		self.color=color
		self.rect=self.image.get_rect()
	def show(self):
		global screen,camera
		draw.rect(screen,self.color,[self.rect.x-camera[0],self.rect.y-camera[1],self.rect.width,self.rect.height])

player=Player((0,0,0),70,100)
player.rect.x=20
player.rect.y=20
all_blocks.add(player)
idle=image.load('sprite0.png')
idle=transform.scale(idle,(player.rect.width,player.rect.height))
boy=[]
imgcount=0
for i in range(10):
	im=image.load('sprite'+str(i+1)+'.png')
	im=transform.scale(im,(player.rect.width,player.rect.height))
	boy.append(im)
jump=[]
for i in range(7):
	im=image.load('jump'+str(i+1)+'.png')
	im=transform.scale(im,(player.rect.width,player.rect.height))
	jump.append(im)

block=Wall((0,255,0),500,50)
block.rect.x=20
block.rect.y=500
all_blocks.add(block)
block=Wall((0,255,0),500,50)
block.rect.x=600
block.rect.y=400
all_blocks.add(block)

a=0.1
friction=0.6
def face(im):
	if flip:
		return transform.flip(im,True,False)
	else:
		return im
def playerpos():
	return (player.rect.x-camera[0],player.rect.y-camera[1],player.rect.width,player.rect.height)
def collisions():
	collide_list=sprite.spritecollide(player,all_blocks,False)
	global colliding
	colliding=False
	for b in collide_list:
		if not b==player:
			colliding=True
			if player.rect.x+player.rect.width-5>b.rect.x and player.rect.x+5<b.rect.x+b.rect.width:
				if player.rect.y+player.rect.height/2<b.rect.y+b.rect.height/2 and player.vy>0:
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
				if player.rect.x<b.rect.x:
					player.vx=-1
					player.rect.x=b.rect.x-player.rect.width
				elif player.rect.x>b.rect.x:
					player.vx=1
					player.rect.x=b.rect.x+b.rect.width
while running:
	for e in event.get():
		if e.type == QUIT:
			running=False
		if e.type == KEYDOWN:
			if e.key == K_RIGHT:
				pressed=True
				player.vx=5
				flip=False
			elif e.key == K_LEFT:
				pressed=True
				flip=True
				player.vx=-5
			elif e.key == K_UP:
				player.vy=-5
		elif e.type == KEYUP:
			if e.key == K_RIGHT:
				pressed=False
			elif e.key == K_LEFT:
				pressed=False
	screen.fill((255,255,255))
	player.vy+=a
	if player.rect.x-camera[0]<width/4:
		camera[0]=player.rect.x-width/4
	elif player.rect.x-camera[0]>width/2:
		camera[0]=player.rect.x-width/2
	if player.rect.y+player.rect.height-camera[1]>height*3/4:
		camera[1]=player.rect.y+player.rect.height-height*3/4
	elif player.rect.y-camera[1]<height/4:
		camera[1]=player.rect.y-height/4
	collisions()
	player.update()
	for block in all_blocks:
		if not block==player:
			block.show()
	if not colliding:
		if player.vy<-0.5:
			screen.blit(face(jump[1]),playerpos())
		elif player.vy<0.5:
			screen.blit(face(jump[3]),playerpos())
		else:
			screen.blit(face(jump[3]),playerpos())
	elif colliding and player.vx==0:
		screen.blit(face(idle),playerpos())
		imgcount=0
	else:
		imgcount=(imgcount+1.5)%60
		screen.blit(face(boy[int(imgcount/6)]),playerpos())
	display.update()
	clock.tick(60)
quit()