DISTANCE_RADIUS = 800
CLOSE_RADIUS = 800
SPEED = 8
ALIGNMENT_FACTOR = 1
COHESION_FACTOR = 0.6
SEPARATION_FACTOR = 1
QUOTA = 1
VIEW_FIELD = 100
FISH_SIZE = 10
width = 800
height = 800
depth = 200
fishes = []
import random


class Fish(object):
    def __init__(self):
        x = random.randint(0, width)
        y = random.randint(0, height)
        z = random.randint(-depth, 0)
        self.direction = self.generate_direction()
        self.pos = Vector(x,y,z)
        self.body = []
        self.body_lenght = 1
        self.max_lenght = 20
        
    def generate_direction(self):
        """
        Genaretes random initial direction as a normalized vector   
        
        :rtype: Vector
        """
        direction = Vector(random.randint(-10,10), random.randint(-10,10), random.randint(-10,10))
        return direction.get_normal()
    
    
    def get_in_range(self, other_fishes):
        """
        Returns two lists with the other fishes in close and distance range
        
        :type other_fishes: list[Fish]
        
        :rtype: tuple(list, list)
        """
        fishes_in_close_range = []
        fishes_in_distance_range = []
        for fish in other_fishes:
            if self.pos.distance_to_less_than(fish.pos, DISTANCE_RADIUS):
                fishes_in_distance_range.append(fish)
            if self.pos.distance_to_less_than(fish.pos, CLOSE_RADIUS):
                fishes_in_close_range.append(fish)
        if fishes_in_close_range is None:
            return (None, None)
        else:
            return (fishes_in_distance_range, fishes_in_close_range)
        
    def display(self):
        print 'here'
        for b in self.body:
            pushMatrix()
            translate(b.x, b.y, b.z)
            fill(255)
            rect(0,0,10,10)
            popMatrix()
        
    def has_in_field(self, other_fish):
        X = self.direction.x - other_fish.pos.x
        Y = self.direction.y - other_fish.pos.y
        Z = self.direction.z - other_fish.pos.z
        distance_vector = Vector(X, Y, Z).get_normal()
        angle = self.direction.get_angle(distance_vector)
        if angle > VIEW_FIELD:
            return False
        else:
            return True
        
    
    def get_new_direction_parts(self, other_fishes_in_range):
        """
        Generates the direction for the next frame usign Alignment, Cohesion and Separation
        """
        distance_list, close_list = other_fishes_in_range
        
        # Calculate alignment and cohesion using distance_list
        alignment_tot = Vector(0,0,0)
        cohesion_tot = Vector(0,0,0)
        distance_count = len(distance_list)
        for f in distance_list:
            alignment_tot.addz(f.direction)
            cohesion_tot.addz(f.pos)
            
        # Alignment
        alignment_tot.x /= distance_count
        alignment_tot.y /= distance_count
        alignment_tot.z /= distance_count
        normal_alignment = alignment_tot.get_normal()
        
        # Cohesion 
        cohesion_tot.x /= distance_count
        cohesion_tot.y /= distance_count
        cohesion_tot.z /= distance_count
        cohesion_tot.x -= self.pos.x
        cohesion_tot.y -= self.pos.y
        cohesion_tot.z -= self.pos.z
        normal_cohesion = cohesion_tot.get_normal()
        
        #BouningForce
        distance_from_center = self.pos.distance(Vector(width/2, height/2, -depth/2))
        normal_bound = Vector(width/2 - self.pos.x, height/2 - self.pos.y, -depth/2 - self.pos.z).get_normal()
        bound_factor = map(distance_from_center, 0, width*4, -0.1, 1) 
        
        # Calculate separation using close_list
        separation_tot = Vector(0,0,0)
        close_count = len(close_list)
        
        for f in close_list:
            separation_tot.addz(f.pos)
        separation_tot.x /= close_count
        separation_tot.y /= close_count
        separation_tot.z /= close_count
        separation_tot.x -= self.pos.x
        separation_tot.y -= self.pos.y
        separation_tot.z -= self.pos.z
        normal_separation = separation_tot.get_normal().get_opposite()
        
        return (normal_alignment, normal_cohesion, normal_separation, normal_bound, bound_factor)
    
    
    def update_direction(self, other_fishes, factors_sum):
        distance_list, close_list = self.get_in_range(other_fishes)
        if not close_list:
            return
        else:
            alignment, cohesion, separation, bound, bound_factor = self.get_new_direction_parts((distance_list, close_list))
            factors_sum += bound_factor
            tot_x = (alignment.x*ALIGNMENT_FACTOR + cohesion.x*COHESION_FACTOR + separation.x*SEPARATION_FACTOR + bound.x*bound_factor)/factors_sum
            tot_y = (alignment.y*ALIGNMENT_FACTOR + cohesion.y*COHESION_FACTOR + separation.y*SEPARATION_FACTOR + bound.y*bound_factor)/factors_sum
            tot_z = (alignment.z*ALIGNMENT_FACTOR + cohesion.z*COHESION_FACTOR + separation.z*SEPARATION_FACTOR + bound.z*bound_factor)/factors_sum
            if tot_x + tot_y + tot_z != 0:
                new_full_dir = Vector(tot_x, tot_y, tot_z).get_normal()
                X = None
                Y = None
                Z = None
                if abs(self.direction.x - new_full_dir.x) > QUOTA:
                    if self.direction.x > new_full_dir.x:
                        X = self.direction.x - QUOTA
                    else:
                        X = self.direction.x + QUOTA
                if abs(self.direction.y - new_full_dir.y) > QUOTA:
                    if self.direction.y > new_full_dir.y:
                        Y = self.direction.y - QUOTA
                        print 'yo'
                    else:
                        Y = self.direction.y + QUOTA
                if abs(self.direction.z - new_full_dir.z) > QUOTA:
                    if self.direction.z > new_full_dir.z:
                        Z = self.direction.z - QUOTA
                    else:
                        Z = self.direction.z + QUOTA
                if X is None:
                    X = new_full_dir.x
                if Y is None:
                    Y = new_full_dir.y
                if Z is None:
                    Z = new_full_dir.z
            self.body.append(self.pos)
            if len(self.body) > FISH_SIZE:
                self.body.pop(FISH_SIZE - 1)
            self.direction = Vector(X, Y, Z).get_normal()
            for i in range(len(self.body)):
                pushMatrix()
                translate(self.body[i].x, self.body[i].y, self.body[i].z)
                fill(255)
                rect(0,0,10,10)
                popMatrix()
                                    
    def update(self, other_fishes, factors_sum):
        random_factor = random.randint(-1, 1) 
        speed = self.direction.multiply(SPEED)
        self.pos.addz(speed)
        self.update_direction(other_fishes, factors_sum)
          
