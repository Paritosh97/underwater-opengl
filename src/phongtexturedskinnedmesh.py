from vertexarray import VertexArray
from mesh import Mesh
import OpenGL.GL as GL
import numpy as np

class PhongTexturedSkinnedMesh(Mesh):
    """class of skinned mesh nodes in scene graph """
    def __init__(self, shader, attributes, bone_nodes, bone_offsets, texture, index=None, light_dir=(0, -1, 0), k_a=(0, 0, 0), k_d=(1, 1, 0), k_s=(1, 1, 1), s=16.):

        super().__init__(shader, attributes, index)

        # store skinning data
        self.bone_nodes = bone_nodes
        self.bone_offsets = bone_offsets

        self.light_dir = light_dir
        self.k_a, self.k_d, self.k_s, self.s = k_a, k_d, k_s, s

        # retrieve OpenGL locations of shader variables at initialization
        names = ['diffuse_map', 'light_dir', 'k_a', 's', 'k_s', 'k_d', 'w_camera_position']

        loc = {n: GL.glGetUniformLocation(shader.glid, n) for n in names}
        self.loc.update(loc)

        # setup texture and upload it to GPU
        self.texture = texture

    
    def draw(self, projection, view, _model):
        """ skinning object draw method """

        shid = self.shader.glid
        GL.glUseProgram(shid)

        # texture access setups
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture.glid)
        GL.glUniform1i(self.loc['diffuse_map'], 0)

        # setup light parameters
        GL.glUniform3fv(self.loc['light_dir'], 1, self.light_dir)

        # setup material parameters
        GL.glUniform3fv(self.loc['k_a'], 1, self.k_a)
        GL.glUniform3fv(self.loc['k_d'], 1, self.k_d)
        GL.glUniform3fv(self.loc['k_s'], 1, self.k_s)
        GL.glUniform1f(self.loc['s'], max(self.s, 0.001))

        # world camera position for Phong illumination specular component
        w_camera_position = np.linalg.inv(view)[:,3]
        GL.glUniform3fv(self.loc['w_camera_position'], 1, w_camera_position)

        # setup camera geometry parameters
        loc = GL.glGetUniformLocation(shid, 'projection')
        GL.glUniformMatrix4fv(loc, 1, True, projection)
        loc = GL.glGetUniformLocation(shid, 'view')
        GL.glUniformMatrix4fv(loc, 1, True, view)

        # bone world transform matrices need to be passed for skinning
        for bone_id, node in enumerate(self.bone_nodes):
            bone_matrix = node.world_transform @ self.bone_offsets[bone_id]

            bone_loc = GL.glGetUniformLocation(shid, 'boneMatrix[%d]' % bone_id)
            GL.glUniformMatrix4fv(bone_loc, 1, True, bone_matrix)

        # draw mesh vertex array
        self.vertex_array.execute(GL.GL_TRIANGLES)

        # leave with clean OpenGL state, to make it easier to detect problems
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glUseProgram(0)
