"""
To run tests in PyCharm:

Create a new Run/Debug configuration configuration
"""

import sys
import unittest

from tests.mb_wrapper import MountebankProcess


def main():
    # automatically discover tests
    suite = unittest.TestLoader().discover('.')

    # start mountebank, exit on failure
    mb_proc = MountebankProcess()
    try:
        print('Starting mountebank...')
        mb_proc.start()
        print('Mountebank started.')
        sys.stdout.flush()
    except Exception as err:
        print(err)
        sys.exit(-1)

    # run tests
    unittest.TextTestRunner().run(suite)

    try:
        sys.stdout.flush()
        print('Stopping mountebank...')
        return_code = mb_proc.stop()
    except Exception as err:
        print(err)
        sys.exit(-1)

    if return_code != 0:
        print('Mountebank closed with a status of {}.'.format(return_code))
    else:
        print('Mountebank stopped properly.')

if __name__ == "__main__":
    main()
