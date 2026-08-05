import numpy as np
import matplotlib.pyplot as plt

# --- Global Constants ---
LENGTH = 100
WIDTH = 20
k = 0.01  # 1st-order rate constant

# --- Stochastic Map Generator ---
def generate_stochastic_map(length, width, density, p_values):
    p_map = np.zeros((length, width))
    for x in range(length):
        for y in range(width):
            if np.random.rand() < density:
                p_map[x, y] = np.random.choice(p_values)
    return p_map

# --- Simulation Function ---
def run_simulation(title, ch_speed, disp_axial, disp_radial,
                   p_map=None, p_stay=0, dead_x=None, dead_y=None):

    n_particles = 10000
    ch_width = 3
    pos = np.zeros((n_particles, 2), dtype=int)
    pos[:, 1] = np.random.randint(0, WIDTH, n_particles)
    exit_times = np.full(n_particles, -1, dtype=int)

    t = 0
    exited = 0
    while exited < n_particles:
        t += 1
        if t > LENGTH * 30:
            print(f"Warning: {title} timed out.")
            break

        for i in range(n_particles):
            if exit_times[i] != -1:
                continue

            x, y = pos[i]
            stuck = False

            if p_map is not None:
                if x >= LENGTH: 
                    x = LENGTH - 1
                if np.random.rand() < p_map[x, y]:
                    stuck = True
            elif p_stay > 0:
                if (dead_x[0] <= x < dead_x[1]) and (dead_y[0] <= y < dead_y[1]) and np.random.rand() < p_stay:
                    stuck = True

            if stuck:
                continue

            pos[i, 0] += 1  # Convection
            if y < ch_width:
                pos[i, 0] += ch_speed

            if np.random.rand() < disp_axial:
                pos[i, 0] += 1 if np.random.rand() < 0.5 else -1

            if np.random.rand() < disp_radial:
                pos[i, 1] += 1 if np.random.rand() < 0.5 else -1

            pos[i, 0] = max(0, pos[i, 0])
            pos[i, 1] = min(max(pos[i, 1], 0), WIDTH - 1)

            if pos[i, 0] >= LENGTH:
                exit_times[i] = t
                exited += 1

    valid_times = exit_times[(exit_times != -1) & (exit_times < LENGTH * 29)]
    if len(valid_times) == 0:
        print(f"Error: No exits in {title}.")
        return 0, 0

    mean_t = np.mean(valid_times)
    conv = np.mean(1 - np.exp(-k * valid_times))
    return mean_t, conv

# --- Run All Simulations ---
print("Running simulations...")

results = {}

print("1. Ideal PFR")
results['Ideal PFR'] = run_simulation("Ideal PFR", 0, 0.0, 0.0, p_stay=0)

print("2. Dispersion")
results['Dispersion'] = run_simulation("Dispersion", 0, 0.2, 0.3, p_stay=0)

print("3. Low NI")
results['Low NI'] = run_simulation("Low NI", 1, 0.2, 0.3, p_stay=0.3, dead_x=[30, 60], dead_y=[5, 15])

print("4. Medium NI")
results['Medium NI'] = run_simulation("Medium NI", 1, 0.2, 0.3, p_stay=0.6, dead_x=[30, 60], dead_y=[5, 15])

print("5. High NI")
results['High NI'] = run_simulation("High NI", 1, 0.2, 0.3, p_stay=0.9, dead_x=[30, 60], dead_y=[5, 15])

print("6. Stochastic")
p_map = generate_stochastic_map(LENGTH, WIDTH, 0.15, [0.3, 0.6, 0.9])
results['Stochastic'] = run_simulation("Stochastic", 1, 0.2, 0.3, p_map=p_map)

# --- Analysis ---
print("\n--- Summary ---")
print(f"{'Model':<15} {'Mean t':<10} {'Sim Conv (%)':<15} {'Ideal Conv (%)':<15} {'Effectiveness (%)':<15}")
print("-" * 70)

model_names, abs_conv, rel_conv = [], [], []

for name, (mean_t, conv) in results.items():
    ideal_conv = 1 - np.exp(-k * mean_t)
    eff = (conv / ideal_conv * 100) if ideal_conv > 0 else 0
    print(f"{name:<15} {mean_t:<10.1f} {conv*100:<15.2f} {ideal_conv*100:<15.2f} {eff:<15.2f}")
    model_names.append(name)
    abs_conv.append(conv * 100)
    rel_conv.append(eff)

