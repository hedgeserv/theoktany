import unittest

# from tests.mb_wrapper import MountebankProcess

# We cannot put this in if __name__ == "__main__" because PyCharm must import the script, so __name__ doesn't equal
# "__main__".

# automatically discover tests
suite = unittest.TestLoader().discover('.')

# start mountebank
# mb_proc = MountebankProcess()
# mb_proc.start()

# run tests
unittest.TextTestRunner().run(suite)

# mb_proc.stop()
