import numpy as np
np.random.seed(1)

# non-linearities
def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def sigmoid_deriv(x):
    return x * (1 - x)

# parameters
alpha = 0.1

# trainin
X = np.array(
    [
        [0, 0, 1],
        [0, 1, 1],
        [1, 0, 1],
        [1, 1, 1]
    ]
)
y = np.array([[0, 1, 1, 0]]).T

# initialize weights
syn0 = 2 * np.random.random((3, 4)) - 1
syn1 = 2 * np.random.random((4, 1)) - 1

# train loop drive
for j in range(6000):

    # forward pass
    l0 = X
    l1 = sigmoid(np.dot(l0, syn0))
    l2 = sigmoid(np.dot(l1, syn1))

    # back-prop calculation
    l2_error = y - l2
    l2_delta = l2_error * sigmoid_deriv(l2)
    l1_error = np.dot(l2_delta, syn1.T)
    l1_delta = l1_error * sigmoid_deriv(l1)

    # adjust weights
    syn1 += alpha * np.dot(l1.T, l2_delta)
    syn0 += alpha * np.dot(l0.T, l1_delta)

    # display error every 10000
    # print error
    if j % 10000 == 0:
        print('Error:', np.mean(np.abs(l2_error)))

# display las prediction
print('last prediction', l2)
