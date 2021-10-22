import tkinter
import numpy
import random
from time import sleep, time
from tkinter import filedialog
from itertools import permutations


class Simulation():

    def __init__(self):
        self.array            = self.create_array()
        self.height           = 500
        self.width            = 500
        self.window           = self.create_window()
        self.canvas           = self.create_canvas()
        self.block_size       = 5
        self.last_states      = []
        self.seed             = []
        self.seed_density     = 100
        self.auto_running     = False
        self.faster_eating    = False
        self.recursive_eating = False
        self.random_spread    = True
        self.random_iter_order= True
        self.single_change    = True
        self.loaded_simulation= False
        self.only_draw_changes= False
        self.recursion_factor = 1
        self.spread_factor    = 1
        self.direction_choices= [-1, -1, 0, 1, 1]
        self.direction_options= list(dict.fromkeys(list(permutations(self.direction_choices, 2))))
        self.spin             = random.randint(0, len(self.direction_options)-1)
        self.population       = [0,0,0,0]
        self.changed_cells    = {}
        self.population_bar   = self.create_population_bar()
        self.spread_slider    = self.create_spread_slider()
        self.recursion_slider = self.create_recursion_slider()
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
        canvas.grid(rowspan=2, columnspan=6)
        return canvas

    def create_array(self):
        array = numpy.zeros((100, 100), dtype=numpy.int8)
        return array

    def clear_canvas(self):
        self.canvas.delete("all")

    def create_buttons(self):
        tkinter.Button(self.window, text='Auto>', borderwidth=1, font=('Verdana','18'),
                    command= lambda: self.auto_run()).grid(row=2, column=1)
        tkinter.Button(self.window, text='<Auto', borderwidth=1, font=('Verdana','18'),
                    command= lambda: self.auto_back()).grid(row=2, column=0)
        tkinter.Button(self.window, text='Step>', borderwidth=1, font=('Verdana','18'),
                    command= lambda: self.step()).grid(row=2, column=3)
        tkinter.Button(self.window, text='New', borderwidth=1, font=('Verdana','18'),
                    command= lambda: self.new_simulation()).grid(row=2, column=4)
        tkinter.Button(self.window, text='<Step', borderwidth=1, font=('Verdana','18'),
                    command= lambda: self.back()).grid(row=2, column=2)
    
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
        view_menu.add_command(label='Toggle only draw changed   V', command=lambda: self.toggle_draw_changes_only())
        view_menu.add_command(label='Default Settings     Shift-D', command=lambda: self.set_defaults())
        view_menu.add_command(label='Reset                Shift-R', command=lambda: self.reset())
        view_menu.add_command(label='New                  Shift-N', command=lambda: self.new_simulation())
        view_menu.add_command(label='Set Seed Density'            , command=lambda: self.set_seed_density())
        menu_bar.add_cascade(label="Simulation options", menu=view_menu)
        self.window.config(menu=menu_bar)

    def create_spread_slider(self):
        spread_slider = tkinter.Scale(self.window, from_=8, to=1, command=lambda x: self.get_spread_from_slider())
        spread_slider.set(self.spread_factor)
        spread_slider.grid(row=0, column=7)
        return spread_slider

    def create_recursion_slider(self):
        recursion_slider = tkinter.Scale(self.window, from_=8, to=1, command=lambda x: self.get_recursion_from_slider())
        recursion_slider.set(self.recursion_factor)
        recursion_slider.grid(row=1, column=7)
        return recursion_slider

    def create_population_bar(self):
        canvas = tkinter.Canvas(self.window, bg="black", height=20, width=self.width)
        canvas.grid(row=3, columnspan=6)
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
        self.window.bind(".", lambda x: self.set_recursion_factor(1))
        self.window.bind(",", lambda x: self.set_recursion_factor(-1))
        self.window.bind("D", lambda x: self.set_defaults())
        self.window.bind("v", lambda x: self.toggle_draw_changes_only())
        self.window.bind("<KeyPress-Up>", lambda x: self.set_spin(1))
        self.window.bind("<KeyPress-Down>", lambda x: self.set_spin(-1))
        self.window.bind("<Control-s>", lambda x: self.save_state())
        self.window.bind("<Control-l>", lambda x: self.load_state())

    def mainloop(self):
        self.window.mainloop()

    def set_seed(self):
        for i in range(self.seed_density):
            x, y = random.choice(range(self.array.shape[0])), random.choice(range(self.array.shape[1]))
            force = random.choice([1,2,3])
            self.array[x][y] = force
        self.seed = self.array.copy()

    def set_seed_density(self):

        def get_density(entry):
            try: 
                seed_density =  min(abs(int(entry.get())), 10000)
                self.seed_density = seed_density
                window.destroy()
            except ValueError: pass

        window = tkinter.Toplevel()
        window.bind('<Return>', lambda x: get_density(entry))
        tkinter.Label(window, text='Enter Seed Density (0-10000)').pack()
        entry = tkinter.Entry(window)
        entry.focus_set()
        entry.pack()
        tkinter.Button(window, text='Set Density', command=lambda: get_density(entry)).pack()

    def draw(self):

        def convert_to_canvas(x, y):
            x_pos, y_pos = x * self.block_size, y * self.block_size
            return x_pos, y_pos, x_pos+self.block_size, y_pos+self.block_size

        def draw_spreaders():
            spreaders = numpy.where(self.array == 1)
            for spreader in range(len(self.array[spreaders])):
                x, y = spreaders[0][spreader], spreaders[1][spreader]
                if self.only_draw_changes and (x, y) not in self.changed_cells: continue
                x0, y0, x1, y1 = convert_to_canvas(x, y)
                Spreader(x0, y0, x1, y1, fill="green")

        def draw_eaters():
            eaters = numpy.where(self.array == 2)
            for eater in range(len(self.array[eaters])):
                x, y = eaters[0][eater], eaters[1][eater]
                if self.only_draw_changes and (x, y) not in self.changed_cells: continue
                x0, y0, x1, y1 = convert_to_canvas(x, y)
                Eater(x0, y0, x1, y1, fill="red")

        def draw_cleaners():
            cleaners = numpy.where(self.array == 3)
            for cleaner in range(len(self.array[cleaners])):
                x, y = cleaners[0][cleaner], cleaners[1][cleaner]
                if self.only_draw_changes and (x, y) not in self.changed_cells: continue
                x0, y0, x1, y1 = convert_to_canvas(x, y)
                Cleaner(x0, y0, x1, y1, fill="yellow")


        self.clear_canvas()
        draw_spreaders()
        draw_eaters()
        draw_cleaners()
        self.draw_population_bar()

    def fast_draw(self):

        def draw_spreaders():
            positions = [coords for coords, force in self.changed_cells.items() if force == 1]
            for coords in positions:
                x, y = coords
                if self.last_states[-1][x][y] == 1: continue # dont bother replacing things with themselves
                x_pos, y_pos = x * self.block_size, y * self.block_size
                tag = f'x{x}y{y}'
                occupant = self.canvas.find_withtag(tag)
                if occupant: self.canvas.itemconfig(occupant, fill='green')
                else: Spreader(x_pos, y_pos, x_pos+self.block_size, y_pos+self.block_size, fill= "green", tags=tag)

        def draw_eaters():
            positions = [coords for coords, force in self.changed_cells.items() if force == 2]
            for coords in positions:
                x, y = coords
                if self.last_states[-1][x][y] == 2: continue # dont bother replacing things with themselves
                x_pos, y_pos = x * self.block_size, y * self.block_size
                tag = f'x{x}y{y}'
                occupant = self.canvas.find_withtag(tag)
                if occupant: self.canvas.itemconfig(occupant, fill='red')
                else: Eater(x_pos, y_pos, x_pos+self.block_size, y_pos+self.block_size, fill= "red", tags=tag)

        def draw_cleaners():
            positions = [coords for coords, force in self.changed_cells.items() if force == 3]
            for coords in positions:
                x, y = coords
                if self.last_states[-1][x][y] == 3: continue # dont bother replacing things with themselves
                x_pos, y_pos = x * self.block_size, y * self.block_size
                tag = f'x{x}y{y}'
                occupant = self.canvas.find_withtag(tag)
                if occupant: 
                    self.canvas.itemconfig(occupant, fill='yellow')
                else: Cleaner(x_pos, y_pos, x_pos+self.block_size, y_pos+self.block_size, fill= "yellow", tags=tag)

        draw_spreaders()
        draw_eaters()
        draw_cleaners()
        self.draw_population_bar()
        self.changed_cells = {}

    def iterate(self):
        self.changed_cells = {}
        rows = [x for x in range(self.array.shape[0])]
        columns = [y for y in range(self.array.shape[1])]
        if self.random_iter_order:
            random.shuffle(rows)
            random.shuffle(columns)
        for x in rows:
            for y in columns:
                force = self.array[x, y]
                #if force == 0: continue
                #if Forces.surrounded_by_same(x, y, force_id=force): continue
                condition = (((x, y) not in self.changed_cells) if self.single_change else True)
                if force == 1 and condition:
                    Spreader.iterate(x, y, self.recursion_factor)
                elif force == 2 and condition:
                    Eater.iterate(x, y, self.recursion_factor)
                elif force == 3 and condition:
                    Cleaner.iterate(x, y, self.recursion_factor)

    def append_last_states(self):
        self.last_states.append(self.array.copy())
        if len(self.last_states) > 50: 
            self.last_states.remove(self.last_states[0])

    def step(self):
        ## bound to <Right Arrow Key>
        self.append_last_states()
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
            t0 = time()
            self.step()
            t1 = time()
            #print(t1-t0)
            sleep(0 if t1-t0 > 0.18 else 0.18-(t1-t0))
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
        self.last_states = []
        setting = True if self.only_draw_changes else False
        self.only_draw_changes = False
        self.draw()
        self.only_draw_changes = setting
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
            sleep(0.1)
            self.window.update()

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

    def toggle_draw_changes_only(self):
        ## bound to <v>
        self.only_draw_changes = not self.only_draw_changes
        print(f"only draw changes = {'ON' if self.only_draw_changes else 'OFF'}")

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

    def set_recursion_factor(self, sign):
        ## bound to <>
        self.recursion_factor += sign
        if self.recursion_factor == 9: self.recursion_factor = 1
        if self.recursion_factor == 0: self.recursion_factor = 8
        self.recursion_slider.set(self.recursion_factor)
        print(f'recursion_factor = {self.recursion_factor}')

    def get_recursion_from_slider(self):
        self.recursion_factor = self.recursion_slider.get()

    def set_spin(self, sign):
        ## bound to <KeyPress-Up> <KeyPress-Down>
        simulation.spin += sign
        if self.spin == len(self.direction_options): self.spin = 0
        if self.spin < 0: self.spread_factor = len(self.direction_options) - 1
        print(f'spin = {self.spin}')

    def set_defaults(self):
        ## bound to <Shift-D>
        self.faster_eating = False
        self.recursive_eating = False
        self.random_spread = True
        self.random_iter_order = True
        self.single_change = True
        self.only_draw_changes = False
        self.direction_choices = [-1, -1, 0, 1, 1]
        self.direction_options= list(dict.fromkeys(list(permutations(self.direction_choices, 2))))
        self.spin = random.randint(0, len(simulation.direction_options)-1)
        self.recursion_factor = 1
        self.spread_factor = 1
        self.changed_cells = {}
        self.spread_slider.set(self.spread_factor)
        self.recursion_slider.set(self.recursion_factor)
        print('SETTINGS RESET')

    def new_simulation(self):
        ## bound to <Shift-N>
        self.array = self.create_array()
        self.auto_running = False
        self.loaded_simulation = False
        self.last_states = []
        self.clear_canvas()
        self.clear_population_bar()
        self.set_defaults()
        self.set_seed()
        self.draw()

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

    def surrounded_by_same(array_x_pos, array_y_pos, force_id):
        for direction in simulation.direction_options:
            x, y = direction
            if -1 < array_x_pos + x < 100 and -1 < array_y_pos + y < 100:
                if simulation.array[array_x_pos+x][array_y_pos+y] != force_id:
                    return False
        return True

    def is_valid_index(array_x_pos, x_direction, array_y_pos, y_direction):
        return 0 <= array_x_pos + x_direction < 100 and 0 <= array_y_pos + y_direction < 100

