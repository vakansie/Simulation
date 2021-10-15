import tkinter
import numpy
import random
from time import sleep
from tkinter import filedialog
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
        self.seed             = []
        self.auto_running     = False
        self.faster_eating    = False
        self.recursive_eating = False
        self.random_spread    = True
        self.random_iter_order= True
        self.single_change    = True
        self.loaded_simulation= False
        self.spread_factor    = 1
        self.direction_choices= [-1, -1, 0, 1, 1]
        self.direction_options= list(dict.fromkeys(list(permutations(self.direction_choices, 2))))
        self.spin             = random.randint(0, len(self.direction_options)-1)
        self.population       = [0,0,0,0]
        self.changed_cells    = {}
        self.population_bar   = self.create_population_bar()
        self.spread_slider    = self.create_slider()
        self.bind_keys()
        self.create_buttons()
        self.create_menu()

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
    
    def create_menu(self):
        menu_bar = tkinter.Menu(self.window, tearoff=0)
        view_menu = tkinter.Menu(menu_bar)
        view_menu.add_command(label='Save                  Ctrl-S', command=lambda: self.save_state())
        view_menu.add_command(label='Load                  Ctrl-L', command=lambda: self.load_state())
        view_menu.add_command(label='Toggle recursive eating    R', command=lambda: self.toggle_recursive_eating())
        view_menu.add_command(label='Toggle spread direction    D', command=lambda: self.toggle_direction_choice())
        view_menu.add_command(label='Toggle add reverse eating  F', command=lambda: self.toggle_faster_eating())
        view_menu.add_command(label='Toggle random spreading    X', command=lambda: self.toggle_random_spread())
        view_menu.add_command(label='Toggle random order        Z', command=lambda: self.toggle_random_iter())
        view_menu.add_command(label='Toggle only change once    C', command=lambda: self.toggle_only_change_once())
        view_menu.add_command(label='Reset                Shift-R', command=lambda: self.reset())    
        view_menu.add_command(label='New                  Shift-N', command=lambda: self.new_simulation())
        menu_bar.add_cascade(label="Simulation options", menu=view_menu)
        self.window.config(menu=menu_bar)

    def create_slider(self):
        spread_slider = tkinter.Scale(self.window, from_=8, to=1, command=lambda x: self.get_spread_from_slider())
        spread_slider.set(self.spread_factor)
        spread_slider.grid(row=0, column=7)
        return spread_slider

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
        self.window.bind("R", lambda x: self.reset())
        self.window.bind("N", lambda x: self.new_simulation())
        self.window.bind("2", lambda x: self.two_steps_one_back())
        self.window.bind("<Button-3>", lambda x: self.nuke(x))
        self.window.bind("f", lambda x: self.toggle_faster_eating())
        self.window.bind("r", lambda x: self.toggle_recursive_eating())
        self.window.bind("d", lambda x: self.toggle_direction_choice())
        self.window.bind("x", lambda x: self.toggle_random_spread())
        self.window.bind("z", lambda x: self.toggle_random_iter())
        self.window.bind("c", lambda x: self.toggle_only_change_once())
        self.window.bind("=", lambda x: self.set_spread_factor(1))
        self.window.bind("-", lambda x: self.set_spread_factor(-1))
        self.window.bind("<KeyPress-Up>", lambda x: self.set_spin(1))
        self.window.bind("<KeyPress-Down>", lambda x: self.set_spin(-1))
        self.window.bind("<Control-s>", lambda x: self.save_state())
        self.window.bind("<Control-l>", lambda x: self.load_state())

    def mainloop(self):
        self.window.mainloop()

    def set_seed(self):
        for i in range(100):
            x, y = random.choice(range(100)), random.choice(range(100))
            force = random.choice([1,2,3])
            self.array[x][y] = force
            self.changed_cells[(x, y)] = force
        self.seed = self.array.copy()

    def draw(self):
        self.clear_canvas()
        self.population = [0,0,0,0]
        for x in range(self.array.shape[0]):
            for y in range(self.array.shape[1]):
                x_pos, y_pos = x * self.block_size, y * self.block_size
                if self.array[x][y] == 1:
                    Spreader(x_pos, y_pos, x_pos+self.block_size, y_pos+self.block_size, fill= "green", tags=f'{(x, y)}')
                elif self.array[x][y] == 2:
                    Eater(x_pos, y_pos, x_pos+self.block_size, y_pos+self.block_size, fill= "red", tags=f'{(x, y)}')
                elif self.array[x][y] == 3:
                    Cleaner(x_pos, y_pos, x_pos+self.block_size, y_pos+self.block_size, fill= "yellow", tags=f'{(x, y)}')
        self.draw_population_bar()

    def fast_draw(self):
        for coords, force in self.changed_cells.items():
            x, y = coords[0], coords[1]
            x_pos, y_pos = x * self.block_size, y * self.block_size
            tag = f'x{coords[0]}y{coords[1]}'
            occupant = self.canvas.find_withtag(tag)
            self.canvas.delete(occupant)
            if force == 1:
                Spreader(x_pos, y_pos, x_pos+self.block_size, y_pos+self.block_size, fill= "green", tags=tag)
            elif force == 2:
                Eater(x_pos, y_pos, x_pos+self.block_size, y_pos+self.block_size, fill= "red", tags=tag)
            elif force == 3:
                Cleaner(x_pos, y_pos, x_pos+self.block_size, y_pos+self.block_size, fill= "yellow", tags=tag)
        self.draw_population_bar()
        self.changed_cells = {}

    def iterate(self):
        #self.changed_cells = {} #comment out if fast_draw
        row_order = [x for x in range(self.array.shape[0])]
        column_order = [y for y in range(self.array.shape[1])]
        if self.random_iter_order:
            random.shuffle(row_order)
            random.shuffle(column_order)
        for x in row_order:
            for y in column_order:
                condition = (((x, y) not in self.changed_cells) if self.single_change else True)
                if self.array[x][y] == 1 and condition:
                    Spreader.iterate(x, y)
                elif self.array[x][y] == 2 and condition:
                    Eater.iterate(x, y)
                elif self.array[x][y] == 3 and condition:
                    Cleaner.iterate(x, y)

    def step(self):
        ## bound to <Right Arrow Key>
        self.last_states.append(self.array.copy())
        if len(self.last_states) > 50: 
            self.last_states.remove(self.last_states[0])
        self.iterate()
        self.fast_draw()

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
            sleep(0.1)
            self.window.update()

    def auto_back(self):
        ## bound to <b>
        self.auto_running = not self.auto_running
        while self.auto_running:
            self.back()
            sleep(0.1)
            self.window.update()
            if len(self.last_states) == 0: self.auto_running = False

    def reset(self):
        ## bound to <Shift-R>
        self.array = self.seed.copy()
        self.draw()
        self.window.update()

    def save_state(self):
        file = filedialog.asksaveasfilename(initialdir= ".\Save Files",title= "Save As",
                                      filetypes = (('numpy files', '*.npy'),('All files', '*.npy')))
        numpy.save(f'{file}', self.array)
    
    def load_state(self):
        self.set_defaults()
        file = filedialog.askopenfilename(initialdir= ".\Save Files",
                                      title     = "Select a File",
                                      filetypes = (('numpy files', '*.npy'),('All files', '*.*')))
        if not file: return
        self.array = numpy.load(file)
        self.loaded_simulation = True
        self.seed = self.array.copy()
        self.draw()

    def two_steps_one_back(self):
        ## bound to <2>
        self.auto_running = not self.auto_running
        while self.auto_running:
            self.step()
            self.window.update()
            sleep(0.1)
            self.step()
            self.window.update()
            sleep(0.1)
            self.back()

    def toggle_faster_eating(self):
        ## bound to <f>
        self.faster_eating = not self.faster_eating
        print(f"faster eating = {'ON' if self.faster_eating else 'OFF'}")

    def toggle_recursive_eating(self):
        ## bound to <r>
        self.recursive_eating = not self.recursive_eating
        print(f"recursive eating = {'ON' if self.recursive_eating else 'OFF'}")

    def toggle_direction_choice(self):
        ## bound to <d>
        if 0 in self.direction_choices:self.direction_choices.remove(0)
        else: self.direction_choices.append(0)
        self.direction_options= list(dict.fromkeys(list(permutations(self.direction_choices, 2))))
        self.spin = random.randint(0, len(simulation.direction_options)-1)
        print(f'directions = {"ALL" if 0 in self.direction_choices else "DIAGONAL"}')

    def toggle_random_spread(self):
        ## bound to <x>
        self.random_spread = not self.random_spread
        print(f"random spreading = {'ON' if self.random_spread else 'OFF'}")

    def toggle_random_iter(self):
        ## bound to <z>
        self.random_iter_order = not self.random_iter_order
        print(f"random iter order = {'ON' if self.random_iter_order else 'OFF'}")

    def toggle_only_change_once(self):
        ## bound to <c>
        self.single_change = not self.single_change
        print(f"only change once = {'ON' if self.single_change else 'OFF'}")

    def set_spread_factor(self, sign):
        ## bound to <+><->
        self.spread_factor += sign
        if self.spread_factor == 9: self.spread_factor = 1
        if self.spread_factor == 0: self.spread_factor = 8
        self.spread_slider.set(self.spread_factor)
        print(f'spread_factor = {self.spread_factor}')

    def get_spread_from_slider(self):
        self.spread_factor = self.spread_slider.get()

    def set_spin(self, sign):
        ## bound to <KeyPress-Up> <KeyPress-Down>
        simulation.spin += sign
        if self.spin == len(self.direction_options): self.spin = 0
        if self.spin < 0: self.spread_factor = len(self.direction_options) - 1
        print(f'spin = {self.spin}')

    def set_defaults(self):
        self.array = numpy.zeros((100, 100), dtype=numpy.int8)
        self.auto_running = False
        self.faster_eating = False
        self.recursive_eating = False
        self.random_spread = True
        self.random_iter_order = True
        self.single_change = True
        self.direction_choices = [-1, -1, 0, 1, 1]
        self.direction_options= list(dict.fromkeys(list(permutations(self.direction_choices, 2))))
        self.spin = random.randint(0, len(simulation.direction_options)-1)
        self.spread_factor = 1
        self.last_states = []
        self.changed_cells = {}
        self.spread_slider.set(1)
        print('SETTINGS RESET')

    def new_simulation(self):
        ## bound to <Shift-N>
        self.loaded_simulation = False
        self.clear_canvas()
        self.clear_population_bar()
        self.set_defaults()
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

    def get_population(self):
        for force in range(len(self.population)):
            count = len(self.array[numpy.where(self.array == force)])
            self.population[force] = count

    def draw_population_bar(self):
        self.clear_population_bar()
        self.get_population()
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

    def surrounded(force_id, array_x_pos, array_y_pos):
        for direction in simulation.direction_options:
            x, y = direction
            if 0 <= array_x_pos + x <= 99 and 0 <= array_y_pos + y <= 99:
                if simulation.array[array_x_pos+x][array_y_pos+y] != force_id:
                    return False
        return True

