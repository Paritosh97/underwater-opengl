import glob
import numpy as np
import OpenGL.GL as GL
from PIL import Image

class Skybox:

    def __init__(self, shader, folder_url, width=1280, height=720):

        # define width and height
        self.width = width
        self.height = height

        # load skybox shaders
        self.skybox_shaders = shader

        # load skybox cubemap texture
        self.skybox_texture = GL.glGenTextures(1)
        face_order = ["right", "left", "top", "bottom", "back", "front"]
        face_urls = sorted(glob.glob(folder_url + "*"))
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, self.skybox_texture)
        for i, face in enumerate(face_order):
            face_url = [face_url for face_url in face_urls if face in face_url.lower()][0]
            face_surface = np.asarray(Image.open(face_url).convert('RGB'))
            GL.glTexImage2D(GL.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL.GL_RGB, 1024, 1024, 0, GL.GL_RGB, GL.GL_UNSIGNED_BYTE, face_surface)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_R, GL.GL_CLAMP_TO_EDGE)
        GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, 0)

        # define skybox vertices
        skybox_right = [1, -1, -1, 1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1, 1, -1, -1]
        skybox_left = [-1, -1, 1, -1, -1, -1, -1, 1, -1, -1, 1, -1, -1, 1, 1, -1, -1, 1]
        skybox_top = [-1, 1, -1, 1, 1, -1, 1, 1, 1, 1, 1, 1, -1, 1, 1, -1, 1, -1]
        skybox_bottom = [-1, -1, -1, -1, -1, 1, 1, -1, -1, 1, -1, -1, -1, -1, 1, 1, -1, 1]
        skybox_back = [-1, 1, -1, -1, -1, -1, 1, -1, -1, 1, -1, -1, 1, 1, -1, -1, 1, -1]
        skybox_front = [-1, -1, 1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1, 1, -1, -1, 1]

        skybox_vertices = np.array([skybox_right, skybox_left, skybox_top, skybox_bottom, skybox_back, skybox_front], dtype=np.float32).flatten()

        # create vertex array object, bind it
        self.glid = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.glid)

        # create new vbo
        self.skybox_vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.skybox_vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, skybox_vertices.nbytes, skybox_vertices, GL.GL_STATIC_DRAW)
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, 0, None)
        GL.glBindVertexArray(self.glid)

        # Get Uniform location of shader program
        names = ['view', 'projection', 'model']
        self.loc = {n: GL.glGetUniformLocation(self.skybox_shaders.glid, n) for n in names}
    
    def draw(self, projection, view, model):

        # change depth functions 
        GL.glDepthFunc(GL.GL_LEQUAL)

        GL.glUseProgram(self.skybox_shaders.glid)

        GL.glUniformMatrix4fv(self.loc['view'], 1, True, view)
        GL.glUniformMatrix4fv(self.loc['projection'], 1, True, projection)
        GL.glUniformMatrix4fv(self.loc['model'], 1, True, model)

        # skybox cube
        GL.glBindVertexArray(self.glid)
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glUniform1i(GL.glGetUniformLocation(self.skybox_shaders.glid, "skybox"), 0)
        GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, self.skybox_texture)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 36)
        GL.glBindVertexArray(0)
        GL.glDepthFunc(GL.GL_LESS)