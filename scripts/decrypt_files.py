# src/manual_test.py

from quiznexusai.utils import read_json, STATISTICS_FILE,CLASSES_FILE,QUESTIONS_DIR
import os
/*************  ✨ Codeium Command 🌟  *************/
def manual_test():
    """
    Manually tests the code to ensure it works correctly.

    This function is for testing purposes only and should not be called in production.
    """
    # Read the encrypted file
    answers = read_json('data/statistics/statistics.json', encrypted=True)

    # Print the contents of the file
    print(f"Decrypted answers: {answers}")
    print(f"{answers}")
/******  b7fb365f-c872-448e-bc83-3d1796171de6  *******/

if __name__ == "__main__":
    manual_test()



