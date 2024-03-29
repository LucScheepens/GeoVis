from path_generation import *

class Station:
    def __init__(self, name, x, y) -> None:
        self.name = name 
        self.coordinates = (x,y)
        self.slots = self.create_slots(x,y)
    
    def create_slots(x,y, d = 1):
        coordinates = [
            (x + d, y + d),
            (x + d, y - d),
            (x - d, y + d),
            (x - d, y - d)
        ]
        return coordinates


class Node:
    def __init__(self, list_of_Station, slots):
        self.all_stations = list_of_Station
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def remove_child(self, child):
        if child in self.children:
            self.children.remove(child)

    def get_children(self):
        return self.children

    def is_leaf(self):
        return len(self.children) == 0

    def __str__(self):
        return str(self.data)

    def cost(self):
        pass
    
    def generate_path(self):
        pass