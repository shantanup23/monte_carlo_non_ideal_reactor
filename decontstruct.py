# --- 1. Initialization ---
import numpy as np
import matplotlib.pyplot as plt

# --- 2. Simulation Function ---
# I've moved your code into a function.
# This lets us call it multiple times with different parameters.

def run_simulation(ax, title, P_STAY_DEAD_ZONE_PARAM, CHANNEL_SPEED_BONUS_PARAM):
    """
    Runs the full RTD simulation and plots the result on a given matplotlib axis.
    
    ax: The matplotlib axis object to plot on.
    title: The title for the subplot.
    P_STAY_DEAD_ZONE_PARAM: The P_STAY_DEAD_ZONE to use (0 to disable).
    CHANNEL_SPEED_BONUS_PARAM: The CHANNEL_SPEED_BONUS to use (0 to disable).
    """

    # --- Setup Parameters (Constants for all runs) ---
    N_PARTICLES = 5000
    REACTOR_LENGTH = 100
    REACTOR_WIDTH = 20
    P_DISP_AXIAL = 0.2  # Base axial dispersion
    P_DISP_RADIAL = 0.3 # Base radial dispersion

    # --- Non-Ideal Definitions ---
    DEAD_ZONE_X = [30, 60]  # x-range [start, end]
    DEAD_ZONE_Y = [5, 15]   # y-range [start, end]
    CHANNEL_WIDTH = 3       # y < 3 is the fast channel

    # --- Initialize Data Structures ---
    particle_positions = np.zeros((N_PARTICLES, 2), dtype=int)
    particle_positions[:, 1] = np.random.randint(0, REACTOR_WIDTH, size=N_PARTICLES)
    exit_times = np.full(N_PARTICLES, -1, dtype=int)

    # --- Main Simulation Loop ---
    time = 0
    particles_exited = 0

    while particles_exited < N_PARTICLES:
        time += 1

        for i in range(N_PARTICLES):
            if exit_times[i] != -1:
                continue
            
            x_pos = particle_positions[i, 0]
            y_pos = particle_positions[i, 1]

            # --- DEAD ZONE CHECK ---
            is_in_dead_zone_x = (DEAD_ZONE_X[0] <= x_pos < DEAD_ZONE_X[1])
            is_in_dead_zone_y = (DEAD_ZONE_Y[0] <= y_pos < DEAD_ZONE_Y[1])
            
            if is_in_dead_zone_x and is_in_dead_zone_y and np.random.rand() < P_STAY_DEAD_ZONE_PARAM:
                continue  # Particle gets stuck

            # --- Apply Movement Rules ---
            
            # 1. Convection
            particle_positions[i, 0] += 1
            
            # 2. CHANNELING CHECK
            if y_pos < CHANNEL_WIDTH:
                particle_positions[i, 0] += CHANNEL_SPEED_BONUS_PARAM # Move extra fast
            
            # 3. Axial Dispersion
            if np.random.rand() < P_DISP_AXIAL:
                if np.random.rand() < 0.5:
                    particle_positions[i, 0] += 1
                else:
                    particle_positions[i, 0] -= 1
                    
            # 4. Radial Dispersion
            if np.random.rand() < P_DISP_RADIAL:
                if np.random.rand() < 0.5:
                    particle_positions[i, 1] += 1
                else:
                    particle_positions[i, 1] -= 1

            # --- Handle Boundaries ---
            if particle_positions[i, 0] < 0:
                 particle_positions[i, 0] = 0
            if particle_positions[i, 1] < 0:
                 particle_positions[i, 1] = 0
            if particle_positions[i, 1] >= REACTOR_WIDTH:
                 particle_positions[i, 1] = REACTOR_WIDTH - 1

            # --- Check for Exit ---
            if particle_positions[i, 0] >= REACTOR_LENGTH:
                exit_times[i] = time
                particles_exited += 1

        if time > REACTOR_LENGTH * 20:
            print(f"Warning: Simulation '{title}' timed out.")
            break
            
    # --- 5. Analysis & Plotting (on the provided 'ax') ---
    final_times = exit_times[exit_times != -1]
    if len(final_times) == 0:
        ax.text(0.5, 0.5, 'Error: No particles exited', ha='center')
        ax.set_title(title, fontsize=12)
        return

    mean_t = np.mean(final_times)
    var_t = np.var(final_times)
    
    ax.hist(final_times, bins=80, density=True, edgecolor='black', alpha=0.7)
    ax.set_title(title, fontsize=12)
    ax.set_xlabel("Residence Time (steps)", fontsize=10)
    ax.set_ylabel("E(t) - Probability Density", fontsize=10)
    
    # Add stats to the plot
    stats_text = f"Mean = {mean_t:.1f}\nVariance = {var_t:.1f}"
    ax.text(0.95, 0.95, stats_text, transform=ax.transAxes, ha='right', va='top', 
            bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.5))
    ax.grid(True, linestyle='--', alpha=0.6)
    # Set a common x-axis limit for all plots for easy comparison
    ax.set_xlim(0, max(time, 550)) # Ensure x-axis is consistent

# --- 6. Main Execution ---
# Create a 2x2 subplot grid
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle("Deconstructing Non-Ideal Reactor Behavior", fontsize=18)

# Run 1: "Ideal-ish" Base Reactor (Axial + Radial Dispersion only)
print("Running: A: Base Reactor...")
run_simulation(ax=axes[0, 0], 
               title="A: Base Reactor (Dispersion Only)", 
               P_STAY_DEAD_ZONE_PARAM=0, 
               CHANNEL_SPEED_BONUS_PARAM=0)

# Run 2: Channeling Only
print("Running: B: Channeling Model...")
run_simulation(ax=axes[0, 1], 
               title="B: Base Reactor + Channeling", 
               P_STAY_DEAD_ZONE_PARAM=0, 
               CHANNEL_SPEED_BONUS_PARAM=1)

# Run 3: Dead Zone Only
print("Running: C: Dead Zone Model...")
run_simulation(ax=axes[1, 0], 
               title="C: Base Reactor + Dead Zone", 
               P_STAY_DEAD_ZONE_PARAM=0.9, 
               CHANNEL_SPEED_BONUS_PARAM=0)

# Run 4: Full Model (The plot you showed me)
print("Running: D: Full Model...")
run_simulation(ax=axes[1, 1], 
               title="D: Full Model (Channeling + Dead Zone)", 
               P_STAY_DEAD_ZONE_PARAM=0.9, 
               CHANNEL_SPEED_BONUS_PARAM=1)

# Clean up the layout and show the final plot
plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Adjust for suptitle
plt.show()

print("All simulations complete.")