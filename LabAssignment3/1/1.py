import glfw
from OpenGL.GL import *
import numpy as np

def render(T):
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
    # draw triangle
    glBegin(GL_TRIANGLES)
    glColor3ub(255, 255, 255)
    glVertex2fv( (T @ np.array([.0,.5,1.]))[:-1] )
    glVertex2fv( (T @ np.array([.0,.0,1.]))[:-1] )
    glVertex2fv( (T @ np.array([.5,.0,1.]))[:-1] )
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
    glfw.swap_interval(1)
    
    while not glfw.window_should_close(window):
        glfw.poll_events()
        t2 = glfw.get_time()
        # t seconds have elapsed since the program was executed
        t = t2 - t1
        # radius
        r = 0.5
        S = np.array([[np.cos(t),-np.sin(t),r*np.cos(t)],
                      [np.sin(t),np.cos(t),r*np.sin(t)],
                      [0.,0.,1.]])
        render(S)
        
        glfw.swap_buffers(window)
    glfw.terminate()
    
if __name__ == "__main__":
    main()