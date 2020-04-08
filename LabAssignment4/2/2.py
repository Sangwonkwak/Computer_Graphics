import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

def render(M):
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    # draw cooridnate
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([1.,0.]))
    glColor3ub(0, 255, 0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([0.,1.]))
    glEnd()
    
    glColor3ub(255, 255, 255)
    # draw point p
    glBegin(GL_POINTS)
    # your implementation
    glVertex2fv( (M @ np.array([1.,0.,1.]))[:-1] )
    glEnd()
    
    # draw vector v
    glBegin(GL_LINES)
    # your implementation
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv( (M @ np.array([0.5,0.,1.]))[:-1] )
    glEnd()

def main():
    if not glfw.init():
        return
    window = glfw.create_window(480,480,"2015004302",None,None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    t1 = glfw.get_time()
    #glfw.swap_interval(1)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        t2 = glfw.get_time()
        # t seconds have elapsed since the program was executed
        t = t2 - t1
        S = np.array([[np.cos(t),-np.sin(t),0.],
                      [np.sin(t),np.cos(t),0.],
                      [0.,0.,1.]])
        render(S)
        glfw.swap_buffers(window)
        
    glfw.terminate()
    
if __name__ == "__main__":
    main()