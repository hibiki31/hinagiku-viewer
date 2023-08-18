#!/usr/bin/env python3
import httpx
import json
from pprint import pprint
import time
import datetime
import sys

from test_01_startup import api_auth_validate, load_library
from test_02_library import main as test_02_library_main


args = sys.argv


def main():
    # Setup
    api_auth_validate()
    load_library()

    test_02_library_main()




if __name__ == "__main__":
    main()