class Spreader(Forces):
    def iterate(array_x_pos, array_y_pos, recursion_factor):
        random_index = random.randint(0, len(simulation.direction_options)-1)
        for loop in range(simulation.spread_factor):
            try: x_direction, y_direction = simulation.direction_options[(random_index - loop if simulation.random_spread else simulation.spin - loop)]
            except IndexError: return
            if Forces.is_valid_index(array_x_pos, x_direction, array_y_pos, y_direction):
                target_x = array_x_pos + x_direction
                target_y = array_y_pos + y_direction
            else: continue
            if simulation.array[target_x][target_y] == 0 or simulation.array[target_x][target_y] == 3:
                simulation.array[target_x][target_y] = 1
                simulation.changed_cells[(target_x, target_y)] = 1
                if simulation.recursive_eating:
                    if simulation.recursion_factor > 0 and loop < 1:
                        if random.randint(0, recursion_factor) > 0:
                            recursion_factor -= 1
                            Spreader.iterate(target_x, target_y, recursion_factor)
            if simulation.faster_eating:
                if simulation.array[target_x][target_y] == 2:
                    simulation.array[array_x_pos][array_y_pos] = 2
                    simulation.changed_cells[(array_x_pos, array_y_pos)] = 2

class Eater(Forces):
    def iterate(array_x_pos, array_y_pos, recursion_factor):
        random_index = random.randint(0, len(simulation.direction_options)-1)
        for loop in range(simulation.spread_factor):
            try: x_direction, y_direction = simulation.direction_options[(random_index - loop if simulation.random_spread else simulation.spin - loop)]
            except IndexError: return
            if Forces.is_valid_index(array_x_pos, x_direction, array_y_pos, y_direction):
                target_x = array_x_pos + x_direction
                target_y = array_y_pos + y_direction
            else: continue
            if simulation.array[target_x][target_y] == 0:
                simulation.array[array_x_pos][array_y_pos] = 0
                simulation.changed_cells[(array_x_pos, array_y_pos)] = 0
            if simulation.array[target_x][target_y] == 0 or simulation.array[target_x][target_y] == 1:
                simulation.array[target_x][target_y] = 2
                simulation.changed_cells[(target_x, target_y)] = 2
                if simulation.recursive_eating:
                    if simulation.recursion_factor > 0 and loop < 1:
                        if random.randint(0, recursion_factor) > 0:
                            recursion_factor -= 1
                            Eater.iterate(target_x, target_y, recursion_factor)
            if simulation.faster_eating:
                if simulation.array[target_x][target_y] == 3:
                    simulation.array[array_x_pos][array_y_pos] = 3
                    simulation.changed_cells[(array_x_pos, array_y_pos)] = 3
            
