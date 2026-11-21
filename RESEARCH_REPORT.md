# Beyond Braess's Paradox: Equilibrium, Optimization, and Network Structure

**Asim Nepal · Independent applied mathematics project · November 2026**

## Research question
Under what conditions does adding a directed road increase user-equilibrium congestion, and how do traffic demand and network structure change the result?

## Scope and originality
Braess's paradox, Wardrop equilibrium, Beckmann's potential, and the price of anarchy are established research topics. The exact threshold results below are derivations for the classical four-node model, not claimed as original discoveries. The code and seeded experiments constitute a reproducible undergraduate investigation. The random networks and road times are entirely synthetic.

## Model
Every edge e has a nonnegative affine latency **t_e(f_e) = a_e + b_e f_e**, where f_e is in *thousands of drivers* and t_e is in minutes. A route flow vector x has x_p >= 0 and sum_p x_p = q. The edge flow is f = R x, with route-edge incidence matrix R.

**User equilibrium (UE):** Each used route has minimum travel time. For nondecreasing separable latencies, a UE is found by minimizing the Beckmann potential

**Phi(x) = sum_e [a_e f_e + (b_e/2) f_e^2]**

subject to flow conservation and nonnegativity.

**System optimum (SO):** Minimize total travel time

**C(x) = sum_e [a_e f_e + b_e f_e^2].**

The *price of anarchy* is C(UE)/C(SO) >= 1. The optimizer is SciPy SLSQP with analytical gradients and multiple initial conditions; it checks Wardrop's minimum-route-time condition. These are numerical approximations with a tolerance, not formal proofs for every generated network.

## Classical four-node network: exact demand thresholds

Edges A→B and C→D have time 10f (f in thousands), B→D and A→C each take 45 minutes, and the added edge B→C takes zero minutes. Total demand is q thousand drivers.

Before adding B→C, the two outer paths split equally, so

**T_before(q) = 45 + 5q.**

After adding B→C, by symmetry, three regimes follow:

- **0 < q <= 4.5:** all drivers take the middle path A→B→C→D. Then **T_after(q) = 20q**. An outer route costs 10q + 45, which is no less than 20q in this regime.
- **4.5 < q < 9:** the middle route carries **9 - q** thousand drivers; each outer route carries **q - 4.5** thousand. All three used routes take **90 minutes**.
- **q >= 9:** the middle route is unused, and the two outer paths split evenly. **T_after(q) = 45 + 5q**, as before.

Therefore the added road **strictly increases** equilibrium travel time if and only if

**3 < q < 9** (thousand drivers).

At q = 4 thousand, travel time rises from **65 to 80 minutes**. The system-optimal route allocation after adding the road is 1.75 thousand on each outer route and 0.5 thousand on the middle route, giving **64.6875 minutes** per driver. Thus **PoA = 80 / 64.6875 ≈ 1.236715**.

## Capacity threshold for fixed demand

At 4,000 drivers, the variable-road time is x/k (x in vehicles). For this family, the added road strictly worsens equilibrium time exactly when

**4000/90 < k < 6000/45**, or approximately **44.444 < k < 133.333**.

The lower bound is where the middle road begins to carry traffic; the upper bound is where the new connection ceases to increase equilibrium time. This is a known-model parameter analysis, not a claim of a new theorem.

## Larger networks: controlled computational study

Two distinct synthetic families were tested with **24 fixed random seeds each** and demands of **1, 2, 4, and 6 thousand drivers**: **192 scenarios total**.

1. **Random layered directed acyclic networks:** Each graph has three intermediate layers of two nodes, with affine edge times drawn from fixed ranges. A shortcut skips one layer. These networks are not designed to exhibit Braess's paradox.
2. **Braess-motif-embedded networks:** The classical network is expanded with an expensive alternate path and two downstream edges. This intentionally preserves a Braess mechanism in a larger graph. It is a **positive control**, not evidence that arbitrary larger networks commonly exhibit the paradox.

For every scenario, the program calculates UE before adding the candidate road, UE afterward, SO afterward, and PoA afterward. The complete individual results appear in `larger_networks.csv`. The chart `larger_networks.png` shows changes in equilibrium travel time.

### Computed outcomes

- Random layered family: **0/96** paradox cases.
- Embedded Braess family: **48/96** paradox cases.
- Combined: **48/192 (25%)** cases, a descriptive proportion for **these particular two generators**, not a population statistic or a result about real cities.

The strong difference is expected because the second family was deliberately constructed around a known Braess network. This demonstrates the importance of network structure and experimental design, rather than discovering a general frequency of the paradox.

## Limitations and future research

- Static, single-origin/single-destination assignment; no departure-time or queue dynamics.
- All road functions are affine and nondecreasing; drivers have perfect information and select equilibrium routes.
- Networks are small DAGs with enumerated simple paths. Large networks require scalable path-generation or link-based assignment.
- No real traffic observations or calibrated travel-time functions are used.
- A stronger future study would specify a null network ensemble, use matched candidate-edge selection, vary topology and demand independently, and report confidence intervals or robustness checks. Empirical validation would require appropriate traffic datasets.

## How to reproduce

From the extracted folder:

```bash
python -m pip install -r requirements.txt
python run_experiments.py
cd research && python -m unittest -v test_traffic
```

The script overwrites the three CSV result files, three PNG plots, and `RESULTS_SUMMARY.md`. It uses fixed seeds; no network access is required.

## Background reading (established literature)

- Braess, D. (1968). *Über ein Paradoxon aus der Verkehrsplanung*. Unternehmensforschung 12, 258–268.
- Beckmann, M., McGuire, C. B., and Winsten, C. B. (1956). *Studies in the Economics of Transportation*. Yale University Press.
- Roughgarden, T., and Tardos, É. (2002). *How Bad Is Selfish Routing?* Journal of the ACM 49(2), 236–259.

This is an educational research portfolio and not a peer-reviewed publication.


All files in this distribution are in a single directory, without subfolders.
