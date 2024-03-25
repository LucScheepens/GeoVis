class Node:
    def __init__(self, data):
        self.data = data
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
    