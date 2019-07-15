from math import exp
from typing import Tuple, Union, Iterable

from settings import Settings


def add_settings(function):
    return lambda x, y, z, t: function(x, y, z, t, Settings)


@add_settings
def calculate_imp(
        x: float,
        y: float,
        z: float,
        t: float,
        p,
) -> Tuple[float, float, float]:
    """
    Функция расчета X(t), y(t), z(t) при подаче импульса
    """
    ds12 = p.S1 - p.S2
    exp_s1ft = exp(-p.S1 * p.F * t)
    exp_lmbt = exp(-p.L * t)
    exp_fs3t = exp(-p.F * p.S3 * t)

    lz_1 = exp_s1ft / (p.L - p.S1 * p.F) / (p.F * p.S3 - p.S1 * p.F)
    lz_2 = exp_lmbt / (p.S1 * p.F - p.L) / (p.F * p.S3 - p.L)
    lz_3 = exp_fs3t / (p.S1 * p.F - p.S3 * p.F) / (p.L - p.S3 * p.F)

    x_n = x * exp_s1ft
    y_n = (x * p.F * ds12) / (p.L - p.F * p.S1) * (exp_s1ft - exp_lmbt) + y * exp_lmbt
    z_n = x * p.F * ds12 * p.L * sum((lz_1, lz_2, lz_3)) + z * exp_fs3t
    return x_n, y_n, z_n


@add_settings
def calculate_pause(
        x: float,
        y: float,
        z: float,
        t: float,
        p,
) -> Tuple[float, float, float]:
    """
    Функция расчета X(t), y(t), z(t) при отсутствии импульса
    """
    exp_lmbt = exp(-p.L * t)
    y_n = y * exp_lmbt
    z_n = z + y * (1 - exp_lmbt)
    return x, y_n, z_n


def arange(
        t0: Union[float, int],
        tm: Union[float, int],
        td: Union[float, int],
) -> Iterable[float]:
    """
        float range with generator
    :param t0: start
    :param tm: end
    :param td: distance
    :return:
    """
    t = t0
    while t < tm:
        yield t
        t += td


__all__ = ['calculate_imp', 'calculate_pause', 'arange']
