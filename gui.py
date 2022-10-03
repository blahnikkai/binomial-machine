import sys
from sys import platform as sys_pf

if sys_pf == 'darwin':
    import matplotlib
    matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from graph import Graph
import tkinter as tk


# north alignment, top of window
ALIGNMENT = 'n'
# window height and width
WINDOW_W = 1200
WINDOW_H = 650
# width of user entry box
ENTRY_WIDTH = 6
# cannot display a binomial distribution with n >= MAX_N
MAX_N = 73
# cannot simulate more than max sims at once
MAX_SIMS = 10**5
FONT = ('Verdana', 14)
VALID_COLOR = 'white'
# red color should be displayed if user input is invalid
ERROR_COLOR = '#ff3333'


# handles user input into entry box
class EntryHandler(object):

    # initializes entry handler
    def __init__(self, label_txt, entry_txt: str, frame, r, left_c):
        self.label = tk.Label(frame, width=6, text=label_txt, font=FONT)
        self.label.grid(row=r, column=left_c)

        self.entry = tk.Entry(frame, width=ENTRY_WIDTH, font=FONT)
        self.entry.insert(0, entry_txt)
        self.entry.grid(row=r, column=left_c+1)


# sets the entry background color to give feedback to the user when invalid numbers are entered
def set_entries_color(entry, color):
    entry.config(bg=color)


# check if user input for n (number of trials) is valid
# n must be a positive integer below MAX_N
def check_n(n: str) -> (int, str):
    try:
        n = int(n)
    except ValueError:
        return None, 'n must be an integer\n\n'
    if n <= 0:
        return None, 'n must be greater than 0\n\n'
    if n >= MAX_N:
        return None, f'n must be less than {MAX_N} for performance purposes'
    return n, ''


# check if user input for p (probability of success on an individual trial) is valid
# p must be a float between 0 and 1 inclusive, because it is a probability
def check_p(p_str: str) -> (int, str):
    try:
        p = float(p_str)
    except ValueError:
        return None, 'p must be a decimal value'
    if not (0 <= p <= 1):
        return None, 'p must be between 0 and 1 (inclusive)'
    return p, ''


# check if user input for adding simulations is valid
# sims must be a positive integer less than MAX_SIMS
def check_sims(sims_str: str):
    try:
        sims = int(sims_str)
    except ValueError:
        return 'Sims must be an integer'
    if sims <= 0:
        return 'Sims must be positive'
    if sims >= MAX_SIMS:
        return f'Sims must be less than {MAX_SIMS} for performance purposes'
    return sims


