import tkinter
import numpy
import random
import time

class Simulation():

    def __init__(self):
        self.array            = numpy.zeros((100, 100), dtype=numpy.int8)
        self.height           = 500
        self.width            = 500
        self.window           = Simulation.create_window()
        self.canvas           = Simulation.create_canvas(self)
        self.block_size       = 5
        self.last_states      = []
        self.memory           = []
        self.auto_running     = False
        self.two_step         = False
        self.bind_keys()
        self.create_buttons()
                    
    def create_window():
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

    def bind_keys(self):
        self.window.bind("<KeyPress-Right>", lambda x: self.step())
        self.window.bind("<KeyPress-Left>", lambda x: self.back())
        self.window.bind("<space>", lambda x: self.auto_run())
        self.window.bind("b", lambda x: self.auto_back())
        self.window.bind("R", lambda x: self.new_simulation())
        self.window.bind("2", lambda x: self.two_steps_one_back())
        self.window.bind("<Button-3>", lambda x: self.nuke(x))

    def mainloop(self):
        self.window.mainloop()

    def set_seed(self):
        for i in range(100):
            x, y = random.choice(range(100)), random.choice(range(100))
            self.array[x][y] = random.choice([1,2,3])

    def draw(self):
        self.clear_canvas()
        for x in range(self.array.shape[0]):
            for y in range(self.array.shape[1]):
                y_pos = y * self.block_size
                x_pos = x * self.block_size
                if self.array[x][y] == 1:
                    Spreader(x_pos, y_pos, x_pos+self.block_size, y_pos+self.block_size, fill = "green")
                elif self.array[x][y] == 2:
                    Eater(x_pos, y_pos, x_pos+self.block_size, y_pos+self.block_size, fill = "red")
                elif self.array[x][y] == 3:
                    Cleaner(x_pos, y_pos, x_pos+self.block_size, y_pos+self.block_size, fill = "yellow")

    def iterate(self):
        for x in range(self.array.shape[0]):
            for y in range(self.array.shape[1]):
                if self.array[x][y] == 1:
                    Spreader.iterate(x, y)
                elif self.array[x][y] == 2:
                    Eater.iterate(x, y)
                elif self.array[x][y] == 3:
                    Cleaner.iterate(x, y)

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
        self.two_step = False
        while self.auto_running:
            self.step()
            time.sleep(0.1)
            self.window.update()

    def auto_back(self):
        ## bound to <b>
        self.auto_running = not self.auto_running
        self.two_step = False
        while self.auto_running:
            self.back()
            time.sleep(0.1)
            self.window.update()
            if len(self.last_states) == 0: self.auto_running = False

    def two_steps_one_back(self):
        ## bound to <2>
        self.auto_running = False
        self.two_step = not self.two_step
        while self.two_step:
            self.step()
            self.window.update()
            time.sleep(0.1)
            self.step()
            self.window.update()
            time.sleep(0.1)
            self.back()

    def new_simulation(self):
        ## bound to <Shift-r>
        self.array = numpy.zeros((100, 100), dtype=numpy.int8)
        self.auto_running = False
        self.last_states = []
        self.clear_canvas()
        self.set_seed()
        self.draw()
        self.window.update()

    def nuke(self, event):
        ## bound to <Left-Click>
        nuke_radius = 10
        array_x, array_y = round((event.x)/5), round((event.y)/5)
        for row in range(array_x - nuke_radius, array_x + nuke_radius):
            for column in range(array_y - 10, array_y + 10):
                try: self.array[max(row, 0)][max(column, 0)] = 0
                except IndexError: continue
        self.draw()
        self.window.update()

class Forces():
    def __init__(self, x0, x1, y0, y1, **kwargs):
        self.rectangle = simulation.canvas.create_rectangle(x0, x1, y0, y1, **kwargs)

class Spreader(Forces):
    def iterate(array_x_pos, array_y_pos):
        x_direction, y_direction = random.choice([1,-1]), random.choice([1,-1])
        target_x  = min(array_x_pos + x_direction,99)
        target_y = min(array_y_pos + y_direction,99)
        if simulation.array[target_x][target_y] in [0,3]:
            simulation.array[target_x][target_y] = 1

class Eater(Forces):
    def iterate(array_x_pos, array_y_pos):
        x_direction, y_direction = random.choice([1,-1]), random.choice([1,-1])
        target_x  = min(array_x_pos + x_direction,99)
        target_y = min(array_y_pos + y_direction,99)
        if simulation.array[target_x][target_y] == 0:
            simulation.array[array_x_pos][array_y_pos] = 0
        if simulation.array[target_x][target_y] in [0,1]:
            simulation.array[target_x][target_y] = 2

class Cleaner(Forces):
    def iterate(array_x_pos, array_y_pos):
        x_direction, y_direction = random.choice([1,-1]), random.choice([1,-1])
        target_x  = min(array_x_pos + x_direction,99)
        target_y = min(array_y_pos + y_direction,99)
        if simulation.array[target_x][target_y] in [0,2]:
            simulation.array[target_x][target_y] = 3

def main():
    global simulation
    simulation = Simulation()
    simulation.set_seed()
    simulation.draw()
    try: simulation.mainloop()
    finally: 
        print('hai mon')
        simulation.window.quit()
if __name__ == '__main__':
    main()