class Spreader(Forces):
    def iterate(array_x_pos, array_y_pos):
        if Forces.surrounded(1, array_x_pos, array_y_pos): return
        random_index = random.randint(0, len(simulation.direction_options))
        for i in range(simulation.spread_factor):
            try: x_direction, y_direction = simulation.direction_options[(random_index - i if simulation.random_spread else simulation.spin - i)]
            except IndexError: break
            if 0 <= array_x_pos + x_direction <= 99 and 0 <= array_y_pos + y_direction <= 99:
                target_x = array_x_pos + x_direction
                target_y = array_y_pos + y_direction
            else: continue
            if simulation.array[target_x][target_y] == 1: continue
            if simulation.array[target_x][target_y] in [0,3]:
                simulation.array[target_x][target_y] = 1
                simulation.changed_cells[(target_x, target_y)] = 1
            if simulation.faster_eating:
                if simulation.array[target_x][target_y] == 2:
                    simulation.array[array_x_pos][array_y_pos] = 2
                    simulation.changed_cells[(array_x_pos, array_y_pos)] = 2
            if simulation.recursive_eating and simulation.array[target_x][target_y] == 3:
                Spreader.iterate(target_x, target_y)

class Eater(Forces):
    def iterate(array_x_pos, array_y_pos):
        if Forces.surrounded(2, array_x_pos, array_y_pos): return
        random_index = random.randint(0, len(simulation.direction_options))
        for i in range(simulation.spread_factor):
            try: x_direction, y_direction = simulation.direction_options[(random_index - i if simulation.random_spread else simulation.spin - i)]
            except IndexError: break
            if 0 <= array_x_pos + x_direction <= 99 and 0 <= array_y_pos + y_direction <= 99:
                target_x = array_x_pos + x_direction
                target_y = array_y_pos + y_direction
            else: continue
            if simulation.array[target_x][target_y] == 2: continue
            if simulation.array[target_x][target_y] == 0:
                simulation.array[array_x_pos][array_y_pos] = 0
                simulation.changed_cells[(array_x_pos, array_y_pos)] = 0
            if simulation.array[target_x][target_y] in [0,1]:
                simulation.array[target_x][target_y] = 2
                simulation.changed_cells[(target_x, target_y)] = 2
            if simulation.faster_eating:
                if simulation.array[target_x][target_y] == 3:
                    simulation.array[array_x_pos][array_y_pos] = 3
                    simulation.changed_cells[(array_x_pos, array_y_pos)] = 3
            if simulation.recursive_eating and simulation.array[target_x][target_y] == 1:
                Eater.iterate(target_x, target_y)