# handles BinomialMachineGUI
class Gui(object):

    # intialize gui by creating window, buttons, and matplotlib graph
    def __init__(self, n: int, p: float):
        self.create_window()
        self.create_buttons(str(n), str(p))
        self.set_graph(self.window, n, p)

    # create window titled 'The Binomial Machine' with width WINDOW_W and height WINDOW_H
    def create_window(self):
        self.window = tk.Tk()
        self.window.title('The Binomial Machine')
        self.window.geometry(f'{WINDOW_W}x{WINDOW_H}')

    # create buttons and bind functions to them
    def create_buttons(self, n_value: str, p_value: str):

        # left side
        frame_l = tk.Frame(self.window, padx=10, bg='white')
        frame_l.grid(row=0, column=0, sticky=ALIGNMENT)

        frame_l.columnconfigure(tuple(range(60)), weight=1)
        frame_l.rowconfigure(tuple(range(30)), weight=1)

        spacer_1 = tk.Label(frame_l, text='', pady=50)
        spacer_1.grid(row=0, column=0)

        entry_frame = tk.Frame(frame_l, padx=10, bg='white')
        entry_frame.grid(row=1, column=0, sticky=ALIGNMENT)
        n_handler = EntryHandler('n =', n_value, entry_frame, 0, 0)
        p_handler = EntryHandler('p =', p_value, entry_frame, 1, 0)
        enter_button = tk.Button(entry_frame, text='Enter', width=ENTRY_WIDTH, font=FONT)
        enter_button.grid(row=3, column=1)

        error_msg = tk.Message(frame_l, text='', font=FONT)
        error_msg.grid(row=2, column=0)

        spacer_2 = tk.Label(frame_l, text='', pady=75)
        spacer_2.grid(row=3, column=0)

        sim_frame = tk.Frame(frame_l, padx=10, bg='white')
        sim_frame.grid(row=4, column=0, sticky=ALIGNMENT)
        sims_handler = EntryHandler('Sims = ', '', sim_frame, 0, 0)

        add_button = tk.Button(sim_frame, text='Add sims', width=8, font=FONT)
        add_button.grid(row=1, column=1)

        clear_button = tk.Button(sim_frame, text='Clear sims', width=8, font=FONT)
        clear_button.grid(row=2, column=1)

        sims_error_msg = tk.Message(frame_l, text='', font=FONT)
        sims_error_msg.grid(row=5, column=0, sticky=ALIGNMENT)

        # right side
        frame_r = tk.Frame(self.window, padx=10, bg='white')
        frame_r.grid(row=0, column=2, sticky=ALIGNMENT)
        spacer_3 = tk.Label(frame_r, text='', pady=25)
        spacer_3.grid(row=0, column=0)
        self.full_prob_msg = tk.Message(frame_r,
                              text='Left click a bar to see advanced probabilites for a single X',
                              font=FONT, width=150)
        self.full_prob_msg.grid(row=1, column=0)
        spacer_4 = tk.Label(frame_r, text='', pady=75)
        spacer_4.grid(row=2, column=0)
        self.cum_prob_msg = tk.Message(frame_r,
                              text='Right click two bars to see the cumulative probability between them',
                              font=FONT, width=150)
        self.cum_prob_msg.grid(row=3, column=0, sticky='s')

        #
        def entry_enter(event):
            n_entry = n_handler.entry
            p_entry = p_handler.entry

            n, n_msg = check_n(n_entry.get())
            p, p_msg = check_p(p_entry.get())

            error_msg.config(text=f'{n_msg}{p_msg}')

            # if n and p are the same as current, tell user and don't change the graph
            if n == self.graph.binomial.n and p == self.graph.binomial.p:
                error_msg.config(text='n and p match current graph')
                set_entries_color(n_entry, ERROR_COLOR)
                set_entries_color(p_entry, ERROR_COLOR)
                return

            if n is not None and p is not None:
                self.set_graph(self.window, n, p)
            # for n and p, if valid, set the entry color to VALID_COLOR
            # if invalid, set entry color to ERROR_COLOR
            if n is not None:
                set_entries_color(n_entry, VALID_COLOR)
            else:
                set_entries_color(n_entry, ERROR_COLOR)
            if p is not None:
                set_entries_color(p_entry, VALID_COLOR)
            else:
                set_entries_color(p_entry, ERROR_COLOR)

        # add some number of simumlations
        def add_sims(event):
            sims_entry = sims_handler.entry
            sims_str = sims_entry.get()
            sims_out = check_sims(sims_str)

            # if user input invalid string, turn sims entry red
            if type(sims_out) is str:
                set_entries_color(sims_entry, ERROR_COLOR)
                sims_error_msg.config(text=sims_out)
            # otherwise, add that number of simulations
            else:
                sims_error_msg.config(text='')
                set_entries_color(sims_entry, VALID_COLOR)
                self.graph.add_sims(sims_out)

        # reset simulations to 0
        def clear_sims(event):
            self.graph.clear_sims()

        # ask to confirm quit
        def on_closing():
            if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
                sys.exit()

        self.window.protocol("WM_DELETE_WINDOW", on_closing)

        # bind buttons to corresponding functions
        add_button.bind('<Button-1>', add_sims)
        enter_button.bind('<Button-1>', entry_enter)
        clear_button.bind('<Button-1>', clear_sims)

    # set new graph and embed it in the tkinter window
    def set_graph(self, window, n: int, p: float):
        # print('\nNew Graph:')
        # print(f'\t{n = }')
        # print(f'\t{p = }')
        try:
            self.graph.close()
        except AttributeError:
            pass
        self.graph = Graph(n, p, self.full_prob_msg, self.cum_prob_msg)

        figure = self.graph.fig
        figure.subplots_adjust(left=0.075, bottom=0.1, right=.99, top=.9, wspace=0, hspace=.2)

        canvas = FigureCanvasTkAgg(figure, master=window)
        canvas.get_tk_widget().grid(row=0, column=1, sticky='nswe')
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=1)

    def show(self):
        self.window.mainloop()





