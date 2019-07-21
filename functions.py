from math import exp
from enum import Enum
from typing import Tuple, NamedTuple, Generator

from settings import Settings
from db import DatabaseHolder


class Mode(Enum):
    IMPULSE = 1
    PAUSE = 2


class Constants(NamedTuple):
    L: float
    F: float
    S1: float
    S2: float
    S3: float


Tuple3float = Tuple[float, float, float]


def calculate_imp(
        input_dat: Tuple3float,
        consts: Constants,
        ranges: Tuple3float,
) -> Tuple3float:
    x, y, z = input_dat
    L, F, S1, S2, S3 = consts.L, consts.F, consts.S1, consts.S2, consts.S3

    x0, y0, z0 = x, y, z
    for t in arange(*ranges):
        ds12 = S1 - S2
        exp_s1ft = exp(-S1 * F * t)
        exp_lmbt = exp(-L * t)
        exp_fs3t = exp(-F * S3 * t)

        lz_1 = exp_s1ft / (L - S1 * F) / (F * S3 - S1 * F)
        lz_2 = exp_lmbt / (S1 * F - L) / (F * S3 - L)
        lz_3 = exp_fs3t / (S1 * F - S3 * F) / (L - S3 * F)

        x_n = x0 * exp_s1ft
        y_n = (x0 * F * ds12) / (L - F * S1) * (exp_s1ft - exp_lmbt) + y0 * exp_lmbt
        z_n = x0 * F * ds12 * L * sum((lz_1, lz_2, lz_3)) + z0 * exp_fs3t

        x, y, z = x_n, y_n, z_n
    return x, y, z


def calculate_borders(
        input_dat: Tuple3float,
        consts: Constants,
        ranges: Tuple3float,
        db: DatabaseHolder,
) -> None:
    mode_lengths = {
        Mode.IMPULSE: Settings.impulse,
        Mode.PAUSE: Settings.pause,
    }

    L, F, S1, S2, S3 = consts.L, consts.F, consts.S1, consts.S2, consts.S3

    current_mode = Mode.IMPULSE
    x, y, z = input_dat
    t, t_max, _ = ranges
    data_to_push = list()
    chunk_size = Settings.chank_size

    while t < t_max:
        t += mode_lengths[current_mode]
        if current_mode == Mode.IMPULSE:
            ds12 = S1 - S2
            exp_s1ft = exp(-S1 * F * t)
            exp_lmbt = exp(-L * t)
            exp_fs3t = exp(-F * S3 * t)

            v1 = L * (exp(-S1*F*t) - exp(-S3*F*t)) + S3*F*(exp(-S3*F*t) + exp(-L*t)) - S1*F*(exp(-L*t) + exp(-S1*F*t))
            v2 = (S3*F - S1*F)*(L - S1*F)*(L - S3*F)

            x_n = x * exp_s1ft
            y_n = (x * F * ds12) / (L - F * S1) * (exp_s1ft - exp_lmbt) + y * exp_lmbt
            z_n = x * F * ds12 * L * v1 / v2 + z * exp_fs3t

            x, y, z = x_n, y_n, z_n
        else:
            exp_lmbt = exp(-L * t)
            y_n = y * exp_lmbt
            z_n = z + y_n * (1 - exp_lmbt)
            y, z = y_n, z_n

        data_to_push.append((x, y, z, t, current_mode == Mode.IMPULSE))

        if len(data_to_push) >= chunk_size:
            db.push(data_to_push)
            data_to_push.clear()

        current_mode = Mode.IMPULSE if current_mode == Mode.PAUSE else Mode.PAUSE


def calculate_pause(
        input_dat: Tuple3float,
        consts: Constants,
        ranges: Tuple3float,
) -> Tuple3float:
    x, y, z = input_dat
    L = consts.L

    y0, z0 = y, z
    for t in arange(*ranges):
        exp_lmbt = exp(-L * t)
        y_n = y0 * exp_lmbt
        z_n = z0 + y_n * (1 - exp_lmbt)
        y, z = y_n, z_n
    return x, y, z


def arange(
        t0: float,
        tm: float,
        td: float
) -> Generator[float, None, None]:
    t = t0
    while t < tm:
        yield t
        t += td


__all__ = ['calculate_imp', 'calculate_pause', 'arange']