class Vector(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        
    def addz(self, other):
        self.x += other.x
        self.y += other.y
        self.z += other.z
        
    def multiply(self, a):
        return Vector(self.x*a, self.y*a, self.z*a)

    def get_vector(self):
        return [self.x, self.y, self.z]
    
    def get_magnitude(self):
        return sqrt(sq(self.x) + sq(self.y) + sq(self.z))
                    
    def get_normal(self):
        magn = self.get_magnitude()
        if magn == 0:
            return
        return Vector(self.x/magn, self.y/magn, self.z/magn)
    
    def get_opposite(self):
        return Vector(self.x*-1, self.y*-1, self.z*-1)
    
    def get_angle(self, other):
        angle = acos(self.x*other.x + self.y*other.y + self.z*other.z)*180/PI
        return angle
        
    def distance(self, other):
        return sqrt(sq(self.x - other.x) + sq(self.y - other.y) + sq(self.z - other.z))
        
    def distance_to_less_than(self, other, distance):
        return distance > sqrt(sq(self.x - other.x) + sq(self.y - other.y) + sq(self.z - other.z))
    

def setup():
    global fishes, sum
    sum = ALIGNMENT_FACTOR + COHESION_FACTOR + SEPARATION_FACTOR
    background(0)
    size(width, height, P3D)
    for x in range(100):
        fishes.append(Fish())
        
def draw():
    global fishes, sum
    background(0)
    for x in range(len(fishes)):
        others_list = fishes[:]
        others_list.pop(x)
        fishes[x].update(others_list, sum)
        fishes[x].display
        

    
        

         
    
        
