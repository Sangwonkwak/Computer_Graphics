import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

Left_pressed = False
Right_pressed = False
degree1 = 0.
degree2 = 0.
init_pos = np.array([0,0])
eye = np.array([0.,0.,.1])
at = np.array([0.,0.,0.])
cameraUp = np.array([0.,1.,0.])
scale = 1.
trans = np.array([0.,0.,0.])
t1 = 0.

def render():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-scale,scale,-scale,scale,-1,1)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    real_eye = eye + trans
    real_at = at + trans
    gluLookAt(real_eye[0],real_eye[1],real_eye[2],real_at[0],real_at[1],real_at[2],cameraUp[0],cameraUp[1],cameraUp[2])
    
    drawframe()
    drawgrid()
    drawModel()

# draw grid
def drawgrid():
    for i in range(21):
        glPushMatrix()
        glBegin(GL_LINES)
        glColor3ub(80,80,80)
        glVertex3fv(np.array([-1.0+0.1*i,0.,1.0]))
        glVertex3fv(np.array([-1.0+0.1*i,0.,-1.0]))
        glVertex3fv(np.array([1.0,0.,-1.0+0.1*i]))
        glVertex3fv(np.array([-1.0,0.,-1.0+0.1*i]))
        glEnd()
        glPopMatrix()

# draw my hierarchical model
def drawModel():
    t2 = glfw.get_time()
    #period = 2
    t = t2 - t1
    temp = t % 2.
    r = 0.025
    # center tf
    glPushMatrix()
    glRotatef(t*(60./np.pi),0,1,0)
    glTranslatef(0.,r,0.)
    if temp < 1.0: 
        glTranslatef(0.,0.25*(np.sqrt(3)/2.)*temp,0.5)
    else:
        glTranslatef(0.,0.25*(np.sqrt(3)/2.)*(2.0-temp),0.5)
    # center draw
    glColor3ub(180,180,180)
    glPushMatrix()
    glScalef(r,r,r)
    drawSphere()
    glPopMatrix()
    # link_left tf
    glPushMatrix()
    if temp < 1.0:
        glRotatef(60.*temp,0,0,1)
    else:
        glRotatef(60.*(2.-temp),0,0,1)
    glTranslatef(-0.125,0.,0.)
    # link_left draw
    glColor3ub(0,200,0)
    glPushMatrix()
    glScalef(0.2,0.05,0.1)
    drawUnitCube()
    glPopMatrix()
    # joint_left tf
    glPushMatrix()
    glTranslatef(-0.125,0.,0.)
    if temp < 1.0:
        glRotatef(-60.*temp,0,0,1)
    else:
        glRotatef(-60.*(2.-temp),0,0,1)
    # joint_left draw
    glColor3ub(180,180,180)
    glPushMatrix()
    glScalef(r,r,r)
    drawSphere()
    glPopMatrix()
    # tail tf
    glPushMatrix()
    if temp < 1.0:
        glRotatef(15.-30.*temp,0,1,0)
    else:
        glRotatef(-45+30.*temp,0,1,0)
    glTranslatef(-0.075,0.,0.)
    # tail draw
    glColor3ub(0,200,0)
    glPushMatrix()
    glScalef(0.1,0.05,0.1)
    drawUnitCube()
    glPopMatrix()
    
    glPopMatrix()
    glPopMatrix()
    glPopMatrix()
    
    # link_right tf
    glPushMatrix()
    if temp < 1.0:
        glRotatef(-60.*temp,0,0,1)
    else:
        glRotatef(-60.*(2.-temp),0,0,1)
    glTranslatef(0.125,0.,0.)
    # link_right draw
    glColor3ub(0,200,0)
    glPushMatrix()
    glScalef(0.2,0.05,0.1)
    drawUnitCube()
    glPopMatrix()
    # joint_right tf
    glPushMatrix()
    glTranslatef(0.125,0.,0.)
    if temp < 1.0:
        glRotatef(60.*temp,0,0,1)
    else:
        glRotatef(60.*(2.-temp),0,0,1)
    # joint_right draw
    glColor3ub(180,180,180)
    glPushMatrix()
    glScalef(r,r,r)
    drawSphere()
    glPopMatrix()
    # head tf
    glPushMatrix()
    if temp < 1.0:
        glRotatef(15.-30.*temp,0,1,0)
    else:
        glRotatef(-45+30.*temp,0,1,0)
    glTranslatef(0.1,0.,0.)
    # head draw
    glColor3ub(0,200,0)
    glPushMatrix()
    glScalef(0.15,0.05,0.15)
    drawUnitCube()
    glPopMatrix()
    # antenna_left tf
    glPushMatrix()
    glTranslatef(0.05,0.,-0.06)
    if temp < 1.0:
        glRotatef(15.-30.*temp,0,0,1)
    else:
        glRotatef(-45+30.*temp,0,0,1)
    # antenna_left draw
    glPushMatrix()
    glColor3ub(100,100,100)
    glBegin(GL_LINES)
    glVertex3fv(np.array([0.,0.,0.]))
    glVertex3fv(np.array([0.,0.3,0.]))
    glEnd()
    glPopMatrix()
    glPopMatrix()
    # antenna_right tf
    glPushMatrix()
    glTranslatef(0.05,0.,0.06)
    if temp < 1.0:
        glRotatef(-15.+30.*temp,0,0,1)
    else:
        glRotatef(45-30.*temp,0,0,1)
    # antenna_right draw
    glPushMatrix()
    glColor3ub(100,100,100)
    glBegin(GL_LINES)
    glVertex3fv(np.array([0.,0.,0.]))
    glVertex3fv(np.array([0.,0.3,0.]))
    glEnd()
    glPopMatrix()
    
    glPopMatrix()
    glPopMatrix()
    glPopMatrix()
    glPopMatrix()
    glPopMatrix()

