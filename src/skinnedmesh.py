from vertexarray import VertexArray
import OpenGL.GL as GL

class SkinnedMesh:
    """class of skinned mesh nodes in scene graph """
    def __init__(self, shader, attributes, bone_nodes, bone_offsets, index=None):
        self.shader = shader

        # setup shader attributes for linear blend skinning shader
        self.vertex_array = VertexArray(attributes, index)

        # store skinning data
        self.bone_nodes = bone_nodes
        self.bone_offsets = bone_offsets

    def draw(self, projection, view, _model):
        """ skinning object draw method """

        shid = self.shader.glid
        GL.glUseProgram(shid)

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
        GL.glUseProgram(0)
