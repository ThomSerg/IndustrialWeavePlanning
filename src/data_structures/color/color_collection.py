class ColorCollection:
    
    def __init__(self, composite_colors=[]):
        self.composite_colors = composite_colors
        print(self.composite_colors)
        
    def add_composite_color(self, composite_color):
        self.composite_colors.append(composite_color)
        return len(self.composite_colors)-1
    
    def get_color(self, index):
        return self.composite_colors[index]