#Blendshape Freeze Transformation Fix Tool
#Work in Maya 2016
#Ver 1.0
#Fred Qiao
#Carnegie Mellon University, 2018
#zhehaoq@andrew.cmu.edu
#412-799-3762

from scipy.linalg import svd
import numpy as np
import random as rd


def compute_mesh(duplicated_mesh, fixer_sec_window):
    #get chosen vertices
    vtx_num = cmds.polyEvaluate(modified_mesh, v = True)
    vtx_unchanged = cmds.ls(sl = True, fl = True)
    chosen_vtx_indices = rd.sample(vtx_unchanged, 4)
    original_vertices = []
    modified_vertices = []
    for each_vertex in chosen_vtx_indices:
        vtx_str = each_vertex[len(original_mesh):]
        print vtx_str
        original_vertices += [original_mesh+vtx_str]
        modified_vertices += [modified_mesh+vtx_str]
    #set up solving matrix
    A = []
    b = []

    #get trs matrix
    for crt_index in range(0,4):
        original_position = cmds.pointPosition(original_vertices[crt_index], w = True)
        modified_position = cmds.pointPosition(modified_vertices[crt_index], w = True) + [1]
        row_1 = modified_position + [0, 0, 0, 0, 0, 0, 0, 0]
        row_2 = [0, 0, 0, 0] + modified_position + [0, 0, 0, 0]
        row_3 = [0, 0, 0, 0, 0, 0, 0, 0] + modified_position
        A += [row_1, row_2, row_3]
        b += original_position
    H_entries = np.linalg.solve(A, b)
    H = np.array([H_entries[0:4]] + [H_entries[4:8]] + [H_entries[8:12]] + [[0, 0, 0, 1]])
    
    for index in range(vtx_num):
	    crt_vtx = duplicated_mesh+'.vtx['+str(index)+']'
	    vertex_position = cmds.pointPosition(crt_vtx, w = True) + [1]

        	#apply transformation to each vertex
	    vertex_transform = np.dot(H, vertex_position)
	    vertex_transform = vertex_transform/vertex_transform[3]
	    cmds.xform(crt_vtx, t = vertex_transform[0:3], ws = True)

    #freeze transformation of the new mesh
    cmds.makeIdentity(duplicated_mesh, a = True)

    #get the transformation of original mesh
    original_translate = map(lambda x: -x, list(cmds.getAttr(original_mesh+'.translate')[0]))
    original_rotate = map(lambda x: -x, list(cmds.getAttr(original_mesh+'.rotate')[0]))    
    original_scale = map(lambda x: 1/x, list(cmds.getAttr(original_mesh+'.scale')[0]))
    original_rotatePivot = list(cmds.getAttr(original_mesh+'.rotatePivot')[0])
    #original_rotatePivotTranslate = list(cmds.getAttr(original_mesh+'.rotatePivotTranslate')[0])
    original_scalePivot = list(cmds.getAttr(original_mesh+'.scalePivot')[0])

    #apply transformation to duplicated mesh
    cmds.xform(duplicated_mesh, t = original_translate, rp = original_rotatePivot, sp = original_scalePivot, p = True)
    cmds.xform(duplicated_mesh, ro = original_rotate, s = original_scale)
    cmds.makeIdentity(duplicated_mesh, a = True)
    cmds.deleteUI(fixer_sec_window)



    
    

def firstCommand():
    meshes_list = cmds.ls(sl = True)
    base = meshes_list[0]
    target = meshes_list[1]
    cmds.text(base_mesh_text, label = base, edit = True)
    cmds.text(target_mesh_text, label = target, edit = True)
    return [base, target]


def secondCommand():
    cmds.deleteUI(fixer_window)
    #make a copy of modified mesh
    duplicated_mesh = modified_mesh+'dup'
    global duplicated_mesh
    cmds.duplicate(modified_mesh, n = duplicated_mesh)
    cmds.setAttr(duplicated_mesh+".translate", lock = 0)
    cmds.setAttr(duplicated_mesh+".rotate", lock = 0)
    cmds.setAttr(duplicated_mesh+".scale", lock = 0)
    fixer_sec_window = cmds.window(title = window_name, iconName='Short Name', widthHeight=(420, 100), 
                                   minimizeButton = True, sizeable = True, leftEdge = 800)
    global fixer_sec_window
    cmds.columnLayout(p = fixer_window, adj = True, rowSpacing = 5)
    cmds.text(label = "choose random vertices remaining the same position in blendshape", al = "center", fn = "boldLabelFont", height = 50)
    cmds.rowColumnLayout(co = [1, "both", 160])
    cmds.button(label='Confirm', command = ("compute_mesh(duplicated_mesh, fixer_sec_window)"), height = 25, width = 100)
    cmds.showWindow(fixer_sec_window)


window_name = "Blendshape Fixer"

fixer_window = cmds.window(title = window_name, iconName='Short Name', widthHeight=(300, 100), 
                           minimizeButton = True, sizeable = True, leftEdge = 800)

cmds.columnLayout(p = fixer_window, adj = True, rowSpacing = 5)
cmds.text(label = "click base mesh first, then target mesh", al = "center", fn = "boldLabelFont", height = 30)
cmds.rowColumnLayout(co = [1, "both", 100])
cmds.button(label='Yes', command=("[original_mesh, modified_mesh] = firstCommand()"), height = 25, width = 100)
cmds.setParent('..')
cmds.rowColumnLayout(numberOfColumns = 2, columnWidth = [(1, 100), (2, 200)], rowSpacing = [1, 20])
cmds.text(label = "base mesh: ", al = "center", height = 30)
base_mesh_text = cmds.text(label = "", al = "center")
cmds.text(label = "target mesh: ", al = "center", height = 30)
target_mesh_text = cmds.text(label = "", al = "center")
cmds.setParent("..")
cmds.rowColumnLayout(co = [1, "both", 100], rowSpacing = [1, 20])
cmds.button(label='Confirm', command=("secondCommand()"), height = 25, width = 100)
cmds.setParent('..')
cmds.showWindow(fixer_window)