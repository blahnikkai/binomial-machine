import random
import matplotlib.pyplot as plt

# only used for testing

class Game(object):
    def __init__(self, prob_model: dict[int, float]):
        assert sum(prob_model.values()) == 1
        self.prob_model = prob_model

    def simulate_many(self, n):
        total = 0
        for i in range(n):
            total += self.simulate()
            plt.plot(i+1, total, 'r')
        plt.show()
        return total/n

    def simulate(self) -> int:
        r = random.random()
        total = 0
        for k, v in self.prob_model.items():
            total += v
            if r <= total:
                return k
        raise ValueError('how\'d you get here')

    def mean(self) -> float:
        expected = 0
        for k, v in self.prob_model.items():
            expected += k*v
        return expected
