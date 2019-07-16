from math import exp


def calculate_imp(input_dat, consts, ranges):
    x, y, z = input_dat
    L, F, S1, S2, S3 = consts.L, consts.F, consts.S1, consts.S2, consts.S3

    for t in arange(*ranges):
        ds12 = S1 - S2
        exp_s1ft = exp(-S1 * F * t)
        exp_lmbt = exp(-L * t)
        exp_fs3t = exp(-F * S3 * t)

        lz_1 = exp_s1ft / (L - S1 * F) / (F * S3 - S1 * F)
        lz_2 = exp_lmbt / (S1 * F - L) / (F * S3 - L)
        lz_3 = exp_fs3t / (S1 * F - S3 * F) / (L - S3 * F)

        x_n = x * exp_s1ft
        y_n = (x * F * ds12) / (L - F * S1) * (exp_s1ft - exp_lmbt) + y * exp_lmbt
        z_n = x * F * ds12 * L * sum((lz_1, lz_2, lz_3)) + z * exp_fs3t

        x, y, z = x_n, y_n, z_n
    return x, y, z


def calculate_pause(input_dat, consts, ranges):
    x, y, z = input_dat
    L = consts.L

    for t in arange(*ranges):
        exp_lmbt = exp(-L * t)
        y_n = y * exp_lmbt
        z_n = z + y * (1 - exp_lmbt)
        y, z = y_n, z_n
    return x, y, z


def arange(t0, tm, td):
    t = t0
    while t < tm:
        yield t
        t += td


__all__ = ['calculate_imp', 'calculate_pause', 'arange']
