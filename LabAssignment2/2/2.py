import glfw
import numpy as np
from OpenGL.GL import *
p_key = 0

#Make vertices and shape
def render():
    angle = np.linspace(0.,330.,12)
    x = np.cos(angle*np.pi/180.)
    y = np.sin(angle*np.pi/180.)
    
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glBegin(p_key)
    for i in range(12):
        glVertex2f(x[i],y[i])
    glEnd()

def key_callback(window,key,scancode,action,mods):
    global p_key
    if key==glfw.KEY_1:
        p_key = GL_POINTS
    if key==glfw.KEY_2:
        p_key = GL_LINES
    if key==glfw.KEY_3:
        p_key = GL_LINE_STRIP
    if key==glfw.KEY_4:
        p_key = GL_LINE_LOOP
    if key==glfw.KEY_5:
        p_key = GL_TRIANGLES
    if key==glfw.KEY_6:
        p_key = GL_TRIANGLE_STRIP
    if key==glfw.KEY_7:
        p_key = GL_TRIANGLE_FAN
    if key==glfw.KEY_8:
        p_key = GL_QUADS
    if key==glfw.KEY_9:
        p_key = GL_QUAD_STRIP
    if key==glfw.KEY_0:
        p_key = GL_POLYGON
    
def main():
    if not glfw.init():
        return
    window = glfw.create_window(480,480,"2015004302",None,None)
    if not window:
        glfw.terminate()
        return 
    
    glfw.set_key_callback(window,key_callback)
    glfw.make_context_current(window)
    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)
    
    glfw.terminate()
    
if __name__ == "__main__":
    main()