from enum import Enum
from argparse import ArgumentParser
from signal import signal, SIGTERM, SIGINT
from logging import getLogger, INFO, StreamHandler
from sys import stdout

from functions import calculate_imp, calculate_pause
from db import DatabaseHolder, DBError
from settings import Settings


class Mode(Enum):
    IMPULSE = 1
    PAUSE = 2


LOGGER = getLogger('Main')
LOGGER.addHandler(StreamHandler(stdout))
CONTINUE = True


def generate(db_holder, _):

    mode_lengths = {
        Mode.IMPULSE: Settings.impulse,
        Mode.PAUSE: Settings.pause,
    }
    mode_functions = {
        Mode.IMPULSE: calculate_imp,
        Mode.PAUSE: calculate_pause,
    }

    consts = Settings.get_consts()

    current_mode = Mode.IMPULSE
    x, y, z = Settings.get_start_point()
    data_to_push = list()

    LOGGER.info('Start')
    t, t_max = 0, Settings.calc
    while t < t_max:
        x, y, z = mode_functions[current_mode](
            (x, y, z),
            consts,
            (t, t + mode_lengths[current_mode], Settings.disc),
        )
        t += mode_lengths[current_mode]

        LOGGER.info((x, y, z, t, current_mode == Mode.IMPULSE))
        data_to_push.append((x, y, z, t, current_mode == Mode.IMPULSE))

        if len(data_to_push) >= Settings.chank_size:
            db_holder.push(data_to_push)
            data_to_push.clear()

        current_mode = Mode.IMPULSE if current_mode == Mode.PAUSE else Mode.PAUSE

    if data_to_push:
        db_holder.push(data_to_push)
    LOGGER.info('Stop')


def sig_handler(sig, frame):
    global CONTINUE
    CONTINUE = False


commands_list = {
    'generate': generate,
}


if __name__ == '__main__':
    parser = ArgumentParser(description='Calculation program')
    parser.add_argument('--config', help='Path to config json file', default='secrets.json')
    parser.add_argument('command', help='Command')

    args = parser.parse_args()

    Settings.load(args.config)

    signal(SIGTERM, sig_handler)
    signal(SIGINT, sig_handler)

    try:
        db = DatabaseHolder()

        if args.command == 'migrate':
            db.create_database()
        else:
            LOGGER.setLevel(INFO)
            commands_list[args.command](db, args)
    except DBError as error:
        LOGGER.exception('Database error on calculation: {}'.format(error))
    except KeyError as error:
        LOGGER.exception('Unknown command {}'.format(args.command))
    except Exception as error:
        LOGGER.exception('Unknown error: {}'.format(error))
