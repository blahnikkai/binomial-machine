import math
import random
import numpy as np
import scipy.stats as st
from statistics import NormalDist


# create a nomral approximation for the binomial distribution
# with n trials and p probability of success per trial
def normal(n: int, p: float):
	if n < 1:
		raise ValueError('Number of trials (n) must be greater than 0')
	if not (0 <= p <= 1):
		raise ValueError('Probability (p) must be between 0 and 1 inclusive')

	mu = n * p
	sigma = math.sqrt(n * p * (1 - p))
	# x values range from z score of -3 to 3, with 100 values
	x = np.linspace(mu - 3 * sigma, mu + 3 * sigma, 100)
	# return x and associated y values (probability density function)
	return x, st.norm.pdf(x, mu, sigma)


# recursive definition
def choose(n: int, k: int) -> int:
	if k == 0:
		return 1
	else:
		return (n * choose(n - 1, k - 1)) // k


# simulates random event
# chance is float from 0 to 1, probability of returning true
def percent_chance(chance: float) -> bool:
	return random.random() < chance


# represents a binomial distribution
class Binomial(object):
	# construct a binomial distribution with n trials and p probability of success for each trial
	def __init__(self, n, p):
		self.n = n
		self.p = p

		self.exact_distribution = {}
		self.approximate_count_distribution = {}
		self.approximate_freq_distribution = {}
		self.total_sims = 0
		# fill exact_distribution with actual computed probabilities
		# fill approximate_count and approximate_freq with 0 for now, no simulations run
		for i in range(n + 1):
			self.exact_distribution[i] = self.binomial(i)
			self.approximate_count_distribution[i] = 0
			self.approximate_freq_distribution[i] = 0

	# calculates the exact binomial distribution probability as a decimal
	def binomial(self, x: int) -> float:
		return choose(self.n, x) * pow(self.p, x) * pow(1 - self.p, self.n - x)

	# calculates cumulative probabilities for all values equal to,
	# less than, less than or equal to, greater than, and greater than or equal to
	def binomial_full(self, x: int) -> dict:
		full_dict = {
			'=': 0,
			'<': 0,
			'<=': 0,
			'>': 0,
			'>=': 0
		}
		for key in full_dict.keys():
			full_dict[key] = self.binomial_custom(x, key)
		return full_dict

	# calculates different cumulative binomial distribution probabilities based on the selected mode
	# mode is inequality symbol specifying what values should be accumulated
	def binomial_custom(self, x: int, mode: str) -> float:
		total = 0
		if mode == '=':
			return self.binomial(x)

		for i in range(x, -1, -1):
			total += self.binomial(i)
		if mode == '<=':
			return total
		if mode == '>':
			return 1 - total
		if mode == '<':
			return total - self.binomial(x)
		if mode == '>=':
			return 1 - total + self.binomial(x)
		raise ValueError('Invalid mode selected')

	# calculates cumulative probabliity between two values
	def binomial_cdf(self, left: int, right: int) -> float:
		print(f'{left=}, {right=}')
		if left > right:
			raise ValueError('Left must be less than or equal to right')
		total = 0
		for x in range(left, right+1):
			total += self.binomial(x)
		return total

	# calculates normal approximation for cumulative probability between two values
	def normal_cdf(self, left: float, right: float) -> float:
		mu = self.n * self.p
		sigma = math.sqrt(self.n * self.p * (1 - self.p))
		r_z = (right - mu) / sigma
		l_z = (left - mu) / sigma
		return NormalDist().cdf(r_z) - NormalDist().cdf(l_z)

	# simulate sim_num binomial trials
	def add_sims(self, sim_num: int) -> None:
		self.total_sims += sim_num
		for sim in range(sim_num):
			# do one simulation
			x = 0
			for i in range(self.n):
				if percent_chance(self.p):
					x += 1
			self.approximate_count_distribution[x] += 1
		for x in range(self.n + 1):
			self.approximate_freq_distribution[x] = self.approximate_count_distribution[x] / self.total_sims

	# reset simulations to 0
	def clear_sims(self) -> None:
		self.total_sims = 0
		for x in range(self.n+1):
			self.approximate_count_distribution[x] = 0
			self.approximate_freq_distribution[x] = 0
