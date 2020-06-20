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
eye = np.zeros(3)
at = np.zeros(3)
cameraUp = np.array([0.,1.,0.])
trans = np.zeros(3)
# for transformation on main object
trans_stack = []
rotation_stack = []
# True -> First-person view, False -> Quater view
camera_mode = True
scale = 10.

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

def main_object_frame():
    global trans_stack, rotation_stack, cameraUp
    M = np.identity(4)
    count = 0
    for item in trans_stack:
        N = np.identity(4)
        # translate
        if item == "W":
            N[0][3] =  0.05
        elif item == "S":
            N[0][3] = -0.05
        elif item == "A":
            N[2][3] = 0.05
        elif item == "D":
            N[2][3] = -0.05
        # scale
        elif item == "Z":
            N *= 1.1
        elif item == "X":
            N *= 0.9
        # shear
        elif item == "1":
            N[0][1] = 0.1
        elif item == "2":
            N[0][1] = -0.1
        elif item == "4":
            N[1][2] = 0.1
        elif item == "5":
            N[1][2] = -0.1
        elif item == "7":
            N[2][0] = 0.1
        elif item == "8":
            N[2][0] = -0.1
        # reflect
        elif item == "3":
            N[0][0] = -1
        elif item == "6":
            N[1][1] = -1
        elif item == "9":
            N[2][2] = -1
        # rotation
        elif item == "ROTATION":
            degree = rotation_stack[count]
            degree1 = degree[0]
            degree2 = degree[1]
            change = np.zeros(3)
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
            r = 1.
            change[0] = r * np.cos(np.radians(degree2)) * np.sin(np.radians(degree1))
            change[1] = r * np.sin(np.radians(degree2))
            change[2] = r * np.cos(np.radians(degree2)) * np.cos(np.radians(degree1))
            N[:3,:3] = get_RotationM(change)
            count += 1
        
        M = M @ N
    return M
            
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

def drawObject_glDrawElements(varr, iarr):
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT, 6*varr.itemsize, varr)
    glVertexPointer(3, GL_FLOAT, 6*varr.itemsize, ctypes.c_void_p(varr.ctypes.data + 3*varr.itemsize))
    glDrawElements(GL_TRIANGLES, iarr.size, GL_UNSIGNED_INT,iarr)

def get_RotationM(change):
    a = 1.0
    b = 1.0
    temp = change - np.array([0.,0.,1.])
    c = np.sqrt(np.dot(temp,temp))
    th = np.arccos((a*a + b*b - c*c)/(2.*a*b))
    u = np.cross(np.array([0.,0.,1.]),change)
    u /= np.sqrt(np.dot(u,u))
    R = np.array([[np.cos(th)+u[0]*u[0]*(1.-np.cos(th)), u[0]*u[1]*(1.-np.cos(th))-u[2]*np.sin(th), u[0]*u[2]*(1.-np.cos(th))+u[1]*np.sin(th)],
                  [u[1]*u[0]*(1.-np.cos(th))+u[2]*np.sin(th), np.cos(th)+u[1]*u[1]*(1.-np.cos(th)), u[1]*u[2]*(1.-np.cos(th))-u[0]*np.sin(th)],
                  [u[2]*u[0]*(1.-np.cos(th))-u[1]*np.sin(th), u[2]*u[1]*(1.-np.cos(th))+u[0]*np.sin(th), np.cos(th)+u[2]*u[2]*(1.-np.cos(th))]
                  ])
    return R

def get_th(change):
    a = 1.0
    b = b = np.sqrt(np.dot(change,change))
    temp = change - np.array([1.,0.,0.])
    c = np.sqrt(np.dot(temp,temp))
    th = np.arccos((a*a + b*b - c*c)/(2.*a*b))
    return th