class Cleaner(Forces):
    def iterate(array_x_pos, array_y_pos, recursion_factor):
        random_index = random.randint(0, len(simulation.direction_options)-1)
        for loop in range(simulation.spread_factor):
            try: x_direction, y_direction = simulation.direction_options[(random_index - loop if simulation.random_spread else simulation.spin - loop)]
            except IndexError: return
            if Forces.is_valid_index(array_x_pos, x_direction, array_y_pos, y_direction):
                target_x = array_x_pos + x_direction
                target_y = array_y_pos + y_direction
            else: continue
            if simulation.array[target_x][target_y] == 0 or simulation.array[target_x][target_y] == 2:
                simulation.array[target_x][target_y] = 3
                simulation.changed_cells[(target_x, target_y)] = 3
                if simulation.recursive_eating:
                    if simulation.recursion_factor > 0 and loop < 1:
                        if random.randint(0, recursion_factor) > 0:
                            recursion_factor -= 1
                            Cleaner.iterate(target_x, target_y, recursion_factor)
            if simulation.faster_eating:
                if simulation.array[target_x][target_y] == 1:
                    simulation.array[array_x_pos][array_y_pos] = 1
                    simulation.changed_cells[(array_x_pos, array_y_pos)] = 1

def main():
    global simulation
    simulation = Simulation()
    simulation.set_seed()
    simulation.draw()
    simulation.mainloop()

if __name__ == '__main__':
    main()