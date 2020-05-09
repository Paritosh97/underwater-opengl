# Original viewer

#!/usr/bin/env python3
"""
Underwater scene in OpenGL
"""
# Python built-in modules
import os                           # os function, i.e. checking file status
import glob
# External, non built-in modules
from glfw import init, terminate
import numpy as np                  # all matrix manipulations & OpenGL args
import assimpcy                     # 3D resource loader

from transform import translate, scale, vec, quaternion, quaternion_from_euler

# import Shader
from shader import Shader

# import VertexArray
from vertexarray import VertexArray

# import Node
from node import Node

# import Mesh
from mesh import Mesh

# import texture
from texture import Texture

# import texturedmesh
from texturedmesh import TexturedMesh

# import KeyframeControlNode
from keyframecontrolnode import KeyFrameControlNode

# import SkinnedMesh
from skinnedmesh import SkinnedMesh

# import SkinnedControlNode
from skinningcontrolnode import SkinningControlNode

# import Skybox
from skybox import Skybox

# import viewer
from viewer import Viewer

from model import load_textured, load, load_phong_mesh

# -------------- main program and scene setup --------------------------------
def main():
    """ create a window, add scene objects, then run rendering loop """
    viewer = Viewer()
    
    """
    # Keyframe Animation
    translate_keys = {0: vec(0, 0, 0), 2: vec(1, 1, 0), 4: vec(0, 0, 0)}

    rotate_keys = {0: quaternion(), 2: quaternion_from_euler(180, 45, 90), 3: quaternion_from_euler(180, 0, 180), 4: quaternion()}

    scale_keys = {0: 1, 2: 0.5, 4: 1}

    keynode = KeyFrameControlNode(translate_keys, rotate_keys, scale_keys)
    """
    #src = ['./assets/models/fish/Barracuda/Barracuda2anim.fbx']

    #viewer.add(*[m for file in src for m in load_skinned(file, shader)])

    #viewer.add(keynode)

    
    """
    # LOAD MODEL FROM PARAMETER
    viewer.add(*[mesh for file in sys.argv[1:] for mesh in load(file, shader)])
    if len(sys.argv) < 2:
        print('Usage:\n\t%s [3dfile]*\n\n3dfile\t\t the filename of a model in'
              ' format supported by assimp.' % (sys.argv[0],))
    """

    """ 
    #ROBOT ARM MODELING
    
    cylinder = Cylinder(shader)

    axis = Axis(shader)

    # make a flat cylinder
    base_shape = Node(transform=scale(1, 0.2, 1))
    base_shape.add(cylinder)  # shape of robot base

    # make a thin cylinder
    arm_shape = Node(transform=translate(0, 0.8, 0) @ scale(0.1, 1, 0.1))
    arm_shape.add(cylinder)  # shape of arm

    # make a thin cylinder
    forearm_shape = Node(transform=translate(0, 2, 0) @ scale(0.1, 0.1, 0.1))
    forearm_shape.add(cylinder)  # shape of forearm

    # ---- construct our robot arm hierarchy ---------------------------
    theta = 45.0  # base horizontal rotation angle
    phi1 = 45.0  # arm angle
    phi2 = 20.0  # forearm angle

    transform_forearm = Node(transform=translate(0, 0, 0) @ rotate((1, 0, 0), phi2))
    transform_forearm.add(forearm_shape)

    transform_arm = Node(transform=rotate((0, 0, 0), phi1))
    transform_arm.add(arm_shape, transform_forearm)

    transform_base = Node(transform=rotate((0, 0, 0), theta))
    transform_base.add(base_shape, transform_arm)

    viewer.add(transform_base)

    # Textured model
    shader = Shader("./shaders/texture.vert", "./shaders/texture.frag")
    src = ['./../assets/models/fish/LionFish/LionFish.fbx']
    texFile = './../assets/models/fish/LionFish/LionFish_Normal.png'
    viewer.add(*[m for file in src for m in load_textured(file, shader, texFile)])
    """

    
    # set skybox
    environment = Node()
    shader = Shader("./shaders/skybox.vert", "./shaders/skybox.frag")    
    environment.add(Skybox(shader, "./../assets/skybox/underwater/"))

    # set seabed
    shader = Shader("./shaders/texture.vert", "./shaders/texture.frag")
    src = ['./../assets/models/seabed/seabed.fbx']
    texFile = './../assets/models/seabed/seabed.jpg'
    seabed = Node(transform=scale(0.008, 0.01, 0.008) @ translate(0, -100, 0))
    seabed.add(*[m for file in src for m in load_textured(file, shader, texFile)])

    """
    # add plants
    shader = Shader("./shaders/phong.vert", "./shaders/phong.frag")
    src = ['./../assets/models/plants/coral/coral.obj']
    mtlFile = 'assets/models/plants/coral/material.mtl'
    #face_urls = sorted(glob.glob(folder_url + "*"))
    plants = Node(transform=scale(2, 2, 2) @ translate(50, 4.5, 0))
    plants.add(*[m for file in src for m in load_phong_mesh(file, shader, mtlFile)])
    seabed.add(plants)
    """


    # add fish models
    #shader = Shader("./shaders/texture.vert", "./shaders/texture.frag")

    

    environment.add(seabed)
    


    scene = Node()
    scene.add(environment)

    viewer.add(scene)

    # start rendering loop
    viewer.run()


if __name__ == '__main__':
    init()                # initialize window system glfw
    main()                     # main function keeps variables locally scoped
    terminate()           # destroy all glfw windows and GL contexts
