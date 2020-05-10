import os
import numpy as np
import assimpcy
from skinnedmesh import SkinnedMesh
from skinningcontrolnode import SkinningControlNode
from texturedmesh import TexturedMesh
from texture import Texture
from mesh import Mesh
from phongmesh import PhongMesh
from phongtexturedskinnedmesh import PhongTexturedSkinnedMesh

MAX_VERTEX_BONES = 4
MAX_BONES = 128

class Model:
    def __init__(self, file, shader):
        self.file = file
        self.shader = shader

        try:
            pp = assimpcy.aiPostProcessSteps
            flags = pp.aiProcess_Triangulate | pp.aiProcess_GenSmoothNormals
            self.scene = assimpcy.aiImportFile(file, flags)
        except assimpcy.all.AssimpError as exception:
            print('ERROR loading', file + ': ', exception.args[0].decode())
            exit()
    
    def load(self):

        meshes = [Mesh(self.shader, [m.mVertices, m.mNormals], m.mFaces)
                for m in self.scene.mMeshes]
        size = sum((mesh.mNumFaces for mesh in self.scene.mMeshes))
        print('Loaded %s\t(%d meshes, %d faces)' % (self.file, len(meshes), size))
        return meshes


    def load_phong(self, light_dir):

        # prepare mesh nodes
        meshes = []
        for mesh in self.scene.mMeshes:
            mat = self.scene.mMaterials[mesh.mMaterialIndex].properties
            mesh = PhongMesh(self. shader, [mesh.mVertices, mesh.mNormals], mesh.mFaces, k_d=mat.get('COLOR_DIFFUSE', (1, 1, 1)), k_s=mat.get('COLOR_SPECULAR', (1, 1, 1)), k_a=mat.get('COLOR_AMBIENT', (0, 0, 0)), s=mat.get('SHININESS', 16.), light_dir=light_dir)
            meshes.append(mesh)

        size = sum((mesh.mNumFaces for mesh in self.scene.mMeshes))
        print('Loaded %s\t(%d meshes, %d faces)' % (self.file, len(meshes), size))
        return meshes

    def load_textured(self, tex_file=None):
    
        # Note: embedded textures not supported at the moment
        path = os.path.dirname(self.file) if os.path.dirname(self.file) != '' else './'
        for mat in self.scene.mMaterials:
            if not tex_file and 'TEXTURE_BASE' in mat.properties:  # texture token
                name = os.path.basename(mat.properties['TEXTURE_BASE'])
                # search texture in file's whole subdir since path often screwed up
                paths = os.walk(path, followlinks=True)
                found = [os.path.join(d, f) for d, _, n in paths for f in n
                        if name.startswith(f) or f.startswith(name)]
                assert found, 'Cannot find texture %s in %s subtree' % (name, path)
                tex_file = found[0]
            if tex_file:
                mat.properties['diffuse_map'] = Texture(tex_file=tex_file)

        # prepare textured mesh
        meshes = []
        for mesh in self.scene.mMeshes:
            mat = self.scene.mMaterials[mesh.mMaterialIndex].properties
            assert mat['diffuse_map'], "Trying to map using a textureless material"
            attributes = [mesh.mVertices, mesh.mTextureCoords[0]]
            mesh = TexturedMesh(self.shader, mat['diffuse_map'], attributes, mesh.mFaces)
            meshes.append(mesh)

        size = sum((mesh.mNumFaces for mesh in self.scene.mMeshes))
        print('Loaded %s\t(%d meshes, %d faces)' % (self.file, len(meshes), size))
        return meshes


    def load_skinned(self):
    
        # ----- load animations
        def conv(assimp_keys, ticks_per_second):
            """ Conversion from assimp key struct to our dict representation """
            return {key.mTime / ticks_per_second: key.mValue for key in assimp_keys}

        # load first animation in scene file (could be a loop over all animations)
        transform_keyframes = {}
        if self.scene.mAnimations:
            anim = self.scene.mAnimations[0]
            for channel in anim.mChannels:
                # for each animation bone, store TRS dict with {times: transforms}
                transform_keyframes[channel.mNodeName] = (
                    conv(channel.mPositionKeys, anim.mTicksPerSecond),
                    conv(channel.mRotationKeys, anim.mTicksPerSecond),
                    conv(channel.mScalingKeys, anim.mTicksPerSecond)
                )

        # ---- prepare scene graph nodes
        # create SkinningControlNode for each assimp node.
        # node creation needs to happen first as SkinnedMeshes store an array of
        # these nodes that represent their bone transforms
        nodes = {}                                       # nodes name -> node lookup
        nodes_per_mesh_id = [[] for _ in self.scene.mMeshes]  # nodes holding a mesh_id

        def make_nodes(assimp_node):
            """ Recursively builds nodes for our graph, matching assimp nodes """
            trs_keyframes = transform_keyframes.get(assimp_node.mName, (None,))
            skin_node = SkinningControlNode(*trs_keyframes,
                                            transform=assimp_node.mTransformation)
            nodes[assimp_node.mName] = skin_node
            for mesh_index in assimp_node.mMeshes:
                nodes_per_mesh_id[mesh_index].append(skin_node)
            skin_node.add(*(make_nodes(child) for child in assimp_node.mChildren))
            return skin_node

        root_node = make_nodes(self.scene.mRootNode)

        # ---- create SkinnedMesh objects
        for mesh_id, mesh in enumerate(self.scene.mMeshes):
            # -- skinned mesh: weights given per bone => convert per vertex for GPU
            # first, populate an array with MAX_BONES entries per vertex
            v_bone = np.array([[(0, 0)]*MAX_BONES] * mesh.mNumVertices,
                            dtype=[('weight', 'f4'), ('id', 'u4')])
            for bone_id, bone in enumerate(mesh.mBones[:MAX_BONES]):
                for entry in bone.mWeights:  # weight,id pairs necessary for sorting
                    v_bone[entry.mVertexId][bone_id] = (entry.mWeight, bone_id)

            v_bone.sort(order='weight')             # sort rows, high weights last
            v_bone = v_bone[:, -MAX_VERTEX_BONES:]  # limit bone size, keep highest

            # prepare bone lookup array & offset matrix, indexed by bone index (id)
            bone_nodes = [nodes[bone.mName] for bone in mesh.mBones]
            bone_offsets = [bone.mOffsetMatrix for bone in mesh.mBones]

            # initialize skinned mesh and store in assimp mesh for node addition
            attrib = [mesh.mVertices, mesh.mNormals, v_bone['id'], v_bone['weight']]
            mesh = SkinnedMesh(self.shader, attrib, bone_nodes, bone_offsets,
                            mesh.mFaces)
            for node in nodes_per_mesh_id[mesh_id]:
                node.add(mesh)

        nb_triangles = sum((mesh.mNumFaces for mesh in self.scene.mMeshes))
        print('Loaded', self.file, '\t(%d meshes, %d faces, %d nodes, %d animations)' %
            (self.scene.mNumMeshes, nb_triangles, len(nodes), self.scene.mNumAnimations))
        return [root_node]


    def load_phong_textured_skinned(self, tex_file=None, light_dir=None):

        # Note: embedded textures not supported at the moment
        path = os.path.dirname(self.file) if os.path.dirname(self.file) != '' else './'
        for mat in self.scene.mMaterials:
            if not tex_file and 'TEXTURE_BASE' in mat.properties:  # texture token
                name = os.path.basename(mat.properties['TEXTURE_BASE'])
                # search texture in file's whole subdir since path often screwed up
                paths = os.walk(path, followlinks=True)
                found = [os.path.join(d, f) for d, _, n in paths for f in n
                        if name.startswith(f) or f.startswith(name)]
                assert found, 'Cannot find texture %s in %s subtree' % (name, path)
                tex_file = found[0]
            if tex_file:
                mat.properties['diffuse_map'] = Texture(tex_file=tex_file)


        # ----- load animations
        def conv(assimp_keys, ticks_per_second):
            """ Conversion from assimp key struct to our dict representation """
            return {key.mTime / ticks_per_second: key.mValue for key in assimp_keys}

        # load first animation in scene file (could be a loop over all animations)
        transform_keyframes = {}
        if self.scene.mAnimations:
            anim = self.scene.mAnimations[0]
            for channel in anim.mChannels:
                # for each animation bone, store TRS dict with {times: transforms}
                transform_keyframes[channel.mNodeName] = (
                    conv(channel.mPositionKeys, anim.mTicksPerSecond),
                    conv(channel.mRotationKeys, anim.mTicksPerSecond),
                    conv(channel.mScalingKeys, anim.mTicksPerSecond)
                )

        # ---- prepare scene graph nodes
        # create SkinningControlNode for each assimp node.
        # node creation needs to happen first as SkinnedMeshes store an array of
        # these nodes that represent their bone transforms
        nodes = {}                                       # nodes name -> node lookup
        nodes_per_mesh_id = [[] for _ in self.scene.mMeshes]  # nodes holding a mesh_id

        def make_nodes(assimp_node):
            """ Recursively builds nodes for our graph, matching assimp nodes """
            trs_keyframes = transform_keyframes.get(assimp_node.mName, (None,))
            skin_node = SkinningControlNode(*trs_keyframes,
                                            transform=assimp_node.mTransformation)
            nodes[assimp_node.mName] = skin_node
            for mesh_index in assimp_node.mMeshes:
                nodes_per_mesh_id[mesh_index].append(skin_node)
            skin_node.add(*(make_nodes(child) for child in assimp_node.mChildren))
            return skin_node

        root_node = make_nodes(self.scene.mRootNode)

        # ---- create SkinnedMesh objects
        for mesh_id, mesh in enumerate(self.scene.mMeshes):
            # -- skinned mesh: weights given per bone => convert per vertex for GPU
            # first, populate an array with MAX_BONES entries per vertex
            v_bone = np.array([[(0, 0)]*MAX_BONES] * mesh.mNumVertices,
                            dtype=[('weight', 'f4'), ('id', 'u4')])
            for bone_id, bone in enumerate(mesh.mBones[:MAX_BONES]):
                for entry in bone.mWeights:  # weight,id pairs necessary for sorting
                    v_bone[entry.mVertexId][bone_id] = (entry.mWeight, bone_id)

            v_bone.sort(order='weight')             # sort rows, high weights last
            v_bone = v_bone[:, -MAX_VERTEX_BONES:]  # limit bone size, keep highest

            # prepare bone lookup array & offset matrix, indexed by bone index (id)
            bone_nodes = [nodes[bone.mName] for bone in mesh.mBones]
            bone_offsets = [bone.mOffsetMatrix for bone in mesh.mBones]

            # Texture 
            mat = self.scene.mMaterials[mesh.mMaterialIndex].properties
            assert mat['diffuse_map'], "Trying to map using a textureless material"

            # initialize skinned mesh and store in assimp mesh for node addition
            attrib = [mesh.mVertices, mesh.mNormals, v_bone['id'], v_bone['weight'], mesh.mTextureCoords[0]]
            mesh = PhongTexturedSkinnedMesh(self.shader, attrib, bone_nodes, bone_offsets, mat['diffuse_map'], mesh.mFaces)

            for node in nodes_per_mesh_id[mesh_id]:
                node.add(mesh)

        nb_triangles = sum((mesh.mNumFaces for mesh in self.scene.mMeshes))
        print('Loaded', self.file, '\t(%d meshes, %d faces, %d nodes, %d animations)' % (self.scene.mNumMeshes, nb_triangles, len(nodes), self.scene.mNumAnimations))

        return [root_node]


