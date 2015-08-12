# Module containing functions to compute multivariate spike delay asymmetry
# Copyright 2015, Mario Mulansky <mario.mulansky@gmx.net>
# Distributed under the BSD License

import numpy as np
from math import exp
from functools import partial
# import pyspike
from pyspike import DiscreteFunc
from pyspike.generic import _generic_profile_multi


############################################################
# spike_delay_asymmetry_profile
############################################################
def spike_delay_asymmetry_profile(spike_train1, spike_train2, max_tau=None):
    """ Computes the spike delay asymmetry profile A(t) of the two given
    spike trains. Returns the profile as a DiscreteFunction object.

    :param spike_train1: First spike train.
    :type spike_train1: :class:`pyspike.SpikeTrain`
    :param spike_train2: Second spike train.
    :type spike_train2: :class:`pyspike.SpikeTrain`
    :param max_tau: Maximum coincidence window size. If 0 or `None`, the
                    coincidence window has no upper bound.
    :returns: The spike-distance profile :math:`S_{sync}(t)`.
    :rtype: :class:`pyspike.function.DiscreteFunction`

    """
    # check whether the spike trains are defined for the same interval
    assert spike_train1.t_start == spike_train2.t_start, \
        "Given spike trains are not defined on the same interval!"
    assert spike_train1.t_end == spike_train2.t_end, \
        "Given spike trains are not defined on the same interval!"

    # cython implementation
    try:
        from cython.cython_directionality import \
            spike_delay_asymmetry_profile_cython as \
            spike_delay_asymmetry_profile_impl
    except ImportError:
        raise NotImplementedError()
#         if not(pyspike.disable_backend_warning):
#             print("Warning: spike_distance_cython not found. Make sure that \
# PySpike is installed by running\n 'python setup.py build_ext --inplace'!\n \
# Falling back to slow python backend.")
#         # use python backend
#         from cython.python_backend import coincidence_python \
#             as coincidence_profile_impl

    if max_tau is None:
        max_tau = 0.0

    times, coincidences, multiplicity \
        = spike_delay_asymmetry_profile_impl(spike_train1.spikes,
                                             spike_train2.spikes,
                                             spike_train1.t_start,
                                             spike_train1.t_end,
                                             max_tau)

    return DiscreteFunc(times, coincidences, multiplicity)


############################################################
# spike_delay_asymmetry
############################################################
def spike_delay_asymmetry(spike_train1, spike_train2,
                          interval=None, max_tau=None):
    """ Computes the overall spike delay asymmetry value for two spike trains.
    """
    if interval is None:
        # distance over the whole interval is requested: use specific function
        # for optimal performance
        try:
            from cython.cython_directionality import \
                spike_delay_asymmetry_cython as spike_delay_impl
            if max_tau is None:
                max_tau = 0.0
            c, mp = spike_delay_impl(spike_train1.spikes,
                                     spike_train2.spikes,
                                     spike_train1.t_start,
                                     spike_train1.t_end,
                                     max_tau)
            return c
        except ImportError:
            # Cython backend not available: fall back to profile averaging
            raise NotImplementedError()
            # return spike_sync_profile(spike_train1, spike_train2,
            #                           max_tau).integral(interval)
    else:
        # some specific interval is provided: not yet implemented
        raise NotImplementedError()


############################################################
# spike_delay_asymmetry_profile_multi
############################################################
def spike_delay_asymmetry_profile_multi(spike_trains, indices=None,
                                        max_tau=None):
    """ Computes the multi-variate spike delay asymmetry profile for a set of
    spike trains. For each spike in the set of spike trains, the multi-variate
    profile is defined as the sum of asymmetry values divided by the number of
    spike trains pairs involving the spike train of containing this spike,
    which is the number of spike trains minus one (N-1).

    :param spike_trains: list of :class:`pyspike.SpikeTrain`
    :param indices: list of indices defining which spike trains to use,
                    if None all given spike trains are used (default=None)
    :type indices: list or None
    :param max_tau: Maximum coincidence window size. If 0 or `None`, the
                    coincidence window has no upper bound.
    :returns: The multi-variate spike sync profile :math:`<S_{sync}>(t)`
    :rtype: :class:`pyspike.function.DiscreteFunction`

    """
    prof_func = partial(spike_delay_asymmetry_profile, max_tau=max_tau)
    average_prof, M = _generic_profile_multi(spike_trains, prof_func,
                                             indices)
    # average_dist.mul_scalar(1.0/M)  # no normalization here!
    return average_prof


############################################################
# spike_delay_asymmetry_matrix
############################################################
def spike_delay_asymmetry_matrix(spike_trains, indices=None,
                                 interval=None, max_tau=None):
    """ Computes the spike delay asymmetry matrix for the given spike trains.
    """
    if indices is None:
        indices = np.arange(len(spike_trains))
    indices = np.array(indices)
    # check validity of indices
    assert (indices < len(spike_trains)).all() and (indices >= 0).all(), \
        "Invalid index list."
    # generate a list of possible index pairs
    pairs = [(indices[i], j) for i in range(len(indices))
             for j in indices[i+1:]]

    distance_matrix = np.zeros((len(indices), len(indices)))
    for i, j in pairs:
        d = spike_delay_asymmetry(spike_trains[i], spike_trains[j],
                                  interval, max_tau=max_tau)
        distance_matrix[i, j] = d
        distance_matrix[j, i] = -d
    return distance_matrix


############################################################
# optimal_asymmetry_order_from_D
############################################################
def optimal_asymmetry_order_from_D(D, full_output=False):
    """ finds the best sorting via simulated annealing.
    Returns the optimal permutation p and A value.
    Internal function, don't call directly! Use optimal_asymmetry_order
    instead.
    """
    N = len(D)
    A = np.sum(np.triu(D, 0))

    p = np.arange(N)

    T = 2*np.max(D)    # starting temperature
    T_end = 1E-5 * T   # final temperature
    alpha = 0.9        # cooling factor
    total_iter = 0
    while T > T_end:
        iterations = 0
        succ_iter = 0
        while iterations < 100*N and succ_iter < 10*N:
            # exchange two rows and cols
            ind1 = np.random.randint(N-1)
            delta_A = -2*D[p[ind1], p[ind1+1]]
            if delta_A > 0.0 or exp(delta_A/T) > np.random.random():
                # swap indices
                p[ind1], p[ind1+1] = p[ind1+1], p[ind1]
                A += delta_A
                succ_iter += 1
            iterations += 1
        total_iter += iterations
        T *= alpha   # cool down
        if succ_iter == 0:
            break
    if full_output:
        return p, A, total_iter
    else:
        return p, A


############################################################
# _optimal_asymmetry_order
############################################################
def optimal_asymmetry_order(spike_trains,  indices=None, interval=None,
                            max_tau=None, full_output=False):
    """ finds the best sorting of the given spike trains via simulated
    annealing.
    Returns the optimal permutation p and A value.
    """
    D = spike_delay_asymmetry_matrix(spike_trains, indices, interval, max_tau)
    return optimal_asymmetry_order_from_D(D, full_output)


############################################################
# reorder_asymmetry_matrix
############################################################
def reorder_asymmetry_matrix(D, p):
    N = len(D)
    D_p = np.empty_like(D)
    for n in xrange(N):
        for m in xrange(N):
            D_p[n, m] = D[p[n], p[m]]
    return D_p
