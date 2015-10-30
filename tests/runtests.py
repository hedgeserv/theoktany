#!/usr/bin/env python

import sys
import unittest

from tests.mb_wrapper import MountebankProcess


def main():
    # start mountebank
    mb_proc = MountebankProcess()
    try:
        print('Starting mountebank...')
        mb_proc.start()
        print('Mountebank started.')
        sys.stdout.flush()
    except Exception as err:
        print(err)
        print("We'll try to run the tests anyway, but no promises.")

    # automatically discover tests
    suite = unittest.TestLoader().discover('.')
    # run tests
    unittest.TextTestRunner().run(suite)

    if mb_proc.is_running():
        sys.stdout.flush()
        try:
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
