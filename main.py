from enum import Enum
from argparse import ArgumentParser
from signal import signal, SIGTERM, SIGINT
from logging import getLogger, INFO, StreamHandler
from sys import stdout

from functions import calculate_imp, calculate_pause, arange
from db import DatabaseHolder, DBError
from settings import Settings


class Mode(Enum):
    IMPULSE = 1
    PAUSE = 2


MODE_LENGTHES = {
    Mode.IMPULSE: Settings.time.impulse,
    Mode.PAUSE: Settings.time.pause,
}
MODE_FUNCTIONS = {
    Mode.IMPULSE: calculate_imp,
    Mode.PAUSE: calculate_pause,
}

LOGGER = getLogger('Main')
LOGGER.addHandler(StreamHandler(stdout))
CONTINUE = True


def generate(db_holder, _):
    mode_length = Settings.time.impulse
    current_mode = Mode.IMPULSE
    x, y, z = Settings.x, Settings.y, Settings.z
    data_to_push = [(x, y, z, 0, True)]

    LOGGER.info('Start')
    for t in arange(0, Settings.time.calc, Settings.time.disc):
        if not CONTINUE:
            LOGGER.info('Halt')
            break

        if mode_length <= 0.0:
            current_mode = Mode.IMPULSE if current_mode == Mode.PAUSE else Mode.PAUSE

        nx, ny, nz = MODE_FUNCTIONS[current_mode](x, y, z, t)

        if mode_length <= 0.0:
            mode_length = MODE_LENGTHES[current_mode]
            data_to_push.append((nx, ny, nz, t, current_mode == Mode.IMPULSE))
            LOGGER.info('%f x=%f, y=%f, z=%f', t, nx, ny, nz)
            if len(data_to_push) >= Settings.general.chank_size:
                db_holder.push(data_to_push)
                data_to_push.clear()

        if current_mode == Mode.IMPULSE:
            x, y, z = nx, ny, nz

        mode_length -= Settings.time.disc
    else:
        LOGGER.info('Stop')


def degenerate(db_holder, _):
    data_to_push = list()

    last = db_holder.get_last_calculation()
    x, y, z, t0, impulse = last if last is not None else (Settings.x, Settings.y, Settings.z, 0, True)
    if not impulse:
        mode_length = Settings.time.pause
        current_mode = Mode.PAUSE
    else:
        mode_length = Settings.time.impulse
        current_mode = Mode.IMPULSE

    LOGGER.info('Start')
    for t in arange(t0, Settings.time.calc, Settings.time.disc):
        if not CONTINUE:
            LOGGER.info('Halt')
            break

        if mode_length <= 0.0:
            current_mode = Mode.IMPULSE if current_mode == Mode.PAUSE else Mode.PAUSE

        nx, ny, nz = MODE_FUNCTIONS[current_mode](x, y, z, t)

        if mode_length <= 0.0:
            mode_length = MODE_LENGTHES[current_mode]
            data_to_push.append((nx, ny, nz, t, current_mode == Mode.IMPULSE))
            LOGGER.info('%f x=%f, y=%f, z=%f', t, nx, ny, nz)
            if len(data_to_push) >= Settings.general.chank_size:
                db_holder.push(data_to_push)
                data_to_push.clear()

        if current_mode == Mode.IMPULSE:
            x, y, z = nx, ny, nz

        mode_length -= Settings.time.disc
    else:
        LOGGER.info('Stop')


def sig_handler(sig, frame):
    global CONTINUE
    CONTINUE = False


commands_list = {
    'generate': generate,
    'degenerate': degenerate,
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
