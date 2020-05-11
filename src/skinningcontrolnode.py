from node import Node
from transformkeyframes import TransformKeyFrames
from transform import identity
from glfw import get_time

# -------- Skinning Control for Keyframing Skinning Mesh Bone Transforms ------
class SkinningControlNode(Node):
    """ Place node with transform keys above a controlled subtree """
    def __init__(self, *keys, transform=identity()):
        super().__init__(transform=transform)
        self.keyframes = TransformKeyFrames(*keys) if keys[0] else None
        self.world_transform = identity()

    def draw(self, projection, view, model):
        """ When redraw requested, interpolate our node transform from keys """
        if self.keyframes:  # no keyframe update should happens if no keyframes
            # loop through animations
            time = get_time()%self.keyframes.translate_keys.times[-1]
            self.transform = self.keyframes.value(time)
            
            

        # store world transform for skinned meshes using this node as bone
        self.world_transform = model @ self.transform

        # default node behaviour (call children's draw method)
        super().draw(projection, view, model)
