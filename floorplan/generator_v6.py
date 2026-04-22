# Generator v6

# Improved 2D spatial coherence
# Features:
# - Independent bedroom entrances
# - Circulation constraints
# - Door visualization

class FloorPlanGenerator:
    def __init__(self):
        # Initialize parameters and settings
        self.bedrooms = []
        self.doors = []
        self.circulation_constraints = []

    def add_bedroom(self, entrance_position):
        # Add a bedroom with an independent entrance
        bedroom = {'entrance': entrance_position}
        self.bedrooms.append(bedroom)
        self.visualize_door(entrance_position)

    def visualize_door(self, position):
        # Visualize door on the floor plan
        door = {'position': position}
        self.doors.append(door)
        print(f"Door added at {position}")

    def add_circulation_constraint(self, constraint):
        # Add circulation constraints to the floor plan
        self.circulation_constraints.append(constraint)

    def generate_floor_plan(self):
        # Method to generate the complete floor plan
        print('Generating floor plan with the following properties:')
        print(f'Bedrooms: {self.bedrooms}')
        print(f'Doors: {self.doors}')
        print(f'Constraints: {self.circulation_constraints}')
        # Implement the logic to render the floor plan

# Example usage
if __name__ == '__main__':
    generator = FloorPlanGenerator()
    generator.add_bedroom((1, 2))  # Bedroom 1 entrance position
    generator.add_bedroom((3, 4))  # Bedroom 2 entrance position
    generator.add_circulation_constraint('Pathway must be at least 3 feet wide.')
    generator.generate_floor_plan()