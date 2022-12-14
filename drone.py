from mesa import Agent
from utils import found_person, battery_decrement, finding_radius
from variables import visibility, wind, temperature


class Drone(Agent):
    """A drone that searches for the missing person."""
    def __init__(self, unique_id, x, y, model, person):
        super().__init__(unique_id, model)
        self.unique_id = unique_id
        self.x = x
        self.y = y
        self.person = person

        self.battery = 1
        self.finding_radius = finding_radius(visibility)
        self.speed = 1

        self.step_nr = 0
        self.steps_dir = 0
        self.right = False
        self.left = False
        self.down = False
        self.up = True

    def xy_to_cell(self):
        """This function converts the float position of the drone to integer coordinates of a cell."""
        x = int(self.x)
        y = int(self.y)
        return x, y

    def parallel_sweep(self):
        """A search pattern that searches for the missing person in parallel lines."""

        max_y = self.model.width - 2 * self.finding_radius
        steps_right = self.finding_radius

        if self.down is True and self.right is True and self.step_nr == steps_right:
            self.right = False
            self.down = False
            self.up = True
            self.step_nr = 0

        if self.up is True and self.right is True and self.step_nr == steps_right:
            self.right = False
            self.down = True
            self.up = False
            self.step_nr = 0

        if self.step_nr == max_y:
            self.right = True
            self.step_nr = 0

        if self.right is False:
            if self.up is True:
                self.y += self.speed
                self.step_nr += 1
            elif self.down is True:
                self.y -= self.speed
                self.step_nr += 1
        else:
            self.x += self.speed
            self.step_nr += 1

        if found_person(self.pos, self.person.pos):
            print("Missing person was found!")
            self.person.found = True
            self.model.running = False

    def linear_search(self):
        """A search pattern that searches for the missing person along a path."""

        if found_person(self.pos, self.person.pos):
            print("Missing person was found!")
            self.person.found = True
            self.model.running = False

    def expanding_square(self):
        """A search pattern that searches for the missing person from its last known location."""

        if found_person(self.pos, self.person.pos):
            print("Missing person was found!")
            self.person.found = True
            self.model.running = False

        if self.steps_dir > 0:
            if self.right is True:
                self.x += self.speed
            if self.left is True:
                self.x -= self.speed
            if self.up is True:
                self.y += self.speed
            if self.down is True:
                self.y -= self.speed
            self.steps_dir -= 1
            return

        if self.step_nr % 2:
            if (self.step_nr / 2) % 2 == 0.5:
                self.right = True
                self.left = False
                self.down = False
                self.up = False
                self.x += self.speed
            else:
                self.right = False
                self.left = True
                self.down = False
                self.up = False
                self.x -= self.speed
        else:
            if (self.step_nr / 2) % 2:
                self.right = False
                self.left = False
                self.down = True
                self.up = False
                self.y -= self.speed
            else:
                self.right = False
                self.left = False
                self.down = False
                self.up = True
                self.y += self.speed
        self.step_nr += 1
        self.steps_dir = self.finding_radius * (self.step_nr / 2) - 1

    def step(self):
        self.battery -= battery_decrement(wind, temperature)
        if self.battery > 0:
            if self.person.georesq:
                self.expanding_square()
                cell = self.xy_to_cell()
                self.model.grid.move_agent(self, cell)
            elif self.person.path:
                self.linear_search()
            else:
                self.parallel_sweep()
                cell = self.xy_to_cell()
                self.model.grid.move_agent(self, cell)
        else:
            print("Drone out of battery... Please charge!")
            self.model.running = False
