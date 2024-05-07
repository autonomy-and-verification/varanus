
class Time_Store(object):

    def __new__(cls):
        if not hasattr(cls, 'instance'):
          cls.instance = super(Time_Store, cls).__new__(cls)
        return cls.instance
    def __init__(self):
        self.times = {}
        self.extras = {}
    def add_time(self, name, time):
        self.times[name] = time

    def add_extra_information(self, name, data):
        self.extras[name] = data
