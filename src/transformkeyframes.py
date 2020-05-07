from keyframes import KeyFrames
from transform import translate, quaternion_matrix, scale, quaternion_slerp

class TransformKeyFrames:
    """ KeyFrames-like object dedicated to 3D transforms """
    def __init__(self, translate_keys, rotate_keys, scale_keys):
        """ stores 3 keyframe sets for translation, rotation, scale """
        self.translate_keys = KeyFrames(translate_keys)
        self.rotate_keys = KeyFrames(rotate_keys, interpolation_function=quaternion_slerp)
        self.scale_keys = KeyFrames(scale_keys)


    def value(self, time):
        """ Compute each component's interpolation and compose TRS matrix """
        translate_mat = translate(self.translate_keys.value(time))
        rotate_mat = quaternion_matrix(self.rotate_keys.value(time))
        scale_mat = scale(self.scale_keys.value(time))

        # return the composed matrix
        return (translate_mat @ rotate_mat @ scale_mat)