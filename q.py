import argparse

class Quiz:
  def __init__(self):

    print("self", str(self))

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', nargs='*', type=file, required=True)
    configuration = parser.parse_args()
