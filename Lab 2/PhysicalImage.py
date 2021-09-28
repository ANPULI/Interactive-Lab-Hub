import random
class PhysicalImage:
    def __init__(self, img, x=0, y=0):
        self.img = img
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
    
    def set_canvas_size(self, canvas_width, canvas_height):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.check_boundry()
    
    def check_boundry(self):
        # left
        if self.x <= 0 or self.x + self.img.width >= self.canvas_width:
            self.vx = -self.vx
        if self.y <= 0 or self.y + self.img.height >= self.canvas_height:
            self.vy = -self.vy
    
    def random_speed(self):
        self.vx, self.vy = random.randint(-5, 5), random.randint(-5, 5)
