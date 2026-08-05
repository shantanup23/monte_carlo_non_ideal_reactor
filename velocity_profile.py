# --- 1. Initialization ---
import numpy as np
import matplotlib.pyplot as plt

# --- 2. Simulation Function (Modified) ---
def run_simulation(ax, title, P_STAY_DEAD_ZONE_PARAM, CHANNEL_SPEED_BONUS_PARAM, USE_LAMINAR_FLOW=False):
    """
    Runs the full RTD simulation with selectable flow profiles.
    
    ax: The matplotlib axis object to plot on.
    title: The title for the subplot.
    P_STAY_DEAD_ZONE_PARAM: The P_STAY_DEAD_ZONE to use (0 to disable).
    CHANNEL_SPEED_BONUS_PARAM: The CHANNEL_SPEED_BONUS (only if USE_LAMINAR_FLOW is False).
    USE_LAMINAR_FLOW: Boolean. If True, uses parabolic velocity. If False, uses plug flow.
    """

    # --- Setup Parameters (Constants for all runs) ---
    N_PARTICLES = 5000
    REACTOR_LENGTH = 100
    REACTOR_WIDTH = 20
    P_DISP_AXIAL = 0.2  # Base axial dispersion
    P_DISP_RADIAL = 0.3 # Base radial dispersion

    # --- Laminar Flow Parameters (if used) ---
    # We set VEL_MAX = 2.0 so the *average* velocity is 1.0, same as plug flow
    VEL_MAX = 2.0 
    CENTER_Y = (REACTOR_WIDTH - 1) / 2.0

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
        if time > REACTOR_LENGTH * 30: # Increased timeout for slow laminar flow at walls
            print(f"Warning: Simulation '{title}' timed out.")
            break
            
        for i in range(N_PARTICLES):
            if exit_times[i] != -1:
                continue
            
            x_pos = particle_positions[i, 0]
            y_pos = particle_positions[i, 1]

            # --- DEAD ZONE CHECK (Applies to both models) ---
            is_in_dead_zone_x = (DEAD_ZONE_X[0] <= x_pos < DEAD_ZONE_X[1])
            is_in_dead_zone_y = (DEAD_ZONE_Y[0] <= y_pos < DEAD_ZONE_Y[1])
            
            if is_in_dead_zone_x and is_in_dead_zone_y and np.random.rand() < P_STAY_DEAD_ZONE_PARAM:
                continue  # Particle gets stuck

            # --- Convection (Two different models) ---
            if USE_LAMINAR_FLOW:
                # --- LAMINAR FLOW CONVECTION ---
                # Calculate parabolic velocity based on y-position
                normalized_y_sq = ((y_pos - CENTER_Y) / CENTER_Y)**2
                v = VEL_MAX * (1 - normalized_y_sq)
                
                # Probabilistic movement for fractional velocity
                base_move = int(v)
                fractional_prob = v - base_move
                
                particle_positions[i, 0] += base_move
                if np.random.rand() < fractional_prob:
                    particle_positions[i, 0] += 1
            
            else:
                # --- PLUG FLOW + CHANNELING CONVECTION (Original Model) ---
                particle_positions[i, 0] += 1 # Base convection
                
                if y_pos < CHANNEL_WIDTH:
                    particle_positions[i, 0] += CHANNEL_SPEED_BONUS_PARAM 
            
            # --- Dispersion (Applies to both models) ---
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

    # --- 5. Analysis & Plotting ---
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
    ax.set_xlim(0, 750) # Use a fixed, large x-axis for comparison

# --- 6. Main Execution ---
fig, axes = plt.subplots(1, 2, figsize=(18, 7))
fig.suptitle("Comparing Flow Profiles (High Non-Ideality: P_stay = 0.9)", fontsize=18)

# --- Run 1: Original Model (Plug Flow + Channeling) ---
print("Running: Plug Flow + Channeling + Dead Zone Model...")
run_simulation(ax=axes[0], 
               title="Plug Flow + Channeling + Dead Zone", 
               P_STAY_DEAD_ZONE_PARAM=0.9,
               CHANNEL_SPEED_BONUS_PARAM=1,
               USE_LAMINAR_FLOW=False)

# --- Run 2: New Model (Laminar Flow) ---
print("Running: Laminar Flow + Dead Zone Model...")
run_simulation(ax=axes[1], 
               title="Laminar Flow + Dead Zone ", 
               P_STAY_DEAD_ZONE_PARAM=0.9, 
               CHANNEL_SPEED_BONUS_PARAM=0, # Not used
               USE_LAMINAR_FLOW=True)

plt.tight_layout(rect=[0, 0.03, 1, 0.93])
plt.show()

print("All simulations complete.")