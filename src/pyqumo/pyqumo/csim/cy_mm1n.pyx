# distutils: sources = pyqumo/csim/c_src/mm1n.cpp
# distutils: language = c++
import numpy as np
from libcpp.vector cimport vector
from pyqumo.csim.mm1n cimport cResults, cSimulateMm1n, cStatistics
from pyqumo.sim.helpers import Statistics
from pyqumo.sim.gg1 import Results
from pyqumo.random import CountableDistribution


cdef vector_asarray(vector[double] vect):
    cdef int n = vect.size()
    ret = np.zeros(n)
    for i in range(n):
        ret[i] = vect[i]
    return ret


cdef _build_statistics(cStatistics *cs):
    return Statistics(avg=cs.avg, std=cs.std, var=cs.var, count=cs.count)


cdef _build_results(cResults *cr):
    results = Results()
    results.system_size = CountableDistribution(vector_asarray(cr.systemSize.pmf))
    results.queue_size = CountableDistribution(vector_asarray(cr.queueSize.pmf))
    results.busy = CountableDistribution(vector_asarray(cr.busy.pmf))
    results.loss_prob = cr.lossProb
    results.departures = _build_statistics(&cr.departures)
    results.response_time = _build_statistics(&cr.responseTime)
    results.wait_time = _build_statistics(&cr.waitTime)
    return results


cdef call_simulate_mm1n(double arrival_rate, double service_rate,
                        int queue_capacity, int max_packets):
    cdef cResults *c_ret = cSimulateMm1n(
        arrival_rate, service_rate, queue_capacity, max_packets)
    result: Results = _build_results(c_ret)
    del c_ret
    return result


def simulate_mm1n(
        arrival_rate: float,
        service_rate: float,
        queue_capacity: int,
        max_packets: int = 100000
) -> Results:
    """
    Wrapper for C++ implementation of M/M/1/N model.

    Returns results in the same dataclass as defined for G/G/1 model
    in `pyqumo.sim.gg1.Results`.

    Parameters
    ----------
    arrival_rate : float
    service_rate : float
    queue_capacity : int
    max_packets : int, optional
        By default 100'000

    Returns
    -------
    results : Results
    """
    return call_simulate_mm1n(
        arrival_rate,
        service_rate,
        queue_capacity,
        max_packets
    )