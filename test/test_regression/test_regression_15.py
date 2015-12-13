""" test_regression_15.py

Regression test for Issue #15

Copyright 2015, Mario Mulansky <mario.mulansky@gmx.net>

Distributed under the BSD License

"""

from __future__ import division

import numpy as np
from numpy.testing import assert_equal, assert_almost_equal, \
    assert_array_almost_equal

import pyspike as spk


def test_regression_15_isi():
    # load spike trains
    spike_trains = spk.load_spike_trains_from_txt("test/SPIKE_Sync_Test.txt",
                                                  edges=[0, 4000])

    N = len(spike_trains)

    dist_mat = spk.isi_distance_matrix(spike_trains)
    assert_equal(dist_mat.shape, (N, N))

    ind = np.arange(N//2)
    dist_mat = spk.isi_distance_matrix(spike_trains, ind)
    assert_equal(dist_mat.shape, (N//2, N//2))

    ind = np.arange(N//2, N)
    dist_mat = spk.isi_distance_matrix(spike_trains, ind)
    assert_equal(dist_mat.shape, (N//2, N//2))


def test_regression_15_spike():
    # load spike trains
    spike_trains = spk.load_spike_trains_from_txt("test/SPIKE_Sync_Test.txt",
                                                  edges=[0, 4000])

    N = len(spike_trains)

    dist_mat = spk.spike_distance_matrix(spike_trains)
    assert_equal(dist_mat.shape, (N, N))

    ind = np.arange(N//2)
    dist_mat = spk.spike_distance_matrix(spike_trains, ind)
    assert_equal(dist_mat.shape, (N//2, N//2))

    ind = np.arange(N//2, N)
    dist_mat = spk.spike_distance_matrix(spike_trains, ind)
    assert_equal(dist_mat.shape, (N//2, N//2))


def test_regression_15_sync():
    # load spike trains
    spike_trains = spk.load_spike_trains_from_txt("test/SPIKE_Sync_Test.txt",
                                                  edges=[0, 4000])

    N = len(spike_trains)

    dist_mat = spk.spike_sync_matrix(spike_trains)
    assert_equal(dist_mat.shape, (N, N))

    ind = np.arange(N//2)
    dist_mat = spk.spike_sync_matrix(spike_trains, ind)
    assert_equal(dist_mat.shape, (N//2, N//2))

    ind = np.arange(N//2, N)
    dist_mat = spk.spike_sync_matrix(spike_trains, ind)
    assert_equal(dist_mat.shape, (N//2, N//2))


if __name__ == "__main__":
    test_regression_15_isi()
    test_regression_15_spike()
    test_regression_15_sync()
