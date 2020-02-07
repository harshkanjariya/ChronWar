import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
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
		new Game();
	}
}
class GamePanel extends JPanel implements Runnable,KeyListener{
	double x,y,vx,vy,a,r,friction;
	private Point camera;
	private boolean pressed;
	private Rectangle []blocks=new Rectangle[5];
	public GamePanel(){
		x=550;
		y=250;
		vx=0;
		vy=-2;
		a=0.1;
		r=30;
		camera=new Point();
		friction=0.9;
		Thread t=new Thread(this);
		t.start();
		blocks[0]=new Rectangle(-500,500,500,50);
		blocks[1]=new Rectangle(0,600,500,50);
		blocks[2]=new Rectangle(500,400,500,50);
		blocks[3]=new Rectangle(1000,300,500,50);
		blocks[4]=new Rectangle(1800,100,500,50);
	}
	public void paint(Graphics g){
		Graphics2D g2d=(Graphics2D)g;
		g2d.setColor(new Color(255,255,255,255));
		g2d.fillRect(0,0,getWidth(),getHeight());
		g2d.translate(-camera.x,-camera.y);
		g2d.setColor(Color.red);
		g2d.fillOval((int)(x-r),(int)(y-r),(int)(2*r),(int)(2*r));
		g2d.setColor(Color.green);
		for(Rectangle rc:blocks)
			g2d.fillRect(rc.x,rc.y,rc.width,rc.height);
		g2d.setColor(Color.blue);
	}
	public void run(){
		while(true){
			if(pressed)
				x+=vx;
			y+=vy;
			if(x-camera.x>getWidth()/2 && vx>0)
				camera.x=(int)(x-getWidth()/2);
			else if(x-camera.x<getWidth()/4 && vx<0)
				camera.x=(int)(x-getWidth()/4);
			if(y-camera.y>getHeight()*3/4 && vy>0)
				camera.y=(int)(y-getHeight()*3/4);
			else if(y-camera.y<getHeight()/4 && vy<0)
				camera.y=(int)(y-getHeight()/4);
			boolean inter=false;
			for(Rectangle rc:blocks)
				inter=inter|intersact(rc);
			if(!inter)
				vy+=a;
			repaint();
			try{Thread.sleep(10);}catch(Exception e){e.printStackTrace();}
		}
	}
	public void keyPressed(KeyEvent e){
		int c=e.getKeyCode();
		if(c==KeyEvent.VK_UP){
			boolean touch=false;
			for(Rectangle rc:blocks){
				if(x>rc.x && x<rc.x+rc.width && y+r+2>rc.y){
					touch=true;
					break;
				}
			}
			if(touch)
				vy=-5;
		}else if(c==KeyEvent.VK_LEFT){
			pressed=true;
			vx=-5;
		}else if(c==KeyEvent.VK_RIGHT){
			pressed=true;
			vx=5;
		}else if(c==KeyEvent.VK_SPACE){
			boolean touch=false;
			for(Rectangle rc:blocks){
				if(x>rc.x && x<rc.x+rc.width && y+r+2>rc.y){
					touch=true;
					break;
				}
			}
			if(touch)
				vy=-7;
		}
	}
	public void keyReleased(KeyEvent e){
		int c=e.getKeyCode();
		if(c==KeyEvent.VK_LEFT){
			pressed=false;
		}else if(c==KeyEvent.VK_RIGHT){
			pressed=false;
		}
	}
	public void keyTyped(KeyEvent e){}
	private boolean intersact(Rectangle rc){
		if(x>rc.x && x<rc.x+rc.width){
			if(y<rc.y+rc.height/2){
				if(y+r>rc.y){
					y=rc.y-r;
					vy=0;
					// vy=-Math.abs(vy*friction);
					return true;
				}
			}
			else if(y>rc.y+rc.height/2){
				if(y-r<rc.y+rc.height){
					y=rc.y+rc.height+r;
					vy=0;
					// vy=Math.abs(vy*friction);
					return true;
				}
			}
		}else if(y>rc.y && y<rc.y+rc.height){
			if(x<rc.x+rc.width/2){
				if(x+r>rc.x){
					vx=-Math.abs(vx*friction);
					return true;
				}
			}
			else if(x>rc.x+rc.width/2){
				if(x-r<rc.x+rc.width){
					vx=Math.abs(vx*friction);
					return true;
				}
			}
		}
		return false;
	}
}