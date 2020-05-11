# Original viewer

#!/usr/bin/env python3
"""
Underwater scene in OpenGL
"""
# Python built-in modules
import os                           # os function, i.e. checking file status
import glob
from random import randrange, randint
# External, non built-in modules
from glfw import init, terminate
import numpy as np                  # all matrix manipulations & OpenGL args
import assimpcy                     # 3D resource loader

from transform import translate, scale, rotate, vec, quaternion, quaternion_from_euler

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

from model import Model

from fishanimation import FishAnimation

from particles import Particles

# -------------- main program and scene setup --------------------------------
def main():
    """ create a window, add scene objects, then run rendering loop """
    viewer = Viewer()
    
    # environment node
    environment = Node()

    
    # set skybox
    shader = Shader("./shaders/skybox.vert", "./shaders/skybox.frag")    
    environment.add(Skybox(shader, "./../assets/skybox/underwater/"))
    
    
    # set seabed
    shader = Shader("./shaders/texture.vert", "./shaders/texture.frag")
    src = './../assets/models/seabed/seabed.fbx'
    texFile = './../assets/models/seabed/seabed.jpg'
    seabed = Node(transform=scale(0.008, 0.01, 0.008) @ translate(0, -100, 0))
    model = Model(src, shader)
    for m in model.load_textured(texFile):
        seabed.add(m)
    
    # plants node
    plants = Node()
    
    # add seaweed
    shader = Shader("./shaders/texture.vert", "./shaders/texture.frag")
    src = './../assets/models/plants/seaweed/seaweed.fbx'
    texFile = './../assets/models/plants/seaweed/seaweed.png'    
    seaweed = Node(transform=scale(2, 2, 2))
    seaweed_density = 40
    for i in range(seaweed_density):
        model = Model(src, shader)
        temp = Node(transform=translate(randrange(-50, 50), 3.5, randrange(-50, 50)))

        temp2 = Node(transform=translate(randrange(-20, 20), 15, randrange(-20, 0)))      

        for m in model.load_textured(texFile):            
            temp.add(m)
            if(i%2 == 0):
                temp2.add(m)
        
        seaweed.add(temp)
        if(i%2 == 0):
                seaweed.add(temp2)
        
    plants.add(seaweed)

    # add coral
    src = './../assets/models/plants/coral/coral.obj'
    
    texFile = './../assets/models/plants/coral/coral.jpg'
    coral = Node(transform=scale(0.1, 0.1, 0.1))
    coral_count = 5
    for i in range(coral_count):
        model = Model(src, shader)
        temp = Node(transform=translate(randrange(-300, 300), 350, randrange(-300, -100)))

        for m in model.load_textured(texFile):            
            temp.add(m)
        
        coral.add(temp)
    
    plants.add(coral)
    
    seabed.add(plants)
    
    environment.add(seabed)
    
    # add fish models
    shader = Shader("./shaders/phong_texture_skinning.vert", "./shaders/phong_texture_skinning.frag")        

    fishes = []
    fish_count = 20
    
    for i in range(0, fish_count):
        model = Model(src, shader)
        fish_no = randint(1, 24)
        src = './../assets/models/fish/%d/model.fbx' % fish_no
        texFile = './../assets/models/fish/%d/texture.png' % fish_no
        fish = Node(transform=scale(0.0001, 0.0001, 0.0001))
        for m in model.load_phong_textured_skinned(texFile):
            fish.add(m)
        fishanimation = FishAnimation()
        animated_node = KeyFrameControlNode(fishanimation.get_translate_keys(), fishanimation.get_rotate_keys(), {0: 1, 2: 1, 4: 1}, loop=True)
        animated_node.add(fish)
        fishes.append(animated_node)
    
    for fish in fishes:
        environment.add(fish)
    

    # add bubbles
    shader = Shader("./shaders/particle.vert", "./shaders/particle.frag")  
    

    # add water
    
    scene = Node()
    scene.add(environment)

    viewer.add(scene)

    # start rendering loop
    viewer.run()


if __name__ == '__main__':
    init()                # initialize window system glfw
    main()                     # main function keeps variables locally scoped
    terminate()           # destroy all glfw windows and GL contexts
