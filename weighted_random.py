class WeightedRandom:
    def __init__(self, weights={}):
        self.set_weights(weights)

    def set_weights(self, weights):
        self.weights = weights
        self.recalculate_core_list()

    def recalculate_core_list(self):
        print("recalculate_core_list")
        total = 0
        core_list = []
        weights = self.weights
        for k in weights:
            weight = weights[k]
            core_list.append({ 'threshold': total , 'value': k })
            total = total + weight

        print(core_list, total)


    def adjust_weight(self, key, weight):
        self.weights[key] = weight
        self.recalculate_core_list()

    def random(self):
        return 1
      
