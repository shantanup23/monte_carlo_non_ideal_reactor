#  Monte Carlo Simulation for Non-Ideal Flow in Packed Bed Reactors

## Overview
Fluid flow in real chemical reactors seldom exhibits perfectly ideal behavior. In actual systems, reactors often experience non-ideal flow due to incomplete mixing, dead zones, channeling, and regions of stagnation. These flow anomalies distort the Residence Time Distribution (RTD) and negatively impact conversion efficiency and selectivity. 

This repository provides a flexible, "bottom-up" **Monte Carlo simulation framework** to model particle paths in non-ideal Packed Bed Reactors (PBR). By tracking thousands of individual fluid particles on a 2D grid, this tool simulates macroscopic flow behavior and generates reliable RTD curves. It bridges the gap between theoretical ideal reactor models and realistic hydrodynamics.

---

## The Monte Carlo Particle Framework
Unlike traditional dispersion or tanks-in-series analytical models, this Monte Carlo approach simulates multi-dimensional flow based on a sequence of probabilistic rules applied to each particle at every time step.

The reactor is modeled as a 2D grid (default dimensions: $100 \times 20$). At each time step, a particle undergoes:
1. **Dead Zone Trapping:** Particles entering a defined "dead zone" have a probability (`P_STAY_DEAD_ZONE`) of getting trapped for that time step.
2. **Convection & Channeling:** Free particles move forward by basic convection. If they are in a designated high-velocity channeling region (e.g., near the reactor wall), they receive an extra speed boost.
3. **Dispersion:** Independent random numbers dictate axial (forward/backward) and radial (side-to-side) dispersion probabilities (`P_DISP_AXIAL` and `P_DISP_RADIAL`).

By aggregating the exit times of $N=5000$ to $10,000$ particles, the simulation generates a highly accurate RTD histogram $E(t)$.

---

## Practical Use Cases for Chemical Engineers

This simulation tool is designed for practical reactor analysis, scale-up, and troubleshooting:

### 1. Predicting Conversion Loss Due to Structural Defects
By simulating an RTD for a given configuration, you can use the segregated flow model to estimate the absolute conversion for a 1st-order reaction. The repository evaluates reactor **Effectiveness**—comparing the simulated non-ideal conversion directly against an ideal Plug Flow Reactor (PFR) with the exact same mean residence time. This highlights exactly how much performance is lost to poor fluid dynamics.

### 2. Modeling Packed Beds via Stochastic Dead Zones
Real packed beds don't have single, large "rectangular" dead zones. Instead, flow anomalies are distributed. The `generate_stochastic_map` function allows you to assign a uniform density of "sticky" regions across the entire reactor grid [cite: 3]. This realistically mimics the irregular fluid pathways through a porous catalyst bed, showing how micro-channeling and random stagnation average out into a broad RTD peak.

### 3. The "Inverse Problem": Diagnosing Real-World Reactors
In real life, engineers perform tracer tests to get an RTD, rather than simulating it from scratch. The provided `find_non_ideality_parameter` function uses a binary search algorithm to reverse-engineer reactor conditions. By inputting an experimental mean residence time and variance, the script computationally finds the internal stickiness/dead-zone probability (`p_stay`) that best fits your real-world data.

---

## How to Use the Repository

### Core Parameters
The main simulation functions accept the following core parameters:
* `N_PARTICLES`: Number of particles to simulate (Recommended: 5000 - 10000 for smooth distributions).
* `P_DISP_AXIAL`: Base probability of axial mixing (default: `0.2`).
* `P_DISP_RADIAL`: Base probability of radial mixing (default: `0.3`).
* `CHANNEL_SPEED_BONUS`: Extra steps taken if in a channeling region.
* `P_STAY_DEAD_ZONE`: Probability of a particle getting stuck if inside a dead zone.

### 1. Running a Basic Sensitivity Analysis
Use the `run_simulation()` function to evaluate different dead zone "stickiness" levels.

```python
import numpy as np
import matplotlib.pyplot as plt

# Simulate a Highly Non-Ideal Reactor
fig, ax = plt.subplots()
run_simulation(
    ax=ax, 
    title="High Non-Ideality (P_stay = 0.9)", 
    P_STAY_DEAD_ZONE_PARAM=0.9, 
    CHANNEL_SPEED_BONUS_PARAM=1
)
plt.show()
```

### 2. Using the Stochastic Map Generator
To model a realistic packed bed, generate a stochastic map and pass it to the simulation.

```python
from reactor_sim import generate_stochastic_map, run_simulation

# Generate a map where 15% of cells have a stickiness of 0.3, 0.6, or 0.9
stochastic_map = generate_stochastic_map(
    length=100, 
    width=20, 
    density=0.15, 
    p_stay_values=[0.3, 0.6, 0.9]
)

fig, ax = plt.subplots()
run_simulation(
    ax=ax, 
    title="Stochastic Packed Bed Model", 
    CHANNEL_SPEED_BONUS_PARAM=1,
    p_stay_map=stochastic_map
)
plt.show()
```

### 3. Solving the Inverse Problem (Parameter Fitting)
If you have practical RTD data (Mean Time and Variance), use the solver to find the reactor's non-ideality parameter.

```python
from inverse_solver import find_non_ideality_parameter

# Target data from a tracer test
target_mean_time = 112.2
target_variance = 1084.4

# Returns the best-fit P_stay, simulated mean, variance, and fit conclusion
p_stay, sim_t, sim_var, conclusion = find_non_ideality_parameter(
    target_t=target_mean_time, 
    target_var=target_variance, 
    model_name="Medium Non-Ideality Test"
)

print(f"Calculated Dead Zone Probability: {p_stay:.4f}")
print(f"Fit Quality: {conclusion}")
```

## Summary of Flow Profiles
The framework allows for comparative studies of various physical setups:
* **Dispersion Only (Base Reactor):** Models natural axial/radial spread, resulting in a narrow Gaussian RTD with low variance.
* **Channeling Only:** Results in a bimodal distribution where a fast peak bypasses the main flow.
* **Dead Zone Only:** Creates a distinct "tail" in the RTD, significantly increasing mean time and variance.
* **Laminar Flow vs. Plug Flow:** The code can optionally switch base convection to a parabolic laminar flow profile to evaluate systematic vs. structural flaws.
