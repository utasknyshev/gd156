from collections import namedtuple
from datetime import timedelta
from json import loads, dumps
from os.path import exists


Consts = namedtuple('Consts', [
    'L', 'F', 'S1', 'S2', 'S3',
])


class MetaSettings(type):
    def __getattr__(cls, item):
        if item in cls.conf.keys():
            return cls

        for settings_head in cls.conf.keys():
            if item in cls.conf[settings_head].keys():
                return cls.conf[settings_head].get(item)

        raise AttributeError("Attribute doesn't exist")


class Settings(metaclass=MetaSettings):
    """Class that contains main static config
    Use conf field to access settings
    """
    conf = {}
    config_path = 'secrets.json'

    @staticmethod
    def save(filename=config_path):
        with open(filename, 'w+') as configfile:
            configfile.write(dumps(Settings.conf, indent=4, sort_keys=True))

    @staticmethod
    def load(filename=config_path):
        if exists(filename):
            with open(filename, 'r') as configfile:
                conf = loads(configfile.read())
                Settings.conf.update(conf)

    @classmethod
    def get_consts(cls):
        return Consts(
            cls.L,
            cls.F,
            cls.S1,
            cls.S2,
            cls.S3,
        )

    @classmethod
    def get_start_point(cls):
        return cls.x, cls.y, cls.z


# Default values
Settings.conf = {
    'general': {
        'chank_size': 10,
    },
    'function': {
        'L': 533076,
        'x': 10e+23,
        'y': 0,
        'z': 0,
        'F': 10e+14,
        'S1': 34.7e-24,
        'S2': 25e-24,
        'S3': 7.8e-26,
    },
    'time': {
        'calc': timedelta(days=10).total_seconds(),
        'impulse': 10e-9,
        'pause': 1,
        'disc': 1e-9,
    },
    'database': {
        'host': '127.0.0.1',
        'port': 5000,
        'base': 'science',
        'user': 'postgres',
        'password': 'postgres',
        'engine': 'postgresql',
    },
}
