import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

stack1 = []

def render():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    # draw cooridnates
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([1.,0.]))
    glColor3ub(0, 255, 0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([0.,1.]))
    glEnd()
    
    glColor3ub(255, 255, 255)
    ###########################
    # implement here
    S = stack1.copy()
    set_tf_matrix(S)
    ###########################
    drawTriangle()
        
def drawTriangle():
    glBegin(GL_TRIANGLES)
    glVertex2fv(np.array([0.,.5]))
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([.5,0.]))
    glEnd()

def key_callback(window,key,scancode,action,mods):
    global stack1
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_Q:
            stack1.append("Q")
        elif key == glfw.KEY_E:
            stack1.append("E")
        elif key == glfw.KEY_A:
            stack1.append("A")
        elif key == glfw.KEY_D:
            stack1.append("D")
        elif key == glfw.KEY_1:
            stack1.append("1")

#Function to set current transformation matrix
def set_tf_matrix(stack):
    global stack1
    #When stack is empty
    if not stack:
        return
    temp = stack.pop()
    if temp == "Q":
        glTranslatef(-0.1,0.,0.)
    elif temp == "E":
        glTranslatef(0.1,0.,0.)
    elif temp == "A":
        glRotatef(10,0,0,1)
    elif temp == "D":
        glRotatef(-10,0,0,1)
    elif temp == "1":
        glLoadIdentity()
        stack1.clear()
        return
    set_tf_matrix(stack)

def main():
    if not glfw.init():
        return
    window = glfw.create_window(480,480,"2015004302",None,None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window,key_callback)
    
    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)
    glfw.terminate()
    
if __name__ == "__main__":
    main()
        