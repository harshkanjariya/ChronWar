import pygame
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
		self.blood=1000
		self.time=0
		self.coins=0
		self.seed=0
		self.time_energy=0
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
		self.starttime=0
		self.endtime=0
		self.imgs=imgs
	def update(self):
		if "diamond" in self.name:
			self.count=(self.count+1)%120
		else:
			self.count=(self.count+2)%60
	def show(self,screen,camera,now):
		if self.starttime<now and self.endtime>now:
			if "diamond" in self.name:
				screen.blit(self.imgs[int(self.count*len(self.imgs)/120)],(self.rect.x-camera[0],self.rect.y-camera[1],50,50))
			else:
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
	def show(self,brickimgs,screen,camera,earth,bricksize):
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