class Cleaner(Forces):
    def iterate(array_x_pos, array_y_pos):
        if Forces.surrounded(3, array_x_pos, array_y_pos): return
        random_index = random.randint(0, len(simulation.direction_options))
        for i in range(simulation.spread_factor):
            try: x_direction, y_direction = simulation.direction_options[(random_index - i if simulation.random_spread else simulation.spin - i)]
            except IndexError: break
            if 0 <= array_x_pos + x_direction <= 99 and 0 <= array_y_pos + y_direction <= 99:
                target_x = array_x_pos + x_direction
                target_y = array_y_pos + y_direction
            else: continue
            if simulation.array[target_x][target_y] == 3: continue
            if simulation.array[target_x][target_y] in [0,2]:
                simulation.array[target_x][target_y] = 3
                simulation.changed_cells[(target_x, target_y)] = 3
            if simulation.faster_eating:
                if simulation.array[target_x][target_y] == 1:
                    simulation.array[array_x_pos][array_y_pos] = 1
                    simulation.changed_cells[(array_x_pos, array_y_pos)] = 1
            if simulation.recursive_eating and simulation.array[target_x][target_y] == 2:
                Cleaner.iterate(target_x, target_y)

def main():
    global simulation
    simulation = Simulation()
    simulation.set_seed()
    simulation.draw()
    simulation.mainloop()

if __name__ == '__main__':
    main()