# Global setup functions need to be defined in this file

import os
import sys


RUN_TEST_DIR = os.path.abspath(os.path.dirname(__file__))
os.chdir(RUN_TEST_DIR)

sys.path.append(RUN_TEST_DIR)