# -------------- 3D resource loader -----------------------------------------
def load_phong_mesh(file, shader, light_dir):
    """ load resources from file using assimp, return list of ColorMesh """
    try:
        pp = assimpcy.aiPostProcessSteps
        flags = pp.aiProcess_Triangulate | pp.aiProcess_GenSmoothNormals
        scene = assimpcy.aiImportFile(file, flags)
    except assimpcy.all.AssimpError as exception:
        print('ERROR loading', file + ': ', exception.args[0].decode())
        return []

    # prepare mesh nodes
    meshes = []
    for mesh in scene.mMeshes:
        mat = scene.mMaterials[mesh.mMaterialIndex].properties
        mesh = PhongMesh(shader, [mesh.mVertices, mesh.mNormals], mesh.mFaces,
                         k_d=mat.get('COLOR_DIFFUSE', (1, 1, 1)),
                         k_s=mat.get('COLOR_SPECULAR', (1, 1, 1)),
                         k_a=mat.get('COLOR_AMBIENT', (0, 0, 0)),
                         s=mat.get('SHININESS', 16.),
                         light_dir=light_dir)
        meshes.append(mesh)

    size = sum((mesh.mNumFaces for mesh in scene.mMeshes))
    print('Loaded %s\t(%d meshes, %d faces)' % (file, len(meshes), size))
    return meshes