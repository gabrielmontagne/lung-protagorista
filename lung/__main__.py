"""CLI for lung drill runner"""

from .q import Quiz
from .cmd import CMDQuiz
import argparse
import sys
import logging
import os



def initialize_lung_config():
    config_path = os.path.expanduser("~/.lung")
    os.makedirs(config_path, exist_ok=True)
    logging.basicConfig(filename=os.path.join(config_path, 'run.log'), level=logging.DEBUG)


def main():

    initialize_lung_config()

    logging.info('\n\nstart lung run')

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", action='store_true',
                        help='sequential (non random)', required=False)
    parser.add_argument('-f', nargs='+', required=False, help='files')
    parser.add_argument('-l', nargs='+', required=False, help='lists')
    parser.add_argument('-cc', nargs='+', required=False, help='flat, per comments')
    parser.add_argument('-m', nargs='+', type=str,
                        required=False, help='modules')
    parser.add_argument('-c', nargs='?', type=int, default=3,
                        required=False, help='correct retries')
    parser.add_argument('-qs', nargs='?', type=int, default=50,
                        required=False, help='cuestion count')
    parser.add_argument('-g', nargs='+', required=False, help='question grep')
    parser.add_argument("-lw", action='store_true',
                        help="lock weight", required=False)

    parser.add_argument('-cmd', action='store_true', help='interactive CMD')

    configuration = parser.parse_args()

    if not configuration.cmd:
        quiz = Quiz(configuration)
    else:
        quiz = CMDQuiz(configuration)

    for x in range(configuration.qs):
        quiz.ask()

    print('...done')

if __name__ == "__main__":
    main()
