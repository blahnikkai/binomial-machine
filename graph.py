import tkinter as tk
import matplotlib.pyplot as plt
from my_stats import Binomial
from my_stats import normal


# fill colors for graph gui
# w = white
# 0 = default, 1 = hover, 2 = range selection/right click, 3 = left click
# upper colors: for actual binomial distribution
UPPER_COLORS = ['w', 'lightblue', 'cornflowerblue', 'darkblue']
# lower colors: for simulated binomial distribution
LOWER_COLORS = ['w', 'lightgreen', 'limegreen', 'darkgreen']


# selects range to view cumulative probability between lower and upper bound
def select_edge(left, right, clicked):
	if left is None:
		left = clicked
	elif right is None:
		if clicked < left:
			right = left
			left = clicked
		else:
			right = clicked
	else:
		left = None
		right = None
	return left, right


# manages mouse interaction
class MouseHandler(object):

	# initializes MouseSystem
	def __init__(self, fig, axes, bars, binomial, colors, full_prob_msg: tk.Message, cum_prob_msg: tk.Message,
	             clickable: bool):
		self.fig = fig
		self.axes = axes
		self.bars = bars
		self.binomial = binomial
		self.colors = colors
		self.clickable = clickable

		self.current_hover = None
		self.current_click = None
		self.current_left = None
		self.current_right = None

		self.full_prob_msg = full_prob_msg
		self.cum_prob_msg = cum_prob_msg

		self.annot = self.create_annot()

		self.fig.canvas.mpl_connect('motion_notify_event', self.hover)
		self.fig.canvas.mpl_connect('button_press_event', self.click)

	# creates annotation displaying probability information for values
	def create_annot(self):
		annot = self.axes.annotate('', xy=(0, 0), xytext=(0, 20), textcoords='offset points',
		                           zorder=100,
		                           bbox=dict(boxstyle='round', fc='white', ec='black', lw=.75),
		                           arrowprops=dict(arrowstyle='->'))
		annot.set_visible(False)
		return annot

	# show the annotation above selected bar
	def show_annot(self, bar_ind: int):
		bar = self.bars.patches[bar_ind]
		x = bar.get_x() + bar.get_width() / 2
		y = bar.get_y() + bar.get_height()
		self.annot.xy = (x, y)
		text = f'P(X={int(x)})\n' \
		       f' = {round(y, 5)}'
		self.annot.set_text(text)
		self.annot.set_visible(True)

	# changes individual bar's fill color according to color index for UPPER_COLORS and LOWER_COLORs
	def change_color(self, bar_ind: int, color_ind: int):
		self.bars.patches[bar_ind].set_fc(self.colors[color_ind])

	# updates bar's fill color based on state
	def update_bar_color(self, bar_ind):
		if bar_ind is None:
			return
		if bar_ind == self.current_click:
			self.change_color(bar_ind, 3)
			return
		if self.current_left is not None and self.current_right is not None and \
		   self.current_left <= bar_ind <= self.current_right:
			self.change_color(bar_ind, 2)
			return
		if bar_ind == self.current_hover:
			self.change_color(bar_ind, 1)
			return
		self.change_color(bar_ind, 0)

	# updates multiple bar colors at once
	def update_bar_color_in_range(self, left, right):
		for j in range(left, right+1):
			self.update_bar_color(j)
		self.fig.canvas.draw_idle()

	# handles mouse hover over bar
	def hover(self, event):
		vis = self.annot.get_visible()
		if event.inaxes == self.axes:
			# for every bar, check if it is the bar that is currently being hovered over (contains event)
			for i in range(len(self.bars.patches)):
				bar = self.bars.patches[i]
				cont, ind = bar.contains(event)
				if cont:
					previous = self.current_hover
					self.current_hover = i
					self.update_bar_color(previous)
					self.update_bar_color(self.current_hover)
					self.show_annot(self.current_hover)
					self.fig.canvas.draw_idle()
					return
		if vis:
			previous = self.current_hover
			self.current_hover = None
			self.update_bar_color(previous)
			self.annot.set_visible(False)
			self.fig.canvas.draw_idle()

	# handles left click event on bar
	def left_click(self, bar_ind: int):
		previous = self.current_click
		if bar_ind == self.current_click:
			bar_ind = None

		self.current_click = bar_ind
		self.update_bar_color(previous)
		self.update_bar_color(self.current_click)
		self.fig.canvas.draw_idle()

		if bar_ind is not None:
			full_dict = self.binomial.binomial_full(bar_ind)
			all_prob = ''
			# add every type of probability to the sidebar
			for key in full_dict:
				all_prob += f'P(x{key}{bar_ind}) = {round(full_dict.get(key), 5)}\n'
			self.full_prob_msg.config(text=all_prob)
		else:
			self.full_prob_msg.config(text='')

	# handles right click on bar
	def right_click(self, bar_ind: int):
		previous_l, previous_r = self.current_left, self.current_right
		self.current_left, self.current_right = select_edge(self.current_left, self.current_right, bar_ind)

		# first click, don't show anything
		if self.current_left is not None and self.current_right is None:
			return

		# clear bars
		if self.current_left is None and self.current_right is None:
			self.update_bar_color_in_range(previous_l, previous_r)
			self.cum_prob_msg.config(text='')

		# second click, color all bars between left and right (lower and upper bound), inclusive
		if self.current_left is not None and self.current_right is not None:
			self.update_bar_color_in_range(self.current_left, self.current_right)
			cum_prob = f'P({self.current_left}<=x<={self.current_right}) = {round(self.binomial.binomial_cdf(self.current_left, self.current_right), 5)}'
			cum_prob += f'\n\nNormal Approx = {round(self.binomial.normal_cdf(self.current_left-.5, self.current_right+.5), 5)}'
			print(cum_prob)
			self.cum_prob_msg.config(text=cum_prob)

	# handles generic click, calls left or right click accordingly
	def click(self, event):
		if self.clickable and event.inaxes == self.axes:
			for i, bar in enumerate(self.bars.patches):
				cont, ind = bar.contains(event)
				if cont:
					if event.button == 1:
						self.left_click(i)
						return
					elif event.button == 3:
						self.right_click(i)
						return


