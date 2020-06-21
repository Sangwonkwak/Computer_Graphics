import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from OpenGL.arrays import vbo
import ctypes

Left_pressed = False
Right_pressed = False
degree1 = 0.
degree2 = 0.
init_pos = np.array([0,0])
eye = np.array([0.,0.,.1])
at = np.array([0.,0.,0.])
cameraUp = np.array([0.,1.,0.])
scale = 2.
# True = GL_FILL, False = GL_LINE
mode_type = True
# True = flat_shading, False = smooth shading
shading_type = True
trans = np.array([0.,0.,0.])
t1 = 0.
count = ''
varr = np.zeros(1)
varr2 = np.zeros(1)
iarr = np.zeros(1)

def render():
    global mode_type, shading_type
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    
    if mode_type:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

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
    
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_LIGHT2)
    glEnable(GL_LIGHT3)
    glEnable(GL_LIGHT4)
    glEnable(GL_NORMALIZE)
    
    # Light setting
    lightPos0 = (1., 1., 1., 1.)
    lightPos1 = (1., 1., -1., 1.)
    lightPos2 = (-1., 1., 1., 1.)
    lightPos3 = (-1., 1., -1., 1.)
    lightPos4 = (0., -1., 0., 0.)
    glLightfv(GL_LIGHT0,GL_POSITION,lightPos0)
    glLightfv(GL_LIGHT1,GL_POSITION,lightPos1)
    glLightfv(GL_LIGHT2,GL_POSITION,lightPos2)
    glLightfv(GL_LIGHT3,GL_POSITION,lightPos3)
    glLightfv(GL_LIGHT4,GL_POSITION,lightPos4)
    
    lightColor1 = (.45, .45, .45, .45)
    lightColor2 = (.3, .3, .3, .3)
    ambientLightColor = (.1,.1,.1,1.)
    glLightfv(GL_LIGHT0,GL_DIFFUSE,lightColor1)
    glLightfv(GL_LIGHT0,GL_SPECULAR,lightColor1)
    glLightfv(GL_LIGHT0,GL_AMBIENT,ambientLightColor)
    glLightfv(GL_LIGHT1,GL_DIFFUSE,lightColor1)
    glLightfv(GL_LIGHT1,GL_SPECULAR,lightColor1)
    glLightfv(GL_LIGHT1,GL_AMBIENT,ambientLightColor)
    glLightfv(GL_LIGHT2,GL_DIFFUSE,lightColor1)
    glLightfv(GL_LIGHT2,GL_SPECULAR,lightColor1)
    glLightfv(GL_LIGHT2,GL_AMBIENT,ambientLightColor)
    glLightfv(GL_LIGHT3,GL_DIFFUSE,lightColor1)
    glLightfv(GL_LIGHT3,GL_SPECULAR,lightColor1)
    glLightfv(GL_LIGHT3,GL_AMBIENT,ambientLightColor)
    glLightfv(GL_LIGHT4,GL_DIFFUSE,lightColor2)
    glLightfv(GL_LIGHT4,GL_SPECULAR,lightColor2)
    glLightfv(GL_LIGHT4,GL_AMBIENT,ambientLightColor)
    
    # Object color setting
    objectColor = (.3, .3, .7, 1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT,GL_AMBIENT_AND_DIFFUSE,objectColor)
    glMaterialfv(GL_FRONT,GL_SHININESS,10)
    glMaterialfv(GL_FRONT,GL_SPECULAR,specularObjectColor)
    
    glPushMatrix()
    # Resize_ratio
    resize_ratio = 0.02
    glScalef(resize_ratio,resize_ratio,resize_ratio)
    if shading_type:
        drawObject_glDrawArray()
    else:
        drawObject_glDrawElements()
    glPopMatrix()
    glDisable(GL_LIGHTING)

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

def button_callback(window,button,action,mod):
    global Left_pressed,Right_pressed,init_pos
    if action == glfw.PRESS:
        init_pos = glfw.get_cursor_pos(window)
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
    global eye,at,degree1,degree2,trans,cameraUp,scale
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
        r = .1
        eye[0] = r * np.cos(np.radians(degree2)) * np.sin(np.radians(degree1))
        eye[1] = r * np.sin(np.radians(degree2))
        eye[2] = r * np.cos(np.radians(degree2)) * np.cos(np.radians(degree1))
        
    elif Right_pressed:
        cameraFront = eye - at
        temp1 = np.cross(cameraFront,cameraUp)
        u = temp1/np.sqrt(np.dot(temp1,temp1))
        temp2 = np.cross(u,cameraFront)
        w = temp2/np.sqrt(np.dot(temp2,temp2))
        trans += u *(-init_pos[0]+xpos)*0.0001
        trans += w *(-init_pos[1]+ypos)*0.0001

def drawObject_glDrawArray():
    global varr
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT, 6*varr.itemsize, varr)
    glVertexPointer(3, GL_FLOAT, 6*varr.itemsize, ctypes.c_void_p(varr.ctypes.data + 3*varr.itemsize))
    glDrawArrays(GL_TRIANGLES, 0, int(varr.size/6))

def drawObject_glDrawElements():
    global varr2, iarr
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT, 6*varr2.itemsize, varr2)
    glVertexPointer(3, GL_FLOAT, 6*varr2.itemsize, ctypes.c_void_p(varr2.ctypes.data + 3*varr2.itemsize))
    glDrawElements(GL_TRIANGLES, iarr.size, GL_UNSIGNED_INT,iarr)

