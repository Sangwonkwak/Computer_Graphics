import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from OpenGL.arrays import vbo
import ctypes
import os

Left_pressed = False
Right_pressed = False
init_pos = np.array([0,0])
cameraUp = np.array([0.,1.,0.])
trans = np.zeros(3)
# for transformation on main object
trans_stack = []
rotation_stack = []
# True -> First-person view, False -> Quater view
camera_mode = True
scale = 20.
main_scale = 0.2

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
    degree1 = 0.
    degree2 = 0.
    for item in trans_stack:
        N = np.identity(4)
        # translate
        if item == "W":
            th = np.radians(degree1)
            K = np.identity(4)
            K[:3,:3] = np.array([[np.cos(th),0.,np.sin(th)],
                                 [0.,1.,0.],
                                 [-np.sin(th),0.,np.cos(th)]
                                 ])
            temp = K @ np.array([0.,0.,0.5,1.])
            N[0,3] = temp[0]
            N[2,3] = temp[2]
        elif item == "S":
            th = np.radians(degree1)
            K = np.identity(4)
            K[:3,:3] = np.array([[np.cos(th),0.,np.sin(th)],
                                 [0.,1.,0.],
                                 [-np.sin(th),0.,np.cos(th)]
                                 ])
            temp = K @ np.array([0.,0.,-0.5,1.])
            N[0,3] = temp[0]
            N[2,3] = temp[2]
        elif item == "A":
            th = np.radians(degree1)
            K = np.identity(4)
            K[:3,:3] = np.array([[np.cos(th),0.,np.sin(th)],
                                 [0.,1.,0.],
                                 [-np.sin(th),0.,np.cos(th)]
                                 ])
            temp = K @ np.array([0.5,0.,0.,1.])
            N[0,3] = temp[0]
            N[2,3] = temp[2]
        elif item == "D":
            th = np.radians(degree1)
            K = np.identity(4)
            K[:3,:3] = np.array([[np.cos(th),0.,np.sin(th)],
                                 [0.,1.,0.],
                                 [-np.sin(th),0.,np.cos(th)]
                                 ])
            temp = K @ np.array([-0.5,0.,0.,1.])
            N[0,3] = temp[0]
            N[2,3] = temp[2]
        # shear
        elif item == "1":
            N[0][1] = 0.3
        elif item == "2":
            N[0][1] = -0.3
        elif item == "4":
            N[1][2] = 0.3
        elif item == "5":
            N[1][2] = -0.3
        elif item == "7":
            N[2][0] = 0.3
        elif item == "8":
            N[2][0] = -0.3
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
            degree1 += degree[0]
            degree2 += degree[1]
            
            if degree2 > 45.:
                degree2 = 45.0
            elif degree2 < -20.:
                degree2 = -20.
            count += 1
        M = M @ N
    # Rotation
    th1 = np.radians(degree1)
    th2 = np.radians(degree2)
    K1 = np.identity(4)
    K1[:3,:3] = np.array([[np.cos(th1),0.,np.sin(th1)],
                        [0.,1.,0.],
                        [-np.sin(th1),0.,np.cos(th1)]
                        ])
    K2 = np.identity(4)
    K2[:3,:3] = np.array([[1., 0., 0.],
                        [0.,np.cos(-th2),np.sin(th2)],
                        [0.,-np.sin(th2),np.cos(th2)]
                        ])
    # R = M @ K1 @ K2
    R = K1 @ K2
    M = M @ R
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
    scale = 20.
    for i in range(21):
        glPushMatrix()
        glBegin(GL_LINES)
        glColor3ub(80,80,80)
        glVertex3fv(np.array([-scale+2.*i,0.,scale]))
        glVertex3fv(np.array([-scale+2.*i,0.,-scale]))
        glVertex3fv(np.array([scale,0.,-scale+2.*i]))
        glVertex3fv(np.array([-scale,0.,-scale+2.*i]))
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
    size = np.sqrt(np.dot(u,u))
    if size == 0.:
        return np.identity(3)
    else:
        u /= size
    
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
    if 2.*a*b == 0.:
        return 0.
    else:
        th = np.arccos((a*a + b*b - c*c)/(2.*a*b))
        return th

