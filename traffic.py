"""Reproducible static traffic assignment with affine edge latencies.

Flow units: thousands of vehicles. Time units: minutes.
UE minimizes Beckmann potential; SO minimizes total system travel time.
Networks are directed acyclic graphs (DAGs), with enumerated simple paths.
"""
from dataclasses import dataclass
import numpy as np
from scipy.optimize import minimize

@dataclass(frozen=True)
class Edge:
    u: str
    v: str
    a: float  # free-flow minutes
    b: float  # minutes per thousand vehicles


def paths(edges, source='A', target='D', max_paths=1000):
    adjacency = {}
    for i, e in enumerate(edges):
        adjacency.setdefault(e.u, []).append((e.v, i))
    out = []
    def dfs(node, visited, used):
        if node == target:
            out.append(tuple(used))
            if len(out) > max_paths:
                raise ValueError('Too many paths; reduce network size')
            return
        for nxt, idx in adjacency.get(node, []):
            if nxt not in visited:
                dfs(nxt, visited | {nxt}, used + [idx])
    dfs(source, {source}, [])
    if not out:
        raise ValueError('No path from origin to destination')
    return out


def assign(edges, demand=4., source='A', target='D', mode='ue'):
    """Return path flows, edge flows, total time and mean time.

    mode='ue' is Wardrop user equilibrium for separable, nondecreasing
    affine latencies; mode='so' minimizes system travel time.
    """
    if demand <= 0: raise ValueError('Demand must be positive')
    if mode not in ('ue', 'so'): raise ValueError('mode must be ue or so')
    pp = paths(edges, source, target)
    R = np.zeros((len(edges), len(pp)))
    for j, path in enumerate(pp):
        for i in path: R[i, j] = 1.
    a = np.array([e.a for e in edges], dtype=float)
    b = np.array([e.b for e in edges], dtype=float)
    if np.any(b < 0) or np.any(a < 0):
        raise ValueError('Only nonnegative affine latency coefficients supported')
    def obj(x):
        f = R @ x
        return float(a @ f + (0.5 if mode == 'ue' else 1.) * np.dot(b, f*f))
    def grad(x):
        f = R @ x
        return R.T @ (a + (1. if mode == 'ue' else 2.) * b * f)
    starts = [np.full(len(pp), demand/len(pp))]
    for j in range(len(pp)):
        z = np.zeros(len(pp)); z[j] = demand; starts.append(z)
    best = None
    for x0 in starts:
        res = minimize(obj, x0, jac=grad, method='SLSQP',
                       bounds=[(0., demand)]*len(pp),
                       constraints=[{'type':'eq', 'fun':lambda x: np.sum(x)-demand,
                                     'jac':lambda x: np.ones(len(x))}],
                       options={'ftol':1e-11, 'maxiter':1500})
        if res.success and (best is None or res.fun < best.fun): best = res
    if best is None: raise RuntimeError('Optimizer did not converge')
    x = np.maximum(best.x, 0.)
    f = R @ x
    latency = a + b*f
    total = float(f @ latency)
    path_times = R.T @ latency
    if mode == 'ue':
        used = x > 1e-5
        # Numerical Wardrop check: used paths are within tolerance of shortest.
        if np.any(path_times[used] > min(path_times) + 2e-3):
            raise RuntimeError('Wardrop equilibrium check failed')
    return {'path_flows':x, 'edge_flows':f, 'paths':pp,
            'mean_minutes':total/demand, 'total_thousand_driver_minutes':total,
            'path_times':path_times, 'potential':float(best.fun)}


def classic(with_link=True, k=100.):
    """Four-node Braess network. k is measured in vehicles."""
    edges = [Edge('A','B',0.,1000./k), Edge('B','D',45.,0.),
             Edge('A','C',45.,0.), Edge('C','D',0.,1000./k)]
    if with_link: edges.append(Edge('B','C',0.,0.))
    return edges


def analyze_addition(before, added, demand, source='A', target='D'):
    old = assign(before, demand, source, target, 'ue')
    after = assign(before+[added], demand, source, target, 'ue')
    optimal = assign(before+[added], demand, source, target, 'so')
    return {'before':old['mean_minutes'], 'after':after['mean_minutes'],
            'change':after['mean_minutes']-old['mean_minutes'],
            'optimal':optimal['mean_minutes'],
            'poa':after['mean_minutes']/optimal['mean_minutes'],
            'ue':after, 'so':optimal}
