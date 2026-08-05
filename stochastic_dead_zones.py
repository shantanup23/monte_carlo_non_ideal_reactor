# --- 1. Initialization ---
import numpy as np
import matplotlib.pyplot as plt

# --- 2. GLOBAL CONSTANTS ---
# <<< MOVED HERE to be accessible by all functions
REACTOR_LENGTH = 100
REACTOR_WIDTH = 20

# --- 3. New Function: Stochastic Map Generator ---
def generate_stochastic_map(length, width, density, p_stay_values):
    """
    Creates a 2D map of the reactor with randomly placed "sticky" cells.
    
    length: Reactor length (e.g., 100)
    width: Reactor width (e.g., 20)
    density: The fraction of cells that will be "sticky" (e.g., 0.15 for 15%)
    p_stay_values: A list of stickiness probabilities to assign (e.g., [0.3, 0.6, 0.9])
    """
    p_stay_map = np.zeros((length, width))
    for x in range(length):
        for y in range(width):
            if np.random.rand() < density:
                # This cell is part of a "dense spot" (dead zone)
                p_stay_map[x, y] = np.random.choice(p_stay_values)
    return p_stay_map

# --- 4. Simulation Function (Modified to accept p_stay_map) ---
def run_simulation(ax, title, CHANNEL_SPEED_BONUS_PARAM, 
                   p_stay_map=None, P_STAY_HOMOGENEOUS=0, DEAD_ZONE_X=None, DEAD_ZONE_Y=None):
    """
    Runs the full RTD simulation.
    If 'p_stay_map' is provided, it uses the stochastic model.
    Otherwise, it uses the homogeneous (hard-coded) dead zone parameters.
    """

    # --- Setup Parameters (Constants for all runs) ---
    N_PARTICLES = 5000
    # <<< DELETED FROM HERE
    # <<< DELETED FROM HERE
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
        if time > REACTOR_LENGTH * 30: # Increased timeout for complex maps
            print(f"Warning: Simulation '{title}' timed out.")
            break
            
        for i in range(N_PARTICLES):
            if exit_times[i] != -1:
                continue
            
            x_pos = particle_positions[i, 0]
            y_pos = particle_positions[i, 1]

            # --- <<< MODIFIED: DEAD ZONE CHECK (Stochastic or Homogeneous) >>> ---
            is_stuck = False
            if p_stay_map is not None:
                # STOCHASTIC MODEL
                # Get stickiness from the map at the particle's current location
                # Boundary check to prevent error if particle is at x=100
                if x_pos >= REACTOR_LENGTH:
                    x_pos = REACTOR_LENGTH - 1 
                
                stickiness = p_stay_map[x_pos, y_pos]
                if np.random.rand() < stickiness:
                    is_stuck = True
            else:
                # HOMOGENEOUS MODEL (Original logic)
                is_in_dead_zone_x = (DEAD_ZONE_X[0] <= x_pos < DEAD_ZONE_X[1])
                is_in_dead_zone_y = (DEAD_ZONE_Y[0] <= y_pos < DEAD_ZONE_Y[1])
                if is_in_dead_zone_x and is_in_dead_zone_y and np.random.rand() < P_STAY_HOMOGENEOUS:
                    is_stuck = True
            
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
    final_times = exit_times[exit_times[exit_times != -1] < (REACTOR_LENGTH * 29)] # Filter timeouts
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
fig.suptitle("Comparing Homogeneous vs. Stochastic Dead Zone Models", fontsize=18)

# --- Run 1: Homogeneous Model (Medium Non-Ideality) ---
print("Running: Homogeneous Model (1 Medium Zone)...")
run_simulation(ax=axes[0], 
               title="Homogeneous Model (P_stay = 0.6)", 
               CHANNEL_SPEED_BONUS_PARAM=1,
               P_STAY_HOMOGENEOUS=0.6,
               DEAD_ZONE_X=[30, 60],
               DEAD_ZONE_Y=[5, 15])

# --- Run 2: Stochastic "Packed Bed" Model ---
print("Running: Stochastic Model...")

# Generate the random reactor map ONCE.
# These calls will now work because REACTOR_LENGTH is a global variable
stochastic_map = generate_stochastic_map(length=REACTOR_LENGTH, 
                                       width=REACTOR_WIDTH, 
                                       density=0.15, 
                                       p_stay_values=[0.3, 0.6, 0.9])

run_simulation(ax=axes[1], 
               title="Stochastic Model (15% density, P_stay=0.3-0.9)", 
               CHANNEL_SPEED_BONUS_PARAM=1,
               p_stay_map=stochastic_map) # Pass the map here

plt.tight_layout(rect=[0, 0.03, 1, 0.93])
plt.show()

print("All simulations complete.")