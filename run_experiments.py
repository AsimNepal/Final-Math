"""Generate all numerical results and plots. Run: python research/run_experiments.py"""
from pathlib import Path
import csv
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent))
from traffic import Edge, classic, assign, analyze_addition

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT; FIGURES = ROOT
RESULTS.mkdir(exist_ok=True); FIGURES.mkdir(exist_ok=True)


def save_csv(name, rows):
    if not rows: return
    with (RESULTS/name).open('w', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def demand_study():
    rows=[]
    for d in np.linspace(0.5, 12., 116):
        r=analyze_addition(classic(False), Edge('B','C',0,0), float(d))
        rows.append({'demand_thousands':round(float(d),5),
                     'before_minutes':round(r['before'],6),
                     'after_minutes':round(r['after'],6),
                     'change_minutes':round(r['change'],6),
                     'optimal_minutes':round(r['optimal'],6),
                     'price_of_anarchy':round(r['poa'],6)})
    save_csv('demand_sweep.csv', rows)
    x=[r['demand_thousands'] for r in rows]
    fig,ax=plt.subplots(figsize=(8,4.8))
    ax.plot(x,[r['before_minutes'] for r in rows],label='Before road')
    ax.plot(x,[r['after_minutes'] for r in rows],label='After road (UE)')
    ax.plot(x,[r['optimal_minutes'] for r in rows],label='After road (system optimum)',linestyle='--')
    ax.axvspan(3,9,alpha=.12,label='Paradox: 3 < demand < 9 thousand')
    ax.set(xlabel='Demand (thousands of drivers)',ylabel='Mean travel time (minutes)',title='Traffic demand and Braess’s paradox')
    ax.legend(fontsize=8); fig.tight_layout();fig.savefig(FIGURES/'demand_sweep.png',dpi=180);plt.close(fig)
    return rows


def capacity_study():
    rows=[]
    for k in range(30,201):
        r=analyze_addition(classic(False,k), Edge('B','C',0,0), 4.)
        rows.append({'k':k,'before_minutes':round(r['before'],6),
                     'after_minutes':round(r['after'],6),
                     'change_minutes':round(r['change'],6),
                     'price_of_anarchy':round(r['poa'],6)})
    save_csv('capacity_sweep.csv',rows)
    fig,ax=plt.subplots(figsize=(8,4.8))
    ax.plot([r['k'] for r in rows],[r['change_minutes'] for r in rows])
    ax.axhline(0,color='gray',linewidth=1)
    ax.axvspan(4000/90,6000/45,alpha=.12,label='Analytical paradox interval')
    ax.set(xlabel='Road parameter k (vehicles)',ylabel='Change in mean time (minutes)',title='When an added road makes travel worse')
    ax.legend();fig.tight_layout();fig.savefig(FIGURES/'capacity_sweep.png',dpi=180);plt.close(fig)
    return rows


def layered_network(seed, layers=3, width=2):
    """Small directed layered network with a guaranteed origin-destination path.

    Candidate roads connect earlier layers to later layers; no cycles.
    All parameters are synthetic, not estimates of real roads.
    """
    rng=np.random.default_rng(seed)
    levels=[['A']]+[[f'L{i}_{j}' for j in range(width)] for i in range(layers)]+[['D']]
    edges=[]
    for i in range(len(levels)-1):
        for u in levels[i]:
            for v in levels[i+1]:
                edges.append(Edge(u,v,float(rng.uniform(3,25)),float(rng.uniform(2,22))))
    # Add an unconnected shortcut candidate skipping one level.
    i=int(rng.integers(0,len(levels)-2))
    u=levels[i][int(rng.integers(len(levels[i])))]
    v=levels[i+2][int(rng.integers(len(levels[i+2])))]
    candidate=Edge(u,v,float(rng.uniform(0,12)),float(rng.uniform(0,8)))
    return edges,candidate,'A','D'


def larger_network_study(n=24):
    rows=[]
    cases=[]
    for seed in range(n):
        edges,added,source,target=layered_network(seed)
        cases.append(('random_layered',seed,edges,added,source,target))
        # A Braess motif embedded inside a larger graph. The added outer
        # route is deliberately expensive; the extra downstream edges
        # are shared by all routes. This is a structural sanity check,
        # NOT an independent discovery of new paradoxical networks.
        rng=np.random.default_rng(seed+1000)
        edges2=classic(False,k=float(rng.uniform(75,125))) + [
            Edge('A','X',60.,0.), Edge('X','D',60.,0.),
            Edge('D','E',float(rng.uniform(2,8)),float(rng.uniform(0,2))),
            Edge('E','F',float(rng.uniform(2,8)),0.)]
        cases.append(('embedded_braess',seed,edges2,Edge('B','C',0.,0.),'A','F'))
    for family,seed,edges,added,source,target in cases:
        for d in (1.,2.,4.,6.):
            r=analyze_addition(edges,added,d,source,target)
            rows.append({'family':family,'seed':seed,'nodes':len({e.u for e in edges}|{e.v for e in edges}),
                         'base_edges':len(edges),'demand_thousands':d,
                         'new_edge':f'{added.u}->{added.v}',
                         'before_minutes':round(r['before'],5),
                         'after_minutes':round(r['after'],5),
                         'change_minutes':round(r['change'],5),
                         'optimal_minutes':round(r['optimal'],5),
                         'price_of_anarchy':round(r['poa'],5),
                         'paradox':int(r['change']>1e-3)})
    save_csv('larger_networks.csv',rows)
    fig,ax=plt.subplots(figsize=(8,4.8))
    for d in (1.,2.,4.,6.):
        vals=[r['change_minutes'] for r in rows if r['demand_thousands']==d]
        ax.scatter([d]*len(vals),vals,alpha=.6,s=18)
    ax.axhline(0,color='gray',linewidth=1)
    ax.set(xlabel='Demand (thousands of drivers)',ylabel='Change after adding a road (minutes)',title='Synthetic networks: added-road effects')
    fig.tight_layout();fig.savefig(FIGURES/'larger_networks.png',dpi=180);plt.close(fig)
    return rows


def main():
    demand_study();capacity_study();rows=larger_network_study()
    classic_case=analyze_addition(classic(False),Edge('B','C',0,0),4.)
    n_bad=sum(r['paradox'] for r in rows)
    by_family={name:(sum(r['paradox'] for r in rows if r['family']==name),sum(r['family']==name for r in rows)) for name in ('random_layered','embedded_braess')}
    summary=f'''# Computed results (generated, not field data)\n\nClassic four-node network at demand 4,000:\n\n- Mean travel time before adding road: {classic_case['before']:.4f} minutes\n- User equilibrium after adding road: {classic_case['after']:.4f} minutes\n- System-optimal mean time after adding road: {classic_case['optimal']:.4f} minutes\n- Price of anarchy after adding road: {classic_case['poa']:.6f}\n\nSynthetic networks: {n_bad} paradox cases out of {len(rows)} network-demand scenarios ({100*n_bad/len(rows):.1f}%).\n\nBy family: {by_family}.\n\nThis proportion describes only the specific seeded synthetic generator, parameter distributions, demand levels, and candidate-edge rule used in this code. It is **not** an estimate for real road networks or for all possible networks.\n\nSee the CSV files and charts for individual outcomes.\n'''
    (RESULTS/'RESULTS_SUMMARY.md').write_text(summary)
    print(summary)

if __name__=='__main__': main()
