from gui import Gui

n = 10
p = .5
SIMS = 100


# creates default scenario of ten coin flips
def build_coin():
	coin = Gui(n, p)
	coin.show()


def main():
	build_coin()


if __name__ == '__main__':
	main()


