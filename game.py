from pygame import *
class Block:
	def __init__(self,a,b,c,d):
		self.x=a
		self.y=b
		self.w=c
		self.h=d
init()
screen=display.set_mode([1200,600])
running=True
clock=time.Clock()
x=100
vx=5
y=400
vy=0
a=0.1
r=30
friction=0.8
blocks=[]
blocks.append(Block(50,500,500,50))
blocks.append(Block(500,450,500,50))
blocks.append(Block(20,200,50,300))
while running:
	for e in event.get():
		if e.type == QUIT:
			running=False
		if e.type == KEYDOWN:
			if e.key == K_RIGHT:
				vx=5
			elif e.key == K_LEFT:
				vx=-5
			elif e.key == K_UP:
				vy=-5
	screen.fill((255,255,255))
	x=x+vx
	y=y+vy
	vy=vy+a
	for b in blocks:
		draw.rect(screen,(0,255,0),(b.x,b.y,b.w,b.h))
		if x>b.x and x<b.x+b.w:
			if y<b.y+b.h/2:
				if y+r>=b.y:
					y=b.y-r
					vy=-abs(vy*friction)
					if abs(vy)<0.8:
						vy=0
					vx=vx*friction
			elif y>b.y+b.h/2:
				if y-r<=b.y:
					y=b.y-r
					vy=abs(vy*friction)
					if abs(vy)<0.8:
						vy=0
					vx=vx*friction
		elif y>b.y and y<b.y+b.h:
			if x<b.x+b.w/2:
				if x+r>=b.x:
					vx=-abs(vx*friction)
			elif x>b.x+b.w/2:
				if x-r<=b.x+b.w:
					vx=abs(vx*friction)
	draw.circle(screen,(255,0,0),(int(x),int(y)),r)
	display.update()
	clock.tick(60)
quit()