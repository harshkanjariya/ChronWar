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
	private Rectangle []blocks=new Rectangle[5];
	public GamePanel(){
		x=100;
		y=200;
		vx=5;
		vy=-2;
		a=0.1;
		r=50;
		friction=0.9;
		Thread t=new Thread(this);
		t.start();
		blocks[0]=new Rectangle(50,500,500,50);
		blocks[1]=new Rectangle(500,600,500,50);
		blocks[2]=new Rectangle(1000,50,50,500);
		blocks[3]=new Rectangle(20,50,50,500);
		blocks[4]=new Rectangle(50,50,500,50);
	}
	public void paint(Graphics g){
		g.setColor(new Color(255,255,255,255));
		g.fillRect(0,0,getWidth(),getHeight());
		g.setColor(Color.red);
		g.fillOval((int)(x-r),(int)(y-r),(int)(2*r),(int)(2*r));
		g.setColor(Color.green);
		for(Rectangle rc:blocks)
			g.fillRect(rc.x,rc.y,rc.width,rc.height);
		g.setColor(Color.blue);
	}
	public void run(){
		while(true){
			x+=vx;
			y+=vy;
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
			vy=-5;
		}else if(c==KeyEvent.VK_LEFT){
			vx=-5;
		}else if(c==KeyEvent.VK_RIGHT){
			vx=5;
		}
	}
	public void keyReleased(KeyEvent e){}
	public void keyTyped(KeyEvent e){}
	private boolean intersact(Rectangle rc){
		if(x>rc.x && x<rc.x+rc.width){
			if(y<rc.y+rc.height/2){
				if(y+r>rc.y){
					vy=-Math.abs(vy*friction);
					vx=vx*friction;
					return true;
				}
			}
			else if(y>rc.y+rc.height/2){
				if(y-r<rc.y+rc.height){
					vy=Math.abs(vy*friction);
					vx=vx*friction;
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