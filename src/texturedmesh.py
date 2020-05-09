import OpenGL.GL as GL
from mesh import Mesh

class TexturedMesh(Mesh):
    """ Simple first textured object """
    def __init__(self, shader, texture, attributes, index=None):
        super().__init__(shader, attributes, index)

        loc = GL.glGetUniformLocation(shader.glid, 'diffuse_map')
        self.loc['diffuse_map'] = loc
        # setup texture and upload it to GPU
        self.texture = texture

    def draw(self, projection, view, model, primitives=GL.GL_TRIANGLES):
        GL.glUseProgram(self.shader.glid)

        # texture access setups
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture.glid)
        GL.glUniform1i(self.loc['diffuse_map'], 0)
        super().draw(projection, view, model, primitives)

        # leave clean state for easier debugging
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glUseProgram(0)