def scroll_callback(window,xoffset,yoffset):
    global scale
    if scale <= 0.1 and yoffset == 1:
        scale = 0.1
        return
    scale -= 0.1 * yoffset

def drop_callback(window,paths):
    global varr, count, varr2, iarr
    
    file_name = ''.join(paths)
    file = open(file_name,'r')
    full_list = file.readlines()
    varr = make_varr(full_list)
    varr2, iarr = make_varr_iarr(full_list)
    print('File name: %s'%(file_name))
    print('Total number of faces: %d\nNumber of faces with 3 vertices: %d\nNumer of faces with 4 vertices: %d\nNumber of faces with more than 4 vertices: %d'
          %(count[0],count[1],count[2],count[3]))
    file.close()

# Flat shading    
def make_varr(full_list):
    global count
    count = np.zeros(4)
    temp_v = []
    temp_vn = []
    # Get data of vertex, normal vector
    for line in full_list:
        temp = line.split(' ')
        if temp[0] == 'v':
            temp_list = []
            for i in range(3):
                temp_list.append(float(temp[i+1]))
            temp_v.append(tuple(temp_list))
        elif temp[0] == 'vn':
            temp_list = []
            for i in range(3):
                temp_list.append(float(temp[i+1]))
            temp_vn.append(tuple(temp_list))
    
    temp_varr = []
    # Make varr for mesh rendering
    for line in full_list:
        temp = line.split(' ')
        if temp[0] == 'f':
            count[0] += 1
            # tri
            if len(temp) == 4:
                count[1] += 1
                for i in range(3):
                    temp_copy = temp[i+1]
                    temp_el = temp_copy.split('/')
                    v_index = int(temp_el[0])
                    vn_index = int(temp_el[2])
                    temp_varr.append(temp_vn[vn_index-1])
                    temp_varr.append(temp_v[v_index-1])
            # other case(4, 5, ...)
            else:
                n = len(temp) - 1
                vertex_order = []
                vn_index = 0
                if n == 4:
                    count[2] += 1
                else:
                    count[3] += 1
                for i in range(n):
                    temp_copy = temp[i+1]
                    temp_el = temp_copy.split('/')
                    vertex_order.append(int(temp_el[0]))
                    vn_index = int(temp_el[2])
                for j in range(n-2):
                    temp_varr.append(temp_vn[vn_index-1])
                    temp_varr.append(temp_v[vertex_order[0]-1])
                    temp_varr.append(temp_vn[vn_index-1])
                    temp_varr.append(temp_v[vertex_order[j+1]-1])
                    temp_varr.append(temp_vn[vn_index-1])
                    temp_varr.append(temp_v[vertex_order[j+2]-1])
    
    return np.array(temp_varr,'float32')

# Smooth shading
def make_varr_iarr(full_list):
    temp_v = []
    temp_vn = []
    # Get data of vertex, normal vector
    for line in full_list:
        temp = line.split(' ')
        if temp[0] == 'v':
            temp_list = []
            for i in range(3):
                temp_list.append(float(temp[i+1]))
            temp_v.append(tuple(temp_list))
        elif temp[0] == 'vn':
            temp_list = []
            for i in range(3):
                temp_list.append(float(temp[i+1]))
            temp_vn.append(tuple(temp_list))
    
    temp_varr = []
    temp_iarr = []
    each_vn_sum = np.zeros((len(temp_v),3))
    each_vn_count = np.zeros(len(temp_v))
    # Make varr, iarr for mesh rendering
    for line in full_list:
        temp = line.split(' ')
        if temp[0] == 'f':
            #tri
            if len(temp) == 4:
                temp_list = []
                for i in range(3):
                    temp_copy = temp[i+1]
                    temp_el = temp_copy.split('/')
                    each_vn_sum[int(temp_el[0])-1] += temp_vn[int(temp_el[2])-1]
                    each_vn_count[int(temp_el[0])-1] += 1.
                    temp_list.append(int(temp_el[0])-1)
                temp_iarr.append(tuple(temp_list))
            # other case(4, 5, ...)
            else:
                n = len(temp) - 1
                vertex_order = []
                vn_index = 0
                for i in range(n):
                    temp_copy = temp[i+1]
                    temp_el = temp_copy.split('/')
                    vertex_order.append(int(temp_el[0]))
                    vn_index = int(temp_el[2])
                for j in range(n-2):
                    temp_arr = np.array([vertex_order[0]-1, vertex_order[j+1]-1, vertex_order[j+2]-1])
                    temp_list = []
                    for i in range(3):
                        each_vn_sum[temp_arr[i]] += temp_vn[vn_index-1]
                        each_vn_count[temp_arr[i]] += 1.
                        temp_list.append(temp_arr[i])
                    temp_iarr.append(tuple(temp_list))
    for i in range(len(temp_v)):
        each_vn = each_vn_sum[i] / each_vn_count[i]
        temp_varr.append(tuple(each_vn))
        temp_varr.append(temp_v[i])
    
    return np.array(temp_varr,'float32'), np.array(temp_iarr) 
                        
def key_callback(window, key, scancode, action, mods):
    global mode_type, shading_type
    if action==glfw.PRESS or action==glfw.REPEAT:
        if key==glfw.KEY_Z:
            mode_type = not mode_type
        if key==glfw.KEY_S:
            shading_type = not shading_type
            
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
    glfw.set_drop_callback(window,drop_callback)
    glfw.set_key_callback(window,key_callback)
    glfw.swap_interval(1)
    
    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()