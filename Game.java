import java.util.*;
import java.text.*;
import javax.swing.*;
import javax.imageio.*;
import javax.sound.sampled.*;
import java.awt.*;
import java.io.*;
import java.awt.event.*;
import java.awt.image.*;
class Game extends JFrame{
	public Game(){
		setSize(1200,700);
		setVisible(true);
		setDefaultCloseOperation(EXIT_ON_CLOSE);
		GamePanel panel=new GamePanel();
		add(panel);
		addKeyListener(panel);
	}
	public static void main(String []args){
	    System.setProperty("sun.java2d.opengl", "true");
	    SwingUtilities.invokeLater(new Runnable(){
	    	public void run(){
				new Game();
	    	}
	    });
	}
}
class GamePanel extends JPanel implements Runnable,KeyListener{
	Player player;
	private Point camera;
	int coinsize,bricksize,jumping,width,height,holepos;
	int tzpos;
	long inittime,temptime,showhole;
	float friction,gravity;
	ArrayList<Wall>walls;
	ArrayList<Other>assets=new ArrayList<>();
	ArrayList<Rectangle>earth=new ArrayList<>();
	BufferedImage []bricks=new BufferedImage[16];
	BufferedImage []coins=new BufferedImage[5];
	BufferedImage []diamonds=new BufferedImage[5];
	BufferedImage hole,energyimg;
	private boolean pressed,colliding,flip,running,temperzone,menu;
	Rectangle holerect,energyrect;
	Font font=new Font("Arial",Font.BOLD,25);
	Font bigfont=new Font("Arial",Font.BOLD,60);
	SimpleDateFormat dateFormat=new SimpleDateFormat("dd/MM/yyyy HH:mm:ss",Locale.US);
	public GamePanel(){
		coinsize=30;
		bricksize=60;
		jumping=0;
		colliding=false;
		pressed=false;
		flip=false;
		showhole=0;
		jumping=-1;
		width=1200;
		height=700;
		friction=0.6f;
		gravity=0.2f;
		menu=false;
		running=true;
		temperzone=false;
		tzpos=0;
		camera=new Point(getWidth()/2,getHeight()/2);
		holerect=new Rectangle(0,0,45,150);
		energyrect=new Rectangle(width-350,30,200,30);
		player=new Player("main",60,100);
		walls=new ArrayList<>();
		String line;
		try{
			hole=ImageIO.read(new File("hole.png"));
			energyimg=ImageIO.read(new File("energy.jpg"));
			for (int i=0;i<16;i++){
					bricks[i]=ImageIO.read(new File("bricks/brick"+i+".png"));
			}
			for (int i=0;i<5;i++){
					coins[i]=ImageIO.read(new File("coins/"+i+".png"));
			}
			for (int i=0;i<5;i++){
					diamonds[i]=ImageIO.read(new File("diamonds/"+i+".png"));
			}
			BufferedReader reader=new BufferedReader(new InputStreamReader(new FileInputStream("earth.data")));
			while((line=reader.readLine())!=null){
				int[]ar=Arrays.asList(line.split(",")).stream().mapToInt(Integer::parseInt).toArray();
				earth.add(new Rectangle(ar[0],ar[1],ar[2],ar[3]));
			}
			reader.close();
			reader=new BufferedReader(new InputStreamReader(new FileInputStream("level1.data")));
			String objtype="";
			int indx=0;
			while((line=reader.readLine())!=null){
				if(line.indexOf(",")<0){
					objtype=line;
					indx=0;
				}else{
					long[]ar=Arrays.asList(line.split(",")).stream().mapToLong(Long::parseLong).toArray();
					if(objtype.equals("coins") || objtype.equals("diamonds")){
						indx++;
						Other obj=new Other(objtype+":"+indx,(int)ar[1],(int)ar[2]);
						obj.starttime=ar[0];
						if(ar.length>3){
							obj.endtime=ar[3];
						}else{
							obj.endtime=Long.MAX_VALUE;
						}
						assets.add(obj);
					}
				}
			}
		}catch(Exception exc){exc.printStackTrace();}
		for(var l:earth)
			walls.add(new Wall(l.x,l.y,l.width,l.height));
		Thread t=new Thread(this);
		t.start();
	}
	public void paint(Graphics g){
		Graphics2D g2d=(Graphics2D)g;
		if (running) {
			g2d.setColor(new Color(100,255,255));
			g2d.fillRect(0,0,getWidth(),getHeight());
			g2d.translate(100-camera.x,-camera.y);
			g2d.setColor(Color.red);
			long now=new Date().getTime();
			if (showhole>0)
			if(now-showhole>5000){
				showhole=0;
				holepos=0;
			}else{
				g2d.drawImage(hole,holerect.x,holerect.y,holerect.width,holerect.height,null);
			}
			for(var w:walls)
				w.show(g2d);
			for(var a:assets)
				a.show(g2d,now);
			player.show(g2d);
			g2d.setFont(font);
			g2d.setColor(Color.BLACK);
			g2d.drawString("Date and Time : "+dateFormat.format(new Date(now+player.time)),width/4+camera.x,20+camera.y);
			g2d.drawString("x "+player.coins,camera.x,45+camera.y);
			g2d.drawImage(coins[0],camera.x-50,20+camera.y,30,30,null);
			if(player.time_energy>0){
				long day=100*3600*24;
				int wid=(int)(player.time_energy/(day*365));
				g2d.drawImage(energyimg.getSubimage(0,0,energyimg.getWidth()*wid/100,energyimg.getHeight()),energyrect.x+camera.x,energyrect.y+camera.y,wid,energyrect.height,null);
			}
			g2d.drawRect(camera.x+energyrect.x,camera.y+energyrect.y,energyrect.width,energyrect.height);
			g2d.setColor(Color.RED);
			g2d.fillRect(camera.x+energyrect.x,50+camera.y+energyrect.y,energyrect.width*player.blood/1000,energyrect.height);
			g2d.setColor(Color.BLACK);
			g2d.drawRect(camera.x+energyrect.x,50+camera.y+energyrect.y,energyrect.width,energyrect.height);
		}else if(temperzone){
			g2d.translate(0,0);
			g2d.setColor(new Color(0,255,0));
			g2d.fillRect(0,0,width,height);
			long now=new Date().getTime();
			g2d.setFont(font);
			g2d.setColor(Color.BLACK);
			g2d.drawString(player.name,50,20);
			long diff = player.time_energy;
			long diffSeconds = diff / 1000 % 60;
			long diffMinutes = diff / (60 * 1000) % 60;
			long diffHours = diff / (60 * 60 * 1000) % 24;
			long diffDays = diff / (24 * 60 * 60 * 1000);

			g2d.drawString(diffDays+" days,",width-260,90);
			g2d.drawString(diffHours+":"+diffMinutes+":"+diffSeconds,width-130,90);
			g2d.drawString("Temper Zone",width/2-50,20);
			g2d.drawImage(player.idle,100,100,player.idle.getWidth(),player.idle.getHeight(),null);
			if(player.time_energy>0){
				long day=100*3600*24;
				int wid=(int)(player.time_energy/(day*365));
				g2d.drawImage(energyimg.getSubimage(0,0,energyimg.getWidth()*wid/100,energyimg.getHeight()),energyrect.x+100,energyrect.y,wid,energyrect.height,null);
			}
			g2d.drawRect(energyrect.x+100,energyrect.y,energyrect.width,energyrect.height);

			g2d.drawString("Day",width/2-370,height-320);
			g2d.drawString("Month",width/2-285,height-320);
			g2d.drawString("Year",width/2-130,height-320);
			g2d.drawString("Hour",width/2+120,height-320);
			g2d.drawString("Minute",width/2+210,height-320);
			g2d.drawString("Second",width/2+300,height-320);

			g2d.setColor(Color.WHITE);
			g2d.setStroke(new BasicStroke(2));
			Calendar cal=Calendar.getInstance();
			cal.setTimeInMillis(temptime);
			g2d.setFont(bigfont);
			if(tzpos==0){
				g2d.drawRect(width/2-400,height-299,97,97);
			}else{
				g2d.fillRect(width/2-400,height-300,98,98);
			}
			if(tzpos==1){
				g2d.drawRect(width/2-300,height-299,97,97);
			}else{
				g2d.fillRect(width/2-300,height-300,98,98);
			}
			if(tzpos==2){
				g2d.drawRect(width/2-200,height-299,197,97);
			}else{
				g2d.fillRect(width/2-200,height-300,198,98);
			}
			if(tzpos==3){
				g2d.drawRect(width/2+100,height-299,97,97);
			}else{
				g2d.fillRect(width/2+100,height-300,98,98);
			}
			if(tzpos==4){
				g2d.drawRect(width/2+200,height-299,97,97);
			}else{
				g2d.fillRect(width/2+200,height-300,98,98);
			}
			if(tzpos==5){
				g2d.drawRect(width/2+300,height-299,97,97);
			}else{
				g2d.fillRect(width/2+300,height-300,98,98);
			}
			if(tzpos==6){
				g2d.drawRect(width/2-50,height-199,197,97);
			}else{
				g2d.fillRect(width/2-50,height-200,198,98);
			}
			g2d.setColor(Color.BLACK);
			g2d.drawString(""+cal.get(Calendar.DAY_OF_MONTH),width/2-375,height-230);
			g2d.drawString(""+(cal.get(Calendar.MONTH)+1),width/2-275,height-230);
			g2d.drawString(""+cal.get(Calendar.YEAR),width/2-165,height-230);
			g2d.drawString(""+cal.get(Calendar.HOUR_OF_DAY),width/2+125,height-230);
			g2d.drawString(""+cal.get(Calendar.MINUTE),width/2+220,height-230);
			g2d.drawString(""+cal.get(Calendar.SECOND),width/2+320,height-230);
			g2d.drawString("Jump",width/2-30,height-135);
		}
	}
	public void run(){
		long now;
		while(true){
			if(running){
				if(player.vy<0)
					player.vy+=gravity;
				else
					player.vy+=2*gravity;
				if(pressed){
					if (flip) {
						player.vx=-5;
					}else{
						player.vx=5;
					}
				}
				collide();
				player.update();
				if(player.x-camera.x<width/4)
					camera.x=player.x-width/4;
				else if(player.x-camera.x>width/2)
					camera.x=player.x-width/2;
				if(player.y+player.height-camera.y>height*3/4)
					camera.y=player.y+player.height-height*3/4;
				else if(player.y-camera.y<height/4)
					camera.y=player.y-height/4;
				gain();
				for(var a:assets)
					a.update();
			}else if(temperzone){

			}
			repaint();
			try{Thread.sleep(10);}catch(Exception e){e.printStackTrace();}
		}
	}
	public void gain(){
		long dt=new Date().getTime()+player.time;
		for(var a:assets){
			if(player.x+player.width>a.x && player.x<a.x+coinsize &&
				player.y+player.height>a.y && player.y<a.y+coinsize &&
				dt>a.starttime && dt<a.endtime){
				a.endtime=dt;
				playSound();
				if(a.name.startsWith("coins:"))
					player.coins+=1;
				else if(a.name.startsWith("diamonds:")){
					long temp=1000*3600*24;
					player.time_energy+=temp*365;
				}
			}
		}
	}
	public void collide(){
		colliding=false;
		for(var r:earth){
			Rectangle b=(Rectangle)r.clone();
			b.x*=bricksize;
			b.y*=bricksize;
			b.width*=bricksize;
			b.height*=bricksize;
			if(player.x+player.width-5>b.x && player.x+5<b.x+b.width){
				if(player.y+player.height/2<b.y+b.height/2 && player.vy>0){
					if(player.y+player.height>=b.y){
						colliding=true;
						player.vy=0;
						player.y=b.y-player.height;
						if(!pressed){
							player.vx=player.vx*friction;
							if(Math.abs(player.vx)<0.6)
								player.vx=0;
						}
					}
				}else if(player.y+player.height/2>b.y+b.height/2){
					if (player.y<=b.y+b.height) {
						player.vy=Math.abs(player.vy);
						player.y=b.y+b.height;
						if(!pressed){
							player.vx=player.vx*friction;
							if(Math.abs(player.vx)<0.6)
								player.vx=0;
						}
					}
				}
			}else if(player.y+player.height>b.y && player.y<b.y+b.height)
				if(player.x+player.width/2<b.x+b.width/2 && player.vx>0){
					if (player.x+player.width>=b.x) {
						player.vx=0;
						// player.rect.x=b.rect.x-player.rect.width
					}
				}else if(player.x+player.width/2>b.x+b.width/2 && player.vx<0){
					if (player.x<=b.x+b.width){
						player.vx=0;
						// player.rect.x=b.rect.x+b.rect.width
					}
				}
		}
	}
	public void keyPressed(KeyEvent e){
		int c=e.getKeyCode();
		if (running){
			if(c==KeyEvent.VK_UP){
				if(colliding){
					jumping=0;
					player.vy=-7;
				}
			}else if(c==KeyEvent.VK_DOWN){
				if(colliding){
					jumping=0;
					player.vy=7;
				}
			}else if(c==KeyEvent.VK_LEFT){
				pressed=true;
				flip=true;
				player.vx=-5;
			}else if(c==KeyEvent.VK_RIGHT){
				pressed=true;
				flip=false;
				player.vx=5;
			}else if(c==KeyEvent.VK_SPACE){
				if(colliding){
					jumping=0;
					player.vy=-9;
				}
			}else if(c==KeyEvent.VK_P){
				if(showhole==0){
					if (colliding){
						if(flip){
							holepos=-1;
							holerect.x=player.x-100;
						}else{
							holepos=1;
							holerect.x=player.x+100;
						}
						holerect.y=player.y-30;
						showhole=new Date().getTime();
						// socks[0].send(bytes('<hole_'+str(holerect.x)+'_'+str(holerect.y)+'>','utf-8'))
					}
				}else{
					showhole=0;
					holepos=0;
				}
			}
		}else if(temperzone){
			long day=1000*60*60*24;
			if(c==27){
				temperzone=false;
				running=true;
				player.time-=new Date().getTime()-inittime;
			}else if(c==KeyEvent.VK_ENTER){
				if(tzpos==6){
					player.time_energy-=Math.abs(temptime-inittime-player.time);
					temperzone=false;
					running=true;
					player.time=temptime-inittime;
				}
			}else if(c==KeyEvent.VK_UP){
				switch(tzpos){
					case 0:
						System.out.println(dateFormat.format(new Date(temptime)));
						temptime+=day;
						break;
					case 1:
						temptime+=day*30;
						break;
					case 2:
						temptime+=day*365;
						break;
					case 3:
						temptime+=1000*60*60;
						break;
					case 4:
						temptime+=1000*60;
						break;
					case 5:
						temptime+=1000;
						break;
				}
			}else if(c==KeyEvent.VK_DOWN){
				switch(tzpos){
					case 0:
						temptime-=day;
						break;
					case 1:
						temptime-=day*30;
						break;
					case 2:
						temptime-=day*365;
						break;
					case 3:
						temptime-=1000*60*60;
						break;
					case 4:
						temptime-=1000*60;
						break;
					case 5:
						temptime-=1000;
						break;
				}
			}else if(c==KeyEvent.VK_LEFT){
				tzpos=(tzpos+6)%7;
			}else if(c==KeyEvent.VK_RIGHT){
				tzpos=(tzpos+1)%7;
			}
		}
	}
	public void keyReleased(KeyEvent e){
		int c=e.getKeyCode();
		if (running) {
			if(c==KeyEvent.VK_LEFT){
				pressed=false;
				player.vx=0;
			}else if(c==KeyEvent.VK_RIGHT){
				pressed=false;
				player.vx=0;
			}
		}
	}
	public void keyTyped(KeyEvent e){}
	class Wall{
		int x,y,col,row,size;
		public Wall(int x,int y,int col,int row){
			this.x=x;
			this.y=y;
			this.row=row;
			this.col=col;
			size=bricksize;
		}
		public void show(Graphics2D g){
			BufferedImage img=null;
			if(row==1){
				if(col==1){
					g.drawImage(bricks[0],x*size,y*size,size,size,null);
				}else{
					for(int i=0;i<col;i++){
						if(i==0){
							img=bricks[13];
							for(var b:earth)
								if(x==b.x+b.width)
									img=bricks[14];
						}else if(i==col-1){
							img=bricks[15];
							for(var b:earth)
								if(x+col==b.x)
									img=bricks[14];
						}else
							img=bricks[14];
						g.drawImage(img,x*size+i*size,y*size,size,size,null);
					}	// screen.blit(img,(self.rect.x+i*bricksize-camera[0],self.rect.y-camera[1],bricksize,bricksize))
				}
			}else{
				for(int i=0;i<row;i++){
					for(int j=0;j<col;j++){
						img=bricks[4];
						if(i==0){
							img=bricks[1];
							if(j==0){
								img=bricks[0];
								for(var b:earth)
									if(x==b.x+b.width){
										if(y==b.y)
											img=bricks[1];
										else if(y<b.y)
											img=bricks[0];
										else if(y>b.y && y<b.y+b.height)
											img=bricks[12];
										break;
									}
							}else if(j==col-1){
								img=bricks[2];
								for(var b:earth)
									if(x+col==b.x){
										if(y==b.y)
											img=bricks[1];
										else if(y<b.y)
											img=bricks[2];
										else
											img=bricks[9];
										break;
									}
							}
						}else if(i==row-1){
							if(j==0){
								img=bricks[6];
								for(var b:earth)
									if(x==b.x+b.width)
										if(y+row==b.y+b.height)
											img=bricks[7];
										else if(y+row>b.y+b.height)
											img=bricks[6];
										else if(y+row<b.y+b.height && y+row>b.y)
											img=bricks[7];
							}else if(j==col-1){
								img=bricks[8];
								for(var b:earth)
									if(x+col==b.x)
										if(y+row==b.y+b.height)
											img=bricks[7];
										else if(y+row>b.y+b.height)
											img=bricks[8];
										else if(y+row<b.y+b.height && y+row>b.y)
											img=bricks[7];
							}else
								img=bricks[7];
						}else{
							if(j==0){
								img=bricks[3];
								for(var b:earth)
									if(x==b.x+b.width)
										if(y+i==b.y){
											img=bricks[10];
											break;
										}else if(y+i>b.y && y+i<b.y+b.height){
											img=bricks[4];
											break;
										}
							}else if(j==col-1){
								img=bricks[5];
								for(var b:earth)
									if(x+col==b.x)
										if(y+i==b.y){
											img=bricks[11];
											break;
										}else if(y+i>b.y && y+i<b.y+b.height){
											img=bricks[4];
											break;
										}
							}
						}
						g.drawImage(img,x*size+j*size,y*size+i*size,size,size,null);
					}	
					// screen.blit(img,(self.rect.x+j*bricksize-camera[0],self.rect.y+i*bricksize-camera[1],bricksize,bricksize))
				}
			}
			// # pygame.draw.rect(screen,self.color,[self.rect.x-camera[0],self.rect.y-camera[1],self.rect.width,self.rect.height])
		}
	}
	public synchronized void playSound(){
		new Thread(new Runnable() {
			public void run() {
				try {
					Clip clip = AudioSystem.getClip();
					AudioInputStream ins=AudioSystem.getAudioInputStream(getClass().getResourceAsStream("coin.wav"));
					clip.open(ins);
					clip.start(); 
				} catch (Exception e) {
					System.err.println(e.getMessage());
				}
			}
		}).start();
	}
	class Other{
		int x,y,count;
		long starttime,endtime;
		BufferedImage []images;
		String name;
		int size;
		public Other(String n,int x,int y){
			name=n;
			this.x=x;
			this.y=y;
			if (n.substring(0,n.indexOf(":")).equals("coins")){
				images=coins;
				size=coinsize;
			}
			else if(n.substring(0,n.indexOf(":")).equals("diamonds")){
				images=diamonds;
				size=coinsize*2;
			}
		}
		public void update(){
			count=(count+1)%60;
		}
		public void show(Graphics2D g,long now){
			if(starttime<now && endtime>now)
			g.drawImage(images[count*images.length/60],x,y,size,size,null);
		}
	}
	class Player{
		String name;
		BufferedImage idle,img;
		BufferedImage []boy;
		BufferedImage []jump;
		float vx,vy;
		long time,time_energy;
		int x,y,width,height,blood,coins,imgcount,sendimgpos,sendimgtype;
		public Player(String name,int width,int height){
			this.width=width;
			this.height=height;
			this.name=name;
			blood=1000;
			x=10;
			y=500;
			vx=0;
			vy=0;
			long temp=1000*60*60*24;
			time=temp*365*50+temp*11+1000*60*30*37-new Date().getTime();
			coins=0;
			imgcount=0;
			time_energy=0;
			boy=new BufferedImage[10];
			jump=new BufferedImage[7];
			try{
				idle=ImageIO.read(new File("character"+File.separator+"idle.png"));
				for (int i=0;i<10;i++)
					boy[i]=ImageIO.read(new File("character"+File.separator+"run"+(i+1)+".png"));
				for (int i=0;i<7;i++)
					jump[i]=ImageIO.read(new File("character"+File.separator+"jump"+(i+1)+".png"));
			}catch (Exception e) {
				e.printStackTrace();
			}
		}
		public void show(Graphics2D g){
			img=null;
			if(!colliding){
				jumping=jumping+1;
				img=jump[0];
				if(jumping<10){
					img=jump[0];
					sendimgpos=0;
				}else if(jumping<20){
					img=jump[1];
					sendimgpos=1;
				}else if(jumping<30 || player.vy<0){
					img=jump[2];
					sendimgpos=2;
				}else if(player.vy<1){
					img=jump[3];
					sendimgpos=3;
				}else{
					img=jump[5];
					sendimgpos=5;
				}
				sendimgtype=2;
			}else if(colliding && vx==0){
				img=idle;
			}else{
				imgcount=(imgcount+1)%60;
				img=boy[imgcount/6];
			}
			if(showhole!=0){
				if(x>holerect.x+holerect.width)
					holepos=1;
				else if(x+width<holerect.x)
					holepos=-1;
			}
		try{
			if(colliding){
				if(holepos==0)
					g.drawImage(img,x+(flip?img.getWidth():0),y,flip?-img.getWidth():img.getWidth(),height,null);
				else if(holepos<0)
					if(x+width<holerect.x+holerect.width/2)
						g.drawImage(img,x+(flip?img.getWidth():0),y,flip?-img.getWidth():img.getWidth(),height,null);
					else if(x>holerect.x+holerect.width/2){
						x=holerect.x+holerect.width/2-5;
						running=false;
						temperzone=true;
						pressed=false;
						inittime=new Date().getTime();
						temptime=inittime+time;
					}
					else{
						int temp=holerect.x+holerect.width/2-x;
						if(flip)
							g.drawImage(img.getSubimage(img.getWidth()-temp,0,temp,height),x+temp,y,-temp,height,null);
						else
							g.drawImage(img.getSubimage(0,0,temp,height),x,y,temp,height,null);
					}
				else if(holepos>0)
					if(x>holerect.x+holerect.width/2)
						g.drawImage(img,x+(flip?img.getWidth():0),y,flip?-img.getWidth():img.getWidth(),height,null);
					else if(x+width<holerect.x+holerect.width/2){
						x=holerect.x+holerect.width/2-width+5;
						running=false;
						temperzone=true;
						pressed=false;
						inittime=new Date().getTime();
						temptime=inittime+time;
					}
					else{
						int temp=holerect.x+holerect.width/2-x;
						if(flip)
							g.drawImage(img.getSubimage(0,0,img.getWidth()-temp,height),x+img.getWidth(),y,temp-img.getWidth(),height,null);
						else
							g.drawImage(img.getSubimage(temp,0,img.getWidth()-temp,height),holerect.x+holerect.width/2,y,img.getWidth()-temp,height,null);
					}
			}else
				g.drawImage(img,x+(flip?img.getWidth():0),y,flip?-img.getWidth():img.getWidth(),height,null);
					// screen.blit(temp,(holerect.x+holerect.width/2-camera[0],friend.y-camera[1]),(holerect.x+holerect.width/2-friend.x,0,player.rect.width,player.rect.height))
			}catch(RasterFormatException e){}
		}
		public void update(){
			x+=vx;
			y+=vy;
		}
	}
}