def drawframe():
    glBegin(GL_LINES)
    glColor3ub(255,0,0)
    glVertex3fv(np.array([-.5,0.,0.]))
    glVertex3fv(np.array([.5,0.,0.]))
    glColor3ub(0,255,0)
    glVertex3fv(np.array([0.,-.5,0.]))
    glVertex3fv(np.array([0.,.5,0.]))
    glColor3ub(0,0,255)
    glVertex3fv(np.array([0.,0.,-.5]))
    glVertex3fv(np.array([0.,0.,.5]))
    glEnd()

def drawSphere(numLats=12, numLongs=12): 
    for i in range(0, numLats + 1): 
        lat0 = np.pi * (-0.5 + float(float(i - 1) / float(numLats)))
        z0 = np.sin(lat0) 
        zr0 = np.cos(lat0)
        
        lat1 = np.pi * (-0.5 + float(float(i) / float(numLats))) 
        z1 = np.sin(lat1) 
        zr1 = np.cos(lat1)
        
        # Use Quad strips to draw the sphere
        glBegin(GL_QUAD_STRIP)
        
        for j in range(0, numLongs + 1):
            lng = 2 * np.pi * float(float(j - 1) / float(numLongs)) 
            x = np.cos(lng) 
            y = np.sin(lng) 
            glVertex3f(x * zr0, y * zr0, z0) 
            glVertex3f(x * zr1, y * zr1, z1)
        glEnd()

def drawUnitCube():
    glBegin(GL_QUADS)
    glVertex3f( 0.5, 0.5,-0.5)
    glVertex3f(-0.5, 0.5,-0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f( 0.5, 0.5, 0.5) 
                
    glVertex3f( 0.5,-0.5, 0.5)
    glVertex3f(-0.5,-0.5, 0.5)
    glVertex3f(-0.5,-0.5,-0.5)
    glVertex3f( 0.5,-0.5,-0.5) 
                             
    glVertex3f( 0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(-0.5,-0.5, 0.5)
    glVertex3f( 0.5,-0.5, 0.5)
                             
    glVertex3f( 0.5,-0.5,-0.5)
    glVertex3f(-0.5,-0.5,-0.5)
    glVertex3f(-0.5, 0.5,-0.5)
    glVertex3f( 0.5, 0.5,-0.5)
 
    glVertex3f(-0.5, 0.5, 0.5) 
    glVertex3f(-0.5, 0.5,-0.5)
    glVertex3f(-0.5,-0.5,-0.5) 
    glVertex3f(-0.5,-0.5, 0.5) 
                             
    glVertex3f( 0.5, 0.5,-0.5) 
    glVertex3f( 0.5, 0.5, 0.5)
    glVertex3f( 0.5,-0.5, 0.5)
    glVertex3f( 0.5,-0.5,-0.5)
    glEnd()

def button_callback(window,button,action,mod):
    global Left_pressed,Right_pressed,init_pos
    if action == glfw.PRESS:
        init_pos = glfw.get_cursor_pos(window)
        print(init_pos)
        if button == glfw.MOUSE_BUTTON_LEFT:
            Left_pressed = True
        elif button == glfw.MOUSE_BUTTON_RIGHT:
            Right_pressed = True
    elif action == glfw.RELEASE:
        if button == glfw.MOUSE_BUTTON_LEFT:
            Left_pressed = False
        elif button == glfw.MOUSE_BUTTON_RIGHT:
            Right_pressed = False

def cursor_callback(window,xpos,ypos):
    global eye,at,degree1,degree2,trans,cameraUp
    if Left_pressed:
        degree1 += (init_pos[0] - xpos) * 0.02
        degree2 += (-init_pos[1] + ypos) * 0.02
        if degree2 >= 0.:
            degree2 %= 360.
        else:
            degree2 %= -360.
        
        if 90. <= degree2 and degree2 <= 270.:
            cameraUp[1] = -1.
        elif -90. >= degree2 and degree2 >= -270.:
            cameraUp[1] = -1.
        else:
            cameraUp[1] = 1.
        eye[0] = 0.1 * np.cos(np.radians(degree2)) * np.sin(np.radians(degree1))
        eye[1] = 0.1 * np.sin(np.radians(degree2))
        eye[2] = 0.1 * np.cos(np.radians(degree2)) * np.cos(np.radians(degree1))
        
    elif Right_pressed:
        cameraFront = eye - at
        temp1 = np.cross(cameraFront,cameraUp)
        u = temp1/np.sqrt(np.dot(temp1,temp1))
        temp2 = np.cross(u,cameraFront)
        w = temp2/np.sqrt(np.dot(temp2,temp2))
        trans += u *(-init_pos[0]+xpos)*0.0001
        trans += w *(-init_pos[1]+ypos)*0.0001
        
def scroll_callback(window,xoffset,yoffset):
    global scale
    if scale <= 0.1 and yoffset == 1:
        scale = 0.1
        return
    scale -= 0.1 * yoffset

def main():
    global t1
    if not glfw.init():
        return
    t1 = glfw.get_time()
    window = glfw.create_window(700,700,'2015004302', None,None)
    if not window:
        glfw.terminate()
        return
    
    glfw.make_context_current(window)
    glfw.set_cursor_pos_callback(window,cursor_callback)
    glfw.set_mouse_button_callback(window,button_callback)
    glfw.set_scroll_callback(window,scroll_callback)
    glfw.swap_interval(1)
    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()