# Handles display of bar graphs
class Graph(object):

	# initializes bar graphs
	def __init__(self, n, p, full_prob_msg: tk.Message, cum_prob_msg: tk.Message):
		self.binomial = Binomial(n, p)
		self.full_prob_msg = full_prob_msg
		self.cum_prob_msg = cum_prob_msg

		self.create_fig()
		self.create_upper()
		self.create_lower()
		self.create_annot()

	# close figure
	def close(self):
		plt.close(self.fig)

	# create figure
	def create_fig(self):
		self.fig, (self.upper, self.lower) = plt.subplots(2, figsize=(10, 9))
		self.fig.suptitle('The Binomial Machine')

	def create_upper(self):
		# exact binomial
		self.upper_bars = self.upper.bar(self.binomial.exact_distribution.keys(),
		                               self.binomial.exact_distribution.values(),
		                               1, label='Exact Binomial Distribution',
		                               linewidth=1.5,
		                               edgecolor='b',
		                               fill=True, fc=UPPER_COLORS[0])

		# normal approximation
		x, y = normal(self.binomial.n, self.binomial.p)
		self.upper.plot(x, y, color='r', linestyle='-', label='Normal Approximation', linewidth=1.0, zorder=4)

		# create legend
		self.upper.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=2, fancybox=True, shadow=True)

		# bounds
		self.upper.set_xlim([-1, self.binomial.n + 1])
		self.upper.set_ylim([0, max(self.binomial.exact_distribution.values()) * 1.25])

	def create_lower(self):
		self.lower_bars = self.lower.bar(self.binomial.approximate_freq_distribution.keys(),
		                                 self.binomial.approximate_freq_distribution.values(),
		                                 1, 0,
		                                 label='Approximate Binomial Distribution',
		                                 linewidth=1.5,
		                                 edgecolor='green',
		                                 fill=True, fc=LOWER_COLORS[0])

		self.lower.set_ylabel('Probability')
		self.lower.set_xlabel('Successes')

		self.lower.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=2, fancybox=True, shadow=True)
		self.lower.set_xlim([-1, self.binomial.n + 1])

		# simulations annotation in upper left corner of lower bar graph showing how many simulations are being
		# displayed
		self.sims_annot = self.lower.annotate(f'Sims: {self.binomial.total_sims}', xy=(0, 0), xytext=(.02, .9),
		                                    textcoords='axes fraction',
		                                    bbox=dict(boxstyle='square', fc='white',
		                                    ec='black', lw=1), zorder=100)
		# y only ranges from 0 to 1, because it is a probability
		self.lower.set_ylim([0, 1])

	# update lower bar graph when more simulations are performed
	def update_lower(self):
		self.sims_annot.set_text(f'Sims: {self.binomial.total_sims}')
		max_height = max(self.binomial.approximate_freq_distribution.values()) * 1.25
		if max_height == 0:
			self.lower.set_ylim([0, 1])
			return
		try:
			self.lower.set_ylim([0, max_height])
		except ValueError:
			self.lower.set_ylim([0, 1])

	# create a mouse handler for each bar graph
	def create_annot(self):
		self.upper_mouse_handler = MouseHandler(self.fig, self.upper, self.upper_bars, self.binomial,
		                                        UPPER_COLORS, self.full_prob_msg, self.cum_prob_msg, True)
		self.lower_mouse_handler = MouseHandler(self.fig, self.lower, self.lower_bars, self.binomial,
		                                        LOWER_COLORS, self.full_prob_msg, self.cum_prob_msg, False)

	# perform more simulations
	def add_sims(self, sim_num):
		if sim_num == 0:
			return
		self.binomial.add_sims(sim_num)
		succ = 0
		for bar in self.lower_bars:
			bar.set_height(self.binomial.approximate_freq_distribution.get(succ))
			succ += 1
		self.update_lower()
		self.fig.canvas.draw_idle()

	# clear all simulations
	def clear_sims(self):
		self.binomial.clear_sims()
		for bar in self.lower_bars:
			bar.set_height(0)
		self.update_lower()
		self.fig.canvas.draw_idle()







