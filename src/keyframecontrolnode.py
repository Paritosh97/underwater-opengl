from node import Node
from transformkeyframes import TransformKeyFrames
from glfw import get_time

class KeyFrameControlNode(Node):
    """ Place node with transform keys above a controlled subtree """
    def __init__(self, translate_keys, rotate_keys, scale_keys, loop=False):
        super().__init__()
        self.loop = loop
        self.keyframes = TransformKeyFrames(translate_keys, rotate_keys, scale_keys)

    def draw(self, projection, view, model):
        """ When redraw requested, interpolate our node transform from keys """
        
        time = get_time()

        # loop animations
        if(self.loop):
            time = get_time()%self.keyframes.translate_keys.times[-1]
        
        self.transform = self.keyframes.value(time)
        
        super().draw(projection, view, model)