obj1_collsion = False
obj1_position = np.array([0.5,0.,0.])
obj1_count = 0
obj2_collsion = False
obj2_position = np.array([0.5,0.,0.])
obj2_count = 0
def render():
    global cameraUp, trans, camera_mode, varr, iarr, obj1_position, obj1_count, obj1_collsion, obj2_position, obj2_count, obj2_collsion
    M = main_object_frame()
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT, GL_FILL)
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-scale,scale,-scale,scale,-10,10)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    if camera_mode:
        eye = (M @ np.array([0.,0.,0.,1.]))[:3]
        temp = (M @ np.array([0.,0.,1.,1.]))[:3]
        at = eye + temp
        gluLookAt(eye[0],eye[1],eye[2],at[0],at[1],at[2],cameraUp[0],cameraUp[1],cameraUp[2])
    else:
        eye = (M @ np.array([0.3,0.3,0.3,1.]))[:3]
        at = (M @ np.array([0.,0.,0.,1.]))[:3]
        gluLookAt(eye[0],eye[1],eye[2],at[0],at[1],at[2],cameraUp[0],cameraUp[1],cameraUp[2])
    
    drawframe()
    drawgrid()
    
    # Main object
    glPushMatrix()
    glMultMatrixf(M.T)
    drawObject_glDrawElements(varr[0],iarr[0])
    glPopMatrix()
    
    main_original = (M @ np.array([0.,0.,0.,1.]))[:3]
    
    # other object

    # Collision condition
    if distance(main_original, obj1_position) <= 0.3:
        obj1_collsion = True
        obj1_count = 0
    
    if distance(main_original, obj1_position) <= 0.3:
        obj2_collsion = True
        obj2_count = 0
    
    glPushMatrix()
    if obj1_collsion:
        v = obj1_position - main_original
        t = 0.01 * obj1_count
        # Pushed away
        obj1_position += v * 0.01
        # Spin 120 degrees on y-axis
        R1 = np.identity(3)
        th = np.radians(120)
        R2 = np.array([[np.cos(th), 0., np.sin(th)],
                        [0.,1.,0.],
                       [-np.sin(th),0.,np.cos(th)]
                       ])
        R = slerp(R1,R2,t)
        glTranslatef(obj1_position[0],obj1_position[1],obj1_position[2])
        glMultMatrixf(R.T)
        obj1_count += 1
        if obj1_count == 100:
            obj1_collsion = False
    else:
        glTranslatef(obj1_position[0],obj1_position[1],obj1_position[2])
    drawObject_glDrawElements(varr[1],iarr[1])
    glPopMatrix()
    
    glPushMatrix()
    if obj2_collsion:
        v = obj2_position - main_original
        # Spin -90 degrees on z-axis
        if obj2_count <= 50:
            i = obj2_count
            t = 0.02 * i
            degree = -1 * np.rad2deg(get_th(v))
            glRotatef(degree,0,1,0)
            R1 = np.identity(3)
            th = np.radians(-90)
            R2 = np.array([[np.cos(th),-np.sin(th),0.],
                           [np.sin(th),np.cos(th),0.],
                           [0.,0.,1.]
                           ])
            R = slerp(R1,R2,t)
            glTranslatef(obj2_position[0],obj2_position[1],obj2_position[2])
            glMultMatrixf(R.T)
            obj2_count += 1
        # Spin 180 degrees on z-axis
        elif obj2_count > 50 and obj2_count <= 150:
            i = obj2_count - 50
            t = 0.01 * i
            degree = -1 * np.rad2deg(get_th(v))
            glRotatef(degree,0,1,0)
            R1 = np.identity(3)
            th = np.radians(180)
            R2 = np.array([[np.cos(th),-np.sin(th),0.],
                           [np.sin(th),np.cos(th),0.],
                           [0.,0.,1.]
                           ])
            R = slerp(R1,R2,t)
            glTranslatef(obj2_position[0],obj2_position[1],obj2_position[2])
            glMultMatrixf(R.T)
            obj2_count += 1
        # Spin -90 degrees on z-axis
        elif obj2_count > 150:
            i = obj2_count - 150
            t = 0.01 * i
            degree = -1 * np.rad2deg(get_th(v))
            glRotatef(degree,0,1,0)
            R1 = np.identity(3)
            th = np.radians(-90)
            R2 = np.array([[np.cos(th),-np.sin(th),0.],
                           [np.sin(th),np.cos(th),0.],
                           [0.,0.,1.]
                           ])
            R = slerp(R1,R2,t)
            glTranslatef(obj2_position[0],obj2_position[1],obj2_position[2])
            glMultMatrixf(R.T)
            obj2_count += 1
            if obj2_count == 250:
                obj2_collsion = False
    else:
        glTranslatef(obj2_position[0],obj2_position[1],obj2_position[2])
    drawObject_glDrawElements(varr[2],iarr[2])
    glPopMatrix()
    
    
def distance(arr1,arr2):
    return np.sqrt(np.dot(arr2-arr1,arr2-arr1))

def l2norm(v):
    return np.sqrt(np.dot(v, v))

def normalized(v):
    l = l2norm(v)
    return 1/l * np.array(v)

