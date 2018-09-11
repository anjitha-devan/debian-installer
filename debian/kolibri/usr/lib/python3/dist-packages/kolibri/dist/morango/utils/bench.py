import time
from contextdecorator import ContextDecorator

class Timer(ContextDecorator):

    def __init__(self, message=""):
        self.message = message

    def __enter__(self):
        self.ts = time.time()
        return self

    def __exit__(self, *args):
        self.te = time.time()
        print ("Total time running {}: {} seconds".format(self.message, str(self.te-self.ts)))
