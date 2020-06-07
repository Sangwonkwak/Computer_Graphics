import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import copy 

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
full_list = []
START_FLAG = False
ENABLE_FLAG = False
tree = []
motion_start = 0 
sum_channel = 0
cur_index = 0
count = 0
Frames = 0

class Node:
    def __init__(self,name):
        self.name = name
        self.offset = np.zeros(3)
        self.tree_index = -1
        self.channel_count = 0
        self.channel = []
        self.child = []
        self.parent_index = -1

def print_data():
    global tree, full_list, motion_start, Frames
    
    frame_time = float(full_list[motion_start+2].split(' ')[2])
    FPS = int(1/frame_time)
    print("Number of frames: %d\nFPS: %d"%(Frames,FPS))
    
    joint_num = 0
    print("List of all joint names: ",end='')
    for i in tree:
        if i.name != "__END__":
            joint_num += 1
            print(i.name, end=' ')
    print("\nNumber of joints: %d"%(joint_num))
       

# Make tree structure for parsing hierarchical model
def make_tree():
    global full_list, tree, motion_start, sum_channel, cur_index, Frames
    tree = []
    motion_start = 0
    i = 0
    sum_channel = 0
    pre_index = -1
    while True:
        temp = full_list[i].lstrip().split(' ')
        if temp[0] == "JOINT" or temp[0] == "ROOT":
            temp_Node = Node(temp[1])
            tree.append(temp_Node)
            # parent, child add
            if temp[0] == "JOINT":
                tree[pre_index].child.append(temp_Node)
                temp_Node.parent_index = pre_index
            
            # offset
            temp1 = full_list[i+2].lstrip().split(' ')
            temp_Node.offset = np.array([float(temp1[1]),float(temp1[2]),float(temp1[3])])
            
            # channel
            temp2 = full_list[i+3].lstrip().split(' ')
            temp_Node.channel_count = int(temp2[1])
            sum_channel += temp_Node.channel_count
            # 기본적으로 x,y,z position channel이 root에 있다고 가정
            if temp2[0] == "ROOT":
                temp_Node.channel_count -= 3
            for j in range(temp_Node.channel_count):
                if(temp2[0] == "ROOT"):
                    j += 3
                if temp2[2+j] == "XROTATION":
                    temp_Node.channel.append("XROT")
                elif temp2[2+j] == "YROTATION":
                    temp_Node.channel.append("YROT")
                elif temp2[2+j] == "ZROTATION":
                    temp_Node.channel.append("ZROT")
                # elif temp[2+j] == "XPOSITION":
                #     temp_Node.channel.append("XPOS")
                # elif temp[2+j] == "YPOSITION":
                #     temp_Node.channel.append("YPOS")
                # elif temp[2+j] == "ZPOSITION":
                #     temp_Node.channel.append("ZPOS")
            # tree index
            pre_index = len(tree) - 1
            temp_Node.tree_index = pre_index
            i += 4
        elif temp[0] == "End":
            temp_Node = Node("__END__")
            tree.append(temp_Node)
            tree[pre_index].child.append(temp_Node)
            temp_Node.parent_index = pre_index
            # offset
            temp1 = full_list[i+2].lstrip().split(' ')
            temp_Node.offset = np.array([float(temp1[1]),float(temp1[2]),float(temp1[3])])
            # tree index
            pre_index = len(tree) - 1
            temp_Node.tree_index = pre_index
            i += 3
        elif temp[0] == '}\n':
            pre_index = tree[pre_index].parent_index
            i += 1
        elif temp[0] == "MOTION\n":
            motion_start = i
            break
        else:
            i += 1
    cur_index = motion_start + 3
    Frames = int(full_list[motion_start+1].split(' ')[1])


motion_index = 0
def draw_Model(node,motion_data):
    global motion_index
    # End site
    glPushMatrix()
    M = np.identity(4)
    if node.channel_count == 0:
        glBegin(GL_LINES)
        glVertex3fv(np.array([0.,0.,0.]))
        M[:-1,3] = [node.offset[0], node.offset[1], node.offset[2]]
        glVertex3fv((M @ np.array([0.,0.,0.,1.]))[:-1])
        glEnd()
    # joint & root
    else:
        # root
        if node.tree_index == 0:
            glTranslatef(motion_data[0],motion_data[1],motion_data[2])
            motion_index = 3
        glBegin(GL_LINES)
        glVertex3fv(np.array([0.,0.,0.]))
        M[:-1,3] = [node.offset[0], node.offset[1], node.offset[2]]
        
        for i in node.channel:
            R = np.identity(4)
            th = np.radians(motion_data[motion_index])
            if i == "XROT":
                R[:3,:3] = [[1., 0., 0.],
                            [0., np.cos(th), -np.sin(th)],
                            [0., np.sin(th), np.cos(th)]
                            ]
            elif i == "YROT":
                R[:3,:3] = [[np.cos(th), 0., np.sin(th)],
                            [0., 1., 0.],
                            [-np.sin(th), 0., np.cos(th)]
                            ]
            elif i == "ZROT":
                R[:3,:3] = [[np.cos(th), -np.sin(th), 0.],
                            [np.sin(th), np.cos(th), 0.],
                            [0., 0., 1.]
                            ]
            M = M @ R
            motion_index += 1
        glVertex3fv((M @ np.array([0.,0.,0.,1.]))[:-1])
        glEnd()
        glMultMatrixf(M.T)
    
        for child in node.child:
            draw_Model(child,motion_data)
    glPopMatrix()

def render():
    global full_list, START_FLAG, ENABLE_FLAG, motion_start, tree, sum_channel, cur_index, motion_index, Frames, count
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
    motion_data = []
    if ENABLE_FLAG: 
        if START_FLAG:
            if count == Frames:
                cur_index = motion_start + 3
                count = 0
            motion_data = full_list[cur_index].split(' ')
            if len(motion_data) == 1:
                motion_data = full_list[cur_index].split('\t')
            for i in range(sum_channel):
                motion_data[i] = float(motion_data[i])
            cur_index += 1
            count += 1
        else:
            motion_data = np.zeros(sum_channel)
        glColor3ub(0,0,200)
        glScalef(.3,.3,.3)
        motion_index = 0
        draw_Model(tree[0], motion_data)

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

def drawframe():
    glBegin(GL_LINES)
    glColor3ub(255,0,0)
    glVertex3fv(np.array([-.1,0.,0.]))
    glVertex3fv(np.array([.1,0.,0.]))
    glColor3ub(0,255,0)
    glVertex3fv(np.array([0.,-.1,0.]))
    glVertex3fv(np.array([0.,.1,0.]))
    glColor3ub(0,0,255)
    glVertex3fv(np.array([0.,0.,-.1]))
    glVertex3fv(np.array([0.,0.,.1]))
    glEnd()

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

def drop_callback(window,paths):
    global full_list, ENABLE_FLAG, START_FLAG
    
    START_FLAG = False
    ENABLE_FLAG = True
    file_name = ''.join(paths)
    file = open(file_name,'r')
    full_list = file.readlines()
    make_tree()
    print("File name: %s"%(file_name))
    print_data()
    print("###########################################################")
    file.close()

def key_callback(window, key, scancode, action, mods):
    global START_FLAG
    if action==glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_SPACE:
            START_FLAG = True

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