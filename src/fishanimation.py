import sys
import math
from random import random, randrange
from transform import vec, quaternion, quaternion_from_euler

class FishAnimation:

    def __init__(self):

        # get random direction for fish motion
        if(random() > 0.5):
            self.direction = 1
        else:
            self.direction = -1

        self.timeskip = randrange(3, 5)
        

    def get_translate_keys(self):

        # generate translate keys
        start = random()*0.9
        height = randrange(-6, 8)/10
        return {0: vec(-start*self.direction, height, -start*self.direction), 2*self.timeskip: vec(-start*self.direction, height, start*self.direction), 3*self.timeskip: vec(start*self.direction, height, start*self.direction), 4*self.timeskip: vec(start*self.direction, height, -start*self.direction), 5*self.timeskip: vec(-start*self.direction, height, -start*self.direction)}

    def get_rotate_keys(self):

        # choose rotation keys based on anti-clockwise/clockwise

        rotate_keys_anticlockwise = {0: quaternion(), 2*self.timeskip-0.2: quaternion(), 2*self.timeskip: quaternion_from_euler(0, 90, 0), 3*self.timeskip-0.2: quaternion_from_euler(0, 90, 0), 3*self.timeskip: quaternion_from_euler(0, 180, 0), 4*self.timeskip-0.2: quaternion_from_euler(0, 180, 0), 4*self.timeskip: quaternion_from_euler(0, 270, 0), 5*self.timeskip-0.2: quaternion_from_euler(0, 270, 0),  5*self.timeskip: quaternion()}

        rotate_keys_clockwise = {0: quaternion_from_euler(0, 180, 0), 2*self.timeskip-0.2: quaternion_from_euler(0, 180, 0), 2*self.timeskip: quaternion_from_euler(0, 270, 0), 3*self.timeskip-0.2: quaternion_from_euler(0, 270, 0), 3*self.timeskip: quaternion(), 14*self.timeskip-0.2: quaternion(), 4*self.timeskip: quaternion_from_euler(0, 90, 0), 5*self.timeskip-0.2: quaternion_from_euler(0, 90, 0),  5*self.timeskip: quaternion_from_euler(0, 180, 0)}

        if(self.direction == 1):
            return rotate_keys_anticlockwise
        else:
            return rotate_keys_clockwise