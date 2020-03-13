import pygame,os

coinsize=30
bricksize=60
width=1200
height=300

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
for i in range(49):
	im=pygame.image.load('diamonds'+os.path.sep+str(i+1)+'.png')
	im=pygame.transform.scale(im,(coinsize*2,coinsize*2))
	assets["diamonds"].append(im)

flowerimg=pygame.image.load('flower.png')
flowerimg=pygame.transform.scale(flowerimg,(30,30))
flowerimgrect=flowerimg.get_rect()

seed=pygame.image.load('seed.png')
seed=pygame.transform.scale(seed,(height//5,height//5))
seedrect=seed.get_rect(centerx=width*3//14,centery=height*3//5)

showhole=0
holepos=0
hole=pygame.image.load('hole.png')
hole=pygame.transform.scale(hole,(45,150))
holerect=hole.get_rect()

energy=pygame.image.load('energy.jpg')
energy=pygame.transform.scale(energy,(200,30))
energyrect=energy.get_rect()

brickimgs=[]
for i in range(16):
	brickimg=pygame.image.load('bricks/brick'+str(i)+'.png')
	brickimg=pygame.transform.scale(brickimg,(bricksize,bricksize))
	brickimgs.append(brickimg)

cloudi=pygame.image.load('cloud.png')
cloudi=pygame.transform.scale(cloudi,(360,120))
cloudirect=cloudi.get_rect()

mainboard=pygame.image.load('menu/menuboard.png')
mainboard=pygame.transform.scale(mainboard,(300,400))
mainboardrect=mainboard.get_rect()
