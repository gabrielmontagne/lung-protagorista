#!/usr/bin/env python3

import random

class WeightedRandom:
    def __init__(self, weights={}):
        self.set_weights(weights)

    def set_weights(self, weights):
        self.weights = weights
        self.recalculate_core_list()

    def recalculate_core_list(self):
        total = 0
        core_list = []
        weights = self.weights
        for k in weights:
            weight = weights[k]
            total = total + weight
            core_list.append({ 'threshold': total , 'value': k })

        self.core_list = core_list
        self.total = total

    def adjust_weight(self, key, weight):
        self.weights[key] = weight
        self.recalculate_core_list()

    def random(self):
        index = random.random() * self.total
        for item in self.core_list:
            if index < item['threshold']:
                return item['value']