# Main_Obj = Alien, Obj1 = Cube, Obj2 = Tree, Obj3 = Cylinder
obj1_collision = False
obj1_position = np.array([6.5,0.,-10.])
obj1_count = 0
obj1_degreeM = np.identity(4)
obj1_signal_count = 1
obj1_save_original = np.zeros(3)

obj2_collision = False
obj2_position = np.array([-8.5,0.,6.5])
obj2_count = 0
obj2_degree = 0.
obj2_signal_count = 1
obj2_save_original = np.zeros(3)

obj3_collision = False
obj3_position = np.array([4.,0.,10.])
obj3_count = 0
obj3_matrix = np.identity(4)
obj3_signal_count = 1
obj3_save_original = np.zeros(3)

def render():
    global main_scale, scale, cameraUp, camera_mode, varr, iarr, obj1_position, obj1_count, obj1_collision, obj1_degreeM, obj1_signal_count, obj2_position, obj2_count, obj2_collision, obj2_degree, obj2_signal_count, obj3_position, obj3_count, obj3_collision, obj3_signal_count, obj3_matrix, obj1_save_original, obj2_save_original, obj3_save_original, trans_stack
    M = main_object_frame()
    main_original = (M @ np.array([0.,0.,0.,1.]))[:3]
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT, GL_FILL)
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # True -> First-person view, False -> Quater view
    if camera_mode:
        gluPerspective(90,1,.1,20)
    else:
        glOrtho(-scale,scale,-scale,scale,-scale,scale)
        
    glMatrixMode(GL_MODELVIEW)
    eye = np.zeros(3)
    at = np.zeros(3)
    glLoadIdentity()
    if camera_mode:
        arr = np.array([0.,1.,0.,1.])
        arr[1] *= main_scale * 4.
        eye = (M @ arr)[:3]
        temp = (M @ np.array([0.,0.,1.,0.]))[:3]
        at = eye + temp
    else:
        eye = np.array([-0.3,0.3,-0.3]) + main_original
        at = main_original
    gluLookAt(eye[0],eye[1],eye[2],at[0],at[1],at[2],cameraUp[0],cameraUp[1],cameraUp[2])
    
    drawframe()
    drawgrid()
    
    # Light setting
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_LIGHT2)
    glEnable(GL_NORMALIZE)
    
    lightPos0 = (0., 12., -12., 1.)
    lightPos1 = (-12., 12., -12., 1.)
    lightPos2 = (-12., 12., 0., 1.)
    glLightfv(GL_LIGHT0,GL_POSITION,lightPos0)
    glLightfv(GL_LIGHT1,GL_POSITION,lightPos1)
    glLightfv(GL_LIGHT2,GL_POSITION,lightPos2)
    
    lightColor1 = (.45, .45, .45, .45)
    lightColor2 = (.3, .3, .3, .3)
    ambientLightColor = (.1,.1,.1,1.)
    glLightfv(GL_LIGHT0,GL_DIFFUSE,lightColor1)
    glLightfv(GL_LIGHT0,GL_SPECULAR,lightColor1)
    glLightfv(GL_LIGHT0,GL_AMBIENT,ambientLightColor)
    glLightfv(GL_LIGHT1,GL_DIFFUSE,lightColor2)
    glLightfv(GL_LIGHT1,GL_SPECULAR,lightColor2)
    glLightfv(GL_LIGHT1,GL_AMBIENT,ambientLightColor)
    glLightfv(GL_LIGHT2,GL_DIFFUSE,lightColor1)
    glLightfv(GL_LIGHT2,GL_SPECULAR,lightColor1)
    glLightfv(GL_LIGHT2,GL_AMBIENT,ambientLightColor)
    
    # Main object
    glPushMatrix()
    objectColor = (.3, .3, .7, 1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT,GL_AMBIENT_AND_DIFFUSE,objectColor)
    glMaterialfv(GL_FRONT,GL_SHININESS,10)
    glMaterialfv(GL_FRONT,GL_SPECULAR,specularObjectColor)
    glMultMatrixf(M.T)
    glScalef(main_scale,main_scale,main_scale)
    drawObject_glDrawElements(varr[0],iarr[0])
    glPopMatrix()
    
    # Collision condition
    if distance(main_original, obj1_position) <= 4.3:
        obj1_collision = True
        if obj1_signal_count == 1:
            obj1_signal_count -= 1
            obj1_count = 0
            obj1_save_original = main_original
    
    if distance(main_original, obj2_position) <= 4.3:
        obj2_collision = True
        if obj2_signal_count == 1:
            obj2_signal_count -= 1
            obj2_count = 0
            obj2_save_original = main_original
    
    if distance(main_original, obj3_position) <= 4.3:
        obj3_collision = True
        if obj3_signal_count == 1:
            obj3_signal_count -= 1
            obj3_count = 0
            obj3_save_original = main_original
    
    # Object1
    glPushMatrix()
    objectColor = (.7, .3, .3, 1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT,GL_AMBIENT_AND_DIFFUSE,objectColor)
    glMaterialfv(GL_FRONT,GL_SHININESS,10)
    glMaterialfv(GL_FRONT,GL_SPECULAR,specularObjectColor)
    if obj1_collision:
        R = np.identity(4)
        v = obj1_position - obj1_save_original
        t = 0.01 * obj1_count
        # Pushed away
        obj1_position += v * 0.015
        # Spin 120 degrees on y-axis
        R1 = np.identity(3)
        th = np.radians(120)
        R2 = np.array([[np.cos(th), 0., np.sin(th)],
                        [0.,1.,0.],
                       [-np.sin(th),0.,np.cos(th)]
                       ])
        R[:3,:3] = slerp(R1,R2,t)
        glTranslatef(obj1_position[0],obj1_position[1],obj1_position[2])
        glMultMatrixf(R.T)
        obj1_count += 1
        if obj1_count == 100:
            obj1_collision = False
            obj1_degreeM = obj1_degreeM @ R
            obj1_signal_count += 1
    else:
        glTranslatef(obj1_position[0],obj1_position[1],obj1_position[2])
        glMultMatrixf(obj1_degreeM.T)
    drawObject_glDrawElements(varr[1],iarr[1])
    glPopMatrix()
    
    # Object2
    glPushMatrix()
    objectColor = (.2, .7, .2, 1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT,GL_AMBIENT_AND_DIFFUSE,objectColor)
    glMaterialfv(GL_FRONT,GL_SHININESS,10)
    glMaterialfv(GL_FRONT,GL_SPECULAR,specularObjectColor)
    glTranslatef(obj2_position[0],obj2_position[1],obj2_position[2])
    glRotatef(obj2_degree,0,1,0)
    if obj2_collision:
        R = np.identity(4)
        # Spin to collision orientation
        if obj2_count <= 10:
            i = obj2_count
            t = 0.1 * i
            v = -obj2_position + obj2_save_original
            degree = -np.rad2deg(get_th(v))
            R1 = np.identity(3)
            th = np.radians(degree)
            R2 = np.array([[np.cos(th),0.,np.sin(th)],
                           [0.,1.,0.],
                           [-np.sin(th),0.,np.cos(th)]
                           ])
            R[:3,:3] = slerp(R1,R2,t)
            glMultMatrixf(R.T)
            obj2_count += 1
            if obj2_count == 10:
                obj2_degree += degree
        # Spin 90 degrees on z-axis
        elif obj2_count > 10 and obj2_count <= 60:
            i = obj2_count - 10
            t = 0.02 * i
            R1 = np.identity(3)
            th = np.radians(90)
            R2 = np.array([[np.cos(th),-np.sin(th),0.],
                           [np.sin(th),np.cos(th),0.],
                           [0.,0.,1.]
                           ])
            R[:3,:3] = slerp(R1,R2,t)
            glMultMatrixf(R.T)
            obj2_count += 1
        # Spin -180 degrees on z-axis
        elif obj2_count > 60 and obj2_count <= 160:
            i = obj2_count - 60
            t = 0.01 * i
            th = np.radians(90)
            R1 = np.array([[np.cos(th),-np.sin(th),0.],
                           [np.sin(th),np.cos(th),0.],
                           [0.,0.,1.]
                           ])
            th2 = np.radians(-90)
            R2 = np.array([[np.cos(th2),-np.sin(th2),0.],
                           [np.sin(th2),np.cos(th2),0.],
                           [0.,0.,1.]
                           ])
            R[:3,:3] = slerp(R1,R2,t)
            glMultMatrixf(R.T)
            obj2_count += 1
        # Spin 90 degrees on z-axis
        elif obj2_count > 160:
            i = obj2_count - 160
            t = 0.01 * i
            th = np.radians(-90)
            R1 = np.array([[np.cos(th),-np.sin(th),0.],
                           [np.sin(th),np.cos(th),0.],
                           [0.,0.,1.]
                           ])
            R2 = np.identity(3)
            R[:3,:3] = slerp(R1,R2,t)
            glMultMatrixf(R.T)
            obj2_count += 1
            if obj2_count == 260:
                obj2_collision = False
                obj2_signal_count += 1
    glScalef(1.2,1.2,1.2)
    drawObject_glDrawElements(varr[2],iarr[2])
    glPopMatrix()
    
    # Object3
    glPushMatrix()
    objectColor = (.1, .5, .5, 1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT,GL_AMBIENT_AND_DIFFUSE,objectColor)
    glMaterialfv(GL_FRONT,GL_SHININESS,10)
    glMaterialfv(GL_FRONT,GL_SPECULAR,specularObjectColor)
    if obj3_collision:
        R = np.identity(4)
        v = -obj3_position + obj3_save_original
        degree = -np.rad2deg(get_th(v))
        # Pushed away
        obj3_position -= v * 0.01
        glTranslatef(obj3_position[0],obj3_position[1],obj3_position[2])
        
        glRotatef(degree,0,1,0)
        t = 0.02 * obj3_count
        # Sheard
        R[0][1] = 0.5 * t
        glMultMatrixf(R.T)
        
        obj3_count += 1
        if obj3_count == 50:
            obj3_collision = False
            obj3_signal_count += 1
            th = np.radians(degree)
            K = np.identity(4)
            K[:3,:3] = np.array([[np.cos(th),0.,np.sin(th)],
                           [0.,1.,0.],
                           [-np.sin(th),0.,np.cos(th)]
                           ])
            obj3_matrix = obj3_matrix @ K @ R
    else:
        glTranslatef(obj3_position[0],obj3_position[1],obj3_position[2])
        glMultMatrixf(obj3_matrix.T)
    glScalef(1.5,1.5,1.5)
    drawObject_glDrawElements(varr[3],iarr[3])
    glPopMatrix()
    
    glDisable(GL_LIGHTING)
    
