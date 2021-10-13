import tkinter
import numpy
import random
import time
from itertools import permutations

class Simulation():

    def __init__(self):
        self.array            = numpy.zeros((100, 100), dtype=numpy.int8)
        self.height           = 500
        self.width            = 500
        self.window           = self.create_window()
        self.canvas           = self.create_canvas()
        self.block_size       = 5
        self.last_states      = []
        self.auto_running     = False
        self.faster_eating    = False
        self.recursive_eating = False
        self.random_spread    = True
        self.random_iter_order= True
        self.spreading_factor = 1
        self.direction_choices= [-1, -1, 1, 1]
        self.direction_options= list(dict.fromkeys(list(permutations(self.direction_choices, 2))))
        self.spin             = random.randint(0, len(self.direction_options)-1)
        self.population       = [0,0,0,0]
        self.changed_cells    = []
        self.population_bar   = self.create_population_bar()
        self.bind_keys()
        self.create_buttons()

    def create_window(self):
        window = tkinter.Tk()
        window.title('Simulation')
        window.geometry('+100+0')
        return window

    def create_canvas(self):
        canvas = tkinter.Canvas(self.window, bg="black", height=self.height, width=self.width)
        canvas.grid(row=0, columnspan=6)
        return canvas

    def clear_canvas(self):
        self.canvas.delete("all")

    def create_buttons(self):
        tkinter.Button(self.window, text='Auto>', borderwidth=1, font=('Verdana','18'),
                    command= lambda: self.auto_run()).grid(row=1, column=1)
        tkinter.Button(self.window, text='<Auto', borderwidth=1, font=('Verdana','18'),
                    command= lambda: self.auto_back()).grid(row=1, column=0)
        tkinter.Button(self.window, text='Step>', borderwidth=1, font=('Verdana','18'),
                    command= lambda: self.step()).grid(row=1, column=3)
        tkinter.Button(self.window, text='New', borderwidth=1, font=('Verdana','18'),
                    command= lambda: self.new_simulation()).grid(row=1, column=4)
        tkinter.Button(self.window, text='<Step', borderwidth=1, font=('Verdana','18'),
                    command= lambda: self.back()).grid(row=1, column=2)

    def create_population_bar(self):
        canvas = tkinter.Canvas(self.window, bg="black", height=20, width=self.width)
        canvas.grid(row=2, columnspan=6)
        return canvas

    def clear_population_bar(self):
        self.population_bar.delete("all")

    def bind_keys(self):
        self.window.bind("<KeyPress-Right>", lambda x: self.step())
        self.window.bind("<KeyPress-Left>", lambda x: self.back())
        self.window.bind("<space>", lambda x: self.auto_run())
        self.window.bind("b", lambda x: self.auto_back())
        self.window.bind("R", lambda x: self.new_simulation())
        self.window.bind("2", lambda x: self.two_steps_one_back())
        self.window.bind("<Button-3>", lambda x: self.nuke(x))
        self.window.bind("f", lambda x: self.toggle_faster_eating())
        self.window.bind("r", lambda x: self.toggle_recursive_eating())
        self.window.bind("d", lambda x: self.toggle_direction_choice())
        self.window.bind("x", lambda x: self.toggle_random_spread())
        self.window.bind("z", lambda x: self.toggle_random_iter())
        self.window.bind("=", lambda x: self.set_spreading_factor(1))
        self.window.bind("-", lambda x: self.set_spreading_factor(-1))
        self.window.bind("<KeyPress-Up>", lambda x: self.set_spin(1))
        self.window.bind("<KeyPress-Down>", lambda x: self.set_spin(-1))

    def mainloop(self):
        self.window.mainloop()

    def set_seed(self):
        for i in range(100):
            x, y = random.choice(range(100)), random.choice(range(100))
            self.array[x][y] =  random.choice([1,2,3]) 
            self.changed_cells.append((x, y))

    def draw(self):
        self.clear_canvas()
        self.population = [0,0,0,0]
        for x in range(self.array.shape[0]):
            for y in range(self.array.shape[1]):
                y_pos = y * self.block_size
                x_pos = x * self.block_size
                if self.array[x][y] == 1:
                    Spreader(x_pos, y_pos, x_pos+self.block_size, y_pos+self.block_size, fill = "green")
                    self.population[1] += 1
                elif self.array[x][y] == 2:
                    Eater(x_pos, y_pos, x_pos+self.block_size, y_pos+self.block_size, fill = "red")
                    self.population[2] += 1
                elif self.array[x][y] == 3:
                    Cleaner(x_pos, y_pos, x_pos+self.block_size, y_pos+self.block_size, fill = "yellow")
                    self.population[3] += 1
                else: self.population[0] += 1
        self.draw_population_bar()

    def iterate(self):

        row_order = [x for x in range(self.array.shape[0])]
        column_order = [y for y in range(self.array.shape[1])]
        if self.random_iter_order:
            random.shuffle(row_order)
            random.shuffle(column_order)
        for x in row_order:
            for y in column_order:
                if self.array[x][y] == 1 and (x, y) not in self.changed_cells:
                    Spreader.iterate(x, y)
                elif self.array[x][y] == 2 and (x, y) not in self.changed_cells:
                    Eater.iterate(x, y)
                elif self.array[x][y] == 3 and (x, y) not in self.changed_cells:
                    Cleaner.iterate(x, y)
        self.changed_cells = []

    def step(self):
        ## bound to <Right Arrow Key>
        self.last_states.append(self.array.copy())
        if len(self.last_states) > 50: 
            self.last_states.remove(self.last_states[0])
        self.iterate()
        self.draw()

    def back(self):
        ## bound to <Left Arrow Key>
        if self.last_states:
            self.array = self.last_states[-1]
            self.last_states.pop()
            self.draw()

    def auto_run(self):
        ## bound to <Spacebar>
        self.auto_running = not self.auto_running
        while self.auto_running:
            self.step()
            time.sleep(0.1)
            self.window.update()

    def auto_back(self):
        ## bound to <b>
        self.auto_running = not self.auto_running
        while self.auto_running:
            self.back()
            time.sleep(0.1)
            self.window.update()
            if len(self.last_states) == 0: self.auto_running = False

    def two_steps_one_back(self):
        ## bound to <2>
        self.auto_running = not self.auto_running
        while self.auto_running:
            self.step()
            self.window.update()
            time.sleep(0.1)
            self.step()
            self.window.update()
            time.sleep(0.1)
            self.back()

    def toggle_faster_eating(self):
        self.faster_eating = not self.faster_eating
        print(f"faster eating = {'ON' if self.faster_eating else 'OFF'}")

    def toggle_recursive_eating(self):
        self.recursive_eating = not self.recursive_eating
        print(f"recursive eating = {'ON' if self.recursive_eating else 'OFF'}")

    def toggle_direction_choice(self):
        if 0 in self.direction_choices:self.direction_choices.remove(0)
        else: self.direction_choices.append(0)
        self.direction_options= list(dict.fromkeys(list(permutations(self.direction_choices, 2))))
        self.spin = random.randint(0, len(simulation.direction_options)-1)
        print(f'directions = {"ALL" if 0 in self.direction_choices else "DIAGONAL"}')

    def toggle_random_spread(self):
        self.random_spread = not self.random_spread
        print(f"random spreading = {'ON' if self.random_spread else 'OFF'}")

    def toggle_random_iter(self):
        self.random_iter_order = not self.random_iter_order
        print(f"random iter order = {'ON' if self.random_iter_order else 'OFF'}")

    def set_spreading_factor(self, sign):
        self.spreading_factor += sign
        if self.spreading_factor == 9: self.spreading_factor = 1
        if self.spreading_factor == 0: self.spreading_factor = 8
        print(f'spreading_factor = {self.spreading_factor}')

    def set_spin(self, sign):
        simulation.spin += sign
        if self.spin == len(self.direction_options): self.spin = 0
        if self.spin < 0: self.spreading_factor = len(self.direction_options) - 1
        print(f'spin = {self.spin}')

    def new_simulation(self):
        ## bound to <Shift-r>
        self.array = numpy.zeros((100, 100), dtype=numpy.int8)
        self.auto_running = False
        self.faster_eating = False
        self.recursive_eating = False
        self.random_spread = True
        self.random_iter_order = True
        self.direction_choices = [-1, -1, 1, 1]
        self.direction_options= list(dict.fromkeys(list(permutations(self.direction_choices, 2))))
        self.spin = random.randint(0, len(simulation.direction_options)-1)
        self.spreading_factor = 1
        self.last_states = []
        self.changed_cells = []
        print('SETTINGS RESET')
        self.clear_canvas()
        self.clear_population_bar()
        self.set_seed()
        self.draw()
        self.window.update()

    def nuke(self, mouse_click):
        ## bound to <Mouse Button 3>
        nuke_radius = 10
        array_x, array_y = round((mouse_click.x)/5), round((mouse_click.y)/5)
        for row in range(array_x - nuke_radius, array_x + nuke_radius):
            for column in range(array_y - 10, array_y + 10):
                try: self.array[max(row, 0)][max(column, 0)] = 0
                except IndexError: continue
        self.draw()
        self.window.update()

    def draw_population_bar(self):
        self.clear_population_bar()
        max_population = self.array.shape[0] * self.array.shape[1]
        green_width  = self.population[1] / max_population * self.width
        red_width    = self.population[2] / max_population * self.width
        yellow_width = self.population[3] / max_population * self.width
        self.population_bar.create_rectangle(0, 0, green_width, 20, fill='green')
        self.population_bar.create_rectangle(green_width, 0, green_width+red_width, 20, fill='red')
        self.population_bar.create_rectangle(green_width+red_width, 0, green_width+red_width+yellow_width, 20, fill='yellow')

