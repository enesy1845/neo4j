# src/manual_test.py

from quiznexusai.utils import read_json, STATISTICS_FILE,CLASSES_FILE,QUESTIONS_DIR
import os
def manual_test():

    answers = read_json('data/statistics/statistics.json', encrypted=True)
    print(f"{answers}")

if __name__ == "__main__":
    manual_test()