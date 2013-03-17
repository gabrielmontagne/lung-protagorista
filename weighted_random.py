class WeightedRandom:
    def __init__(self, weights={}):
        self.set_weights(weights)

    def set_weights(self, weights):
        self.weights = weights
        self.recalculate_core_list()

    def recalculate_core_list(self):
        print("recalculate_core_list")
        for k in self.weights:
            print(k, self.weights[k])

    def adjust_weight(self, key, weight):
        self.weights[key] = weight
        self.recalculate_core_list()

    def random(self):
        return 1
      
