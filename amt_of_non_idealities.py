# --- 1. Initialization ---
import numpy as np
import matplotlib.pyplot as plt

# --- 2. Simulation Function ---
# (This is the same function as before, for re-usability)
def run_simulation(ax, title, P_STAY_DEAD_ZONE_PARAM, CHANNEL_SPEED_BONUS_PARAM):
    """
    Runs the full RTD simulation and plots the result on a given matplotlib axis.
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
        if time > REACTOR_LENGTH * 20: # Safety break
            print(f"Warning: Simulation '{title}' timed out.")
            break
            
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
            particle_positions[i, 0] += 1
            
            if y_pos < CHANNEL_WIDTH:
                particle_positions[i, 0] += CHANNEL_SPEED_BONUS_PARAM 
            
            if np.random.rand() < P_DISP_AXIAL:
                particle_positions[i, 0] += 1 if np.random.rand() < 0.5 else -1
                    
            if np.random.rand() < P_DISP_RADIAL:
                particle_positions[i, 1] += 1 if np.random.rand() < 0.5 else -1

            # --- Handle Boundaries ---
            if particle_positions[i, 0] < 0: particle_positions[i, 0] = 0
            if particle_positions[i, 1] < 0: particle_positions[i, 1] = 0
            if particle_positions[i, 1] >= REACTOR_WIDTH: particle_positions[i, 1] = REACTOR_WIDTH - 1

            # --- Check for Exit ---
            if particle_positions[i, 0] >= REACTOR_LENGTH:
                exit_times[i] = time
                particles_exited += 1

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
    
    stats_text = f"Mean = {mean_t:.1f}\nVariance = {var_t:.1f}"
    ax.text(0.95, 0.95, stats_text, transform=ax.transAxes, ha='right', va='top', 
            bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.5))
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.set_xlim(0, 650) # Use a fixed, large x-axis for comparison

# --- 6. Main Execution ---
# Create a 1x3 subplot grid
fig, axes = plt.subplots(1, 3, figsize=(20, 6))
fig.suptitle("Sensitivity Analysis: Effect of Dead Zone 'Stickiness'", fontsize=18)

# --- Run 1: Low Non-Ideality ---
print("Running: Low Non-Ideality Model...")
run_simulation(ax=axes[0], 
               title="Low Non-Ideality (P_stay = 0.3)", 
               P_STAY_DEAD_ZONE_PARAM=0.3,  # Mildly sticky
               CHANNEL_SPEED_BONUS_PARAM=1)

# --- Run 2: Medium Non-Ideality ---
print("Running: Medium Non-Ideality Model...")
run_simulation(ax=axes[1], 
               title="Medium Non-Ideality (P_stay = 0.6)", 
               P_STAY_DEAD_ZONE_PARAM=0.6,  # Moderately sticky
               CHANNEL_SPEED_BONUS_PARAM=1)

# --- Run 3: High Non-Ideality ---
print("Running: High Non-Ideality Model...")
run_simulation(ax=axes[2], 
               title="High Non-Ideality (P_stay = 0.9)", 
               P_STAY_DEAD_ZONE_PARAM=0.9,  # Very sticky
               CHANNEL_SPEED_BONUS_PARAM=1)

plt.tight_layout(rect=[0, 0.03, 1, 0.93])
plt.show()

print("All simulations complete.")