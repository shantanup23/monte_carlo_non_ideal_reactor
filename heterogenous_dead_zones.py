# --- 1. Initialization ---
import numpy as np
import matplotlib.pyplot as plt

# --- 2. Simulation Function (Modified for Heterogeneous Zones) ---
def run_simulation(ax, title, dead_zones_list, CHANNEL_SPEED_BONUS_PARAM):
    """
    Runs the full RTD simulation with a list of dead zones.
    
    ax: The matplotlib axis object to plot on.
    title: The title for the subplot.
    dead_zones_list: A list of dictionaries, where each dict defines a zone.
                     e.g., [{'x_range': [20, 40], 'y_range': [5, 10], 'p_stay': 0.9}]
    CHANNEL_SPEED_BONUS_PARAM: The CHANNEL_SPEED_BONUS to use.
    """

    # --- Setup Parameters (Constants for all runs) ---
    N_PARTICLES = 5000
    REACTOR_LENGTH = 100
    REACTOR_WIDTH = 20
    P_DISP_AXIAL = 0.2  # Base axial dispersion
    P_DISP_RADIAL = 0.3 # Base radial dispersion

    # --- Non-Ideal Definitions ---
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

            # --- <<< MODIFIED: HETEROGENEOUS DEAD ZONE CHECK >>> ---
            # Loop through all defined dead zones
            is_stuck = False
            for zone in dead_zones_list:
                is_in_x = (zone['x_range'][0] <= x_pos < zone['x_range'][1])
                is_in_y = (zone['y_range'][0] <= y_pos < zone['y_range'][1])
                
                if is_in_x and is_in_y and np.random.rand() < zone['p_stay']:
                    is_stuck = True
                    break  # Particle is stuck, no need to check other zones
            
            if is_stuck:
                continue # Skip all movement for this time step

            # --- Apply Movement Rules ---
            particle_positions[i, 0] += 1 # Base Convection
            
            if y_pos < CHANNEL_WIDTH: # Channeling
                particle_positions[i, 0] += CHANNEL_SPEED_BONUS_PARAM 
            
            if np.random.rand() < P_DISP_AXIAL: # Axial Dispersion
                particle_positions[i, 0] += 1 if np.random.rand() < 0.5 else -1
                    
            if np.random.rand() < P_DISP_RADIAL: # Radial Dispersion
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
# Create a 1x2 subplot grid
fig, axes = plt.subplots(1, 2, figsize=(18, 7))
fig.suptitle("Comparing Homogeneous vs. Heterogeneous Dead Zones", fontsize=18)

# --- Define the Dead Zone setups ---

# 1. Homogeneous Model: One "medium" dead zone
medium_zone_list = [
    {'x_range': [30, 60], 'y_range': [5, 15], 'p_stay': 0.6}
]

# 2. Heterogeneous Model: One "deep" (sticky) zone and one "shallow" (mild) zone
hetero_zone_list = [
    {'x_range': [20, 40], 'y_range': [5, 10], 'p_stay': 0.9},  # Deep/Sticky
    {'x_range': [60, 80], 'y_range': [10, 15], 'p_stay': 0.4}  # Shallow/Mild
]

# --- Run 1: Homogeneous Model ---
print("Running: Homogeneous Model (1 Medium Zone)...")
run_simulation(ax=axes[0], 
               title="Homogeneous Model (P_stay = 0.6)", 
               dead_zones_list=medium_zone_list,
               CHANNEL_SPEED_BONUS_PARAM=1)

# --- Run 2: Heterogeneous Model ---
print("Running: Heterogeneous Model (1 Deep + 1 Shallow Zone)...")
run_simulation(ax=axes[1], 
               title="Heterogeneous Model (P_stay=0.9 & P_stay=0.4)", 
               dead_zones_list=hetero_zone_list,
               CHANNEL_SPEED_BONUS_PARAM=1)

plt.tight_layout(rect=[0, 0.03, 1, 0.93])
plt.show()

print("All simulations complete.")