from node import Node
from transform import translate, rotate

class ControlNode(Node):

    def __init__(self, key_up, key_down, key_left, key_right, speed):
        super().__init__()
        self.speed = speed
        self.zpos = 0
        self.xpos = 0
        self.key_up, self.key_down, self.key_left, self.key_right = key_up, key_down, key_left, key_right

    def key_handler(self, key):
        self.zpos += self.speed * int(key == self.key_up)
        self.zpos -= self.speed * int(key == self.key_down)
        self.xpos -= self.speed * int(key == self.key_right)
        self.xpos += self.speed * int(key == self.key_left)
        self.transform = translate(self.xpos, 0, self.zpos)
        super().key_handler(key)