def exp(rv):
    u = normalized(rv)
    a = l2norm(rv)
    R = np.array([[np.cos(a)+u[0]*u[0]*(1-np.cos(a)), u[0]*u[1]*(1-np.cos(a))-u[2]*np.sin(a), u[0]*u[2]*(1-np.cos(a))+u[1]*np.sin(a)],
                  [u[1]*u[0]*(1-np.cos(a))+u[2]*np.sin(a), np.cos(a)+u[1]*u[1]*(1-np.cos(a)), u[1]*u[2]*(1-np.cos(a))-u[0]*np.sin(a)],
                  [u[2]*u[0]*(1-np.cos(a))-u[1]*np.sin(a), u[2]*u[1]*(1-np.cos(a))+u[0]*np.sin(a), np.cos(a)+u[2]*u[2]*(1-np.cos(a))]
                  ])
    return R

def log(R):
    a = np.arccos((R[0][0]+R[1][1]+R[2][2]-1)/2)
    v1 = (R[2][1]-R[1][2])/(2*np.sin(a))
    v2 = (R[0][2]-R[2][0])/(2*np.sin(a))
    v3 = (R[1][0]-R[0][1])/(2*np.sin(a))
    rv = a * np.array([v1,v2,v3])
    return rv

def slerp(R1,R2,t):
    result = R1 @ exp(t*log(R1.T @ R2))
    return result

def button_callback(window,button,action,mod):
    global Left_pressed, camera_mode, init_pos
    if action == glfw.PRESS:
        init_pos = glfw.get_cursor_pos(window)
        if button == glfw.MOUSE_BUTTON_LEFT:
            Left_pressed = True
        elif button == glfw.MOUSE_BUTTON_RIGHT:
            camera_mode = not camera_mode
    elif action == glfw.RELEASE:
        if button == glfw.MOUSE_BUTTON_LEFT:
            Left_pressed = False

def cursor_callback(window,xpos,ypos):
    global degree1,degree2,trans,cameraUp, trans_stack, rotation_stack
    # Main object rotation
    if Left_pressed:
        degree1 += (init_pos[0] - xpos) * 0.02
        degree2 += (-init_pos[1] + ypos) * 0.02
        trans_stack.append("ROTATION")
        rotation_stack.append([degree1,degree2])
    
def scroll_callback(window,xoffset,yoffset):
    global scale
    if scale <= 0.1 and yoffset == 1:
        scale = 0.1
        return
    scale -= 0.1 * yoffset


def key_callback(window, key, scancode, action, mods):
    global trans_stack
    if action==glfw.PRESS or action==glfw.REPEAT:
        if key==glfw.KEY_W:
            trans_stack.append("W")
        elif key==glfw.KEY_S:
            trans_stack.append("S")
        elif key==glfw.KEY_A:
            trans_stack.append("A")
        elif key==glfw.KEY_D:
            trans_stack.append("D")
        elif key==glfw.KEY_Z:
            trans_stack.append("Z")
        elif key==glfw.KEY_X:
            trans_stack.append("X")
        elif key==glfw.KEY_1:
            trans_stack.append("1")
        elif key==glfw.KEY_2:
            trans_stack.append("2")
        elif key==glfw.KEY_3:
            trans_stack.append("3")
        elif key==glfw.KEY_4:
            trans_stack.append("4")
        elif key==glfw.KEY_5:
            trans_stack.append("5")
        elif key==glfw.KEY_6:
            trans_stack.append("6")
        elif key==glfw.KEY_7:
            trans_stack.append("7")
        elif key==glfw.KEY_8:
            trans_stack.append("8")
        elif key==glfw.KEY_9:
            trans_stack.append("9")

varr = []
iarr = []
def main():
    global varr, iarr
    if not glfw.init():
        return
    window = glfw.create_window(700,700,'2015004302', None,None)
    if not window:
        glfw.terminate()
        return
    
    # object load from file
    file_name = ["file1","file2","file3"]
    for item in file_name:
        file = open(item,'r')
        full_list = file.readlines()
        temp_v, temp_i = make_varr_iarr(full_list)
        varr.append(temp_v)
        iarr.append(temp_i)
    
    glfw.make_context_current(window)
    glfw.set_cursor_pos_callback(window,cursor_callback)
    glfw.set_mouse_button_callback(window,button_callback)
    glfw.set_scroll_callback(window,scroll_callback)
    glfw.set_key_callback(window,key_callback)
    glfw.swap_interval(1)
    
    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()