class Forces():
    def __init__(self, x0, x1, y0, y1, **kwargs):
        self.rectangle = simulation.canvas.create_rectangle(x0, x1, y0, y1, **kwargs)

class Spreader(Forces):
    def iterate(array_x_pos, array_y_pos):
        random_index = random.randint(0, len(simulation.direction_options))
        for i in range(simulation.spreading_factor):
            try: x_direction, y_direction = simulation.direction_options[(random_index - i if simulation.random_spread else simulation.spin - i)]
            except IndexError: break
            target_x = min(array_x_pos + x_direction,99)
            target_y = min(array_y_pos + y_direction,99)
            if simulation.array[target_x][target_y] in [0,3]:
                simulation.array[target_x][target_y] = 1
                simulation.changed_cells.append((target_x, target_y))
            if simulation.faster_eating:
                if simulation.array[target_x][target_y] == 2:
                    simulation.array[array_x_pos][array_y_pos] = 2
                    simulation.changed_cells.append((array_x_pos, array_y_pos))
            if simulation.recursive_eating and simulation.array[target_x][target_y] == 3:
                Spreader.iterate(target_x, target_y)
        list(dict.fromkeys(simulation.changed_cells))

class Eater(Forces):
    def iterate(array_x_pos, array_y_pos):
        random_index = random.randint(0, len(simulation.direction_options))
        for i in range(simulation.spreading_factor):
            try: x_direction, y_direction = simulation.direction_options[(random_index - i if simulation.random_spread else simulation.spin - i)]
            except IndexError: break
            target_x = min(array_x_pos + x_direction,99)
            target_y = min(array_y_pos + y_direction,99)
            if simulation.array[target_x][target_y] == 0:
                simulation.array[array_x_pos][array_y_pos] = 0
                simulation.changed_cells.append((array_x_pos, array_y_pos))
            if simulation.array[target_x][target_y] in [0,1]:
                simulation.array[target_x][target_y] = 2
                simulation.changed_cells.append((target_x, target_y))
            if simulation.faster_eating:
                if simulation.array[target_x][target_y] == 3:
                    simulation.array[array_x_pos][array_y_pos] = 3
                    simulation.changed_cells.append((array_x_pos, array_y_pos))
            if simulation.recursive_eating and simulation.array[target_x][target_y] == 1:
                Eater.iterate(target_x, target_y)
        list(dict.fromkeys(simulation.changed_cells))

class Cleaner(Forces):
    def iterate(array_x_pos, array_y_pos):
        random_index = random.randint(0, len(simulation.direction_options))
        for i in range(simulation.spreading_factor):
            try: x_direction, y_direction = simulation.direction_options[(random_index - i if simulation.random_spread else simulation.spin - i)]
            except IndexError: break
            target_x = min(array_x_pos + x_direction,99)
            target_y = min(array_y_pos + y_direction,99)
            if simulation.array[target_x][target_y] in [0,2]:
                simulation.array[target_x][target_y] = 3
                simulation.changed_cells.append((target_x, target_y))
            if simulation.faster_eating:
                if simulation.array[target_x][target_y] == 1:
                    simulation.array[array_x_pos][array_y_pos] = 1
                    simulation.changed_cells.append((array_x_pos, array_y_pos))
            if simulation.recursive_eating and simulation.array[target_x][target_y] == 2:
                Cleaner.iterate(target_x, target_y)
        list(dict.fromkeys(simulation.changed_cells))

def main():
    global simulation
    simulation = Simulation()
    simulation.set_seed()
    simulation.draw()
    simulation.mainloop()

if __name__ == '__main__':
    main()