def distance(arr1,arr2):
    return np.sqrt(np.dot(arr2-arr1,arr2-arr1))

def l2norm(v):
    return np.sqrt(np.dot(v, v))
    
def normalized(v):
    l = l2norm(v)
    if l == 0.:
        return np.array(v)
    else:
        return (1/l) * np.array(v)

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
    if a != 0.:
        v1 = (R[2][1]-R[1][2])/(2*np.sin(a))
        v2 = (R[0][2]-R[2][0])/(2*np.sin(a))
        v3 = (R[1][0]-R[0][1])/(2*np.sin(a))
    else:
        v1 = 0.
        v2 = 0.
        v3 = 0.
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
    global trans,cameraUp, trans_stack, rotation_stack, init_pos
    # Main object rotation
    if Left_pressed:
        degree1 =  0. + (init_pos[0] - xpos) * 0.02
        degree2 =  0. + (init_pos[1] - ypos) * 0.02
        trans_stack.append("ROTATION")
        rotation_stack.append([degree1,degree2])
    
def scroll_callback(window,xoffset,yoffset):
    global scale
    if scale <= 0.1 and yoffset == 1:
        scale = 0.1
        return
    scale -= 0.8 * yoffset


def key_callback(window, key, scancode, action, mods):
    global trans_stack, main_scale
    
    if action==glfw.PRESS or action==glfw.REPEAT:
        if key==glfw.KEY_W:
            trans_stack.append("W")
        elif key==glfw.KEY_S:
            trans_stack.append("S")
        elif key==glfw.KEY_A:
            trans_stack.append("A")
        elif key==glfw.KEY_D:
            trans_stack.append("D")
        # main obj size up
        elif key==glfw.KEY_Z:
            main_scale *= 1.2
        # main obj size down
        elif key==glfw.KEY_X:
            main_scale *= 0.8
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
    
    file_name = []
    relative_path = ''.join(os.getcwd()) + '\OBJ'
    file_name.append(relative_path + '\main.obj')
    file_name.append(relative_path + '\obj1.obj')
    file_name.append(relative_path + '\obj2.obj')
    file_name.append(relative_path + '\obj3.obj')
    
    # object load from file
    # file_name = [relative_path + "\main.obj",relative_path + "\obj1.obj",relative_path + "\obj2.obj"]
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