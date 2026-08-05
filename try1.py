# --- 1. Initialization ---
import numpy as np
import matplotlib.pyplot as plt

# --- 2. Setup Parameters ---
N_PARTICLES = 5000
REACTOR_LENGTH = 100
REACTOR_WIDTH = 20
P_DISP_AXIAL = 0.2  # Renamed for clarity

# --- <<< ADDED: REALISM PARAMETERS >>> ---
# Set probabilities to 0 to disable that feature

# 1. RADIAL DISPERSION (side-to-side mixing)
P_DISP_RADIAL = 0.3  # Probability of a y-direction jump (0 to disable)

# 2. DEAD ZONE (a stagnant region)
# Define the zone's coordinates
DEAD_ZONE_X = [30, 60]  # x-range [start, end]
DEAD_ZONE_Y = [5, 15]   # y-range [start, end]
P_STAY_DEAD_ZONE = 0.9  # 90% chance of getting 'stuck' for one time step (0 to disable)

# 3. CHANNELING / BYPASSING (a fast lane)
CHANNEL_WIDTH = 3       # y < 3 is the fast channel
CHANNEL_SPEED_BONUS = 1 # Extra +1 x-step if in channel (0 to disable)
# --- <<< END OF ADDED PARAMETERS >>> ---


# --- 3. Initialize Data Structures ---
particle_positions = np.zeros((N_PARTICLES, 2), dtype=int)
particle_positions[:, 1] = np.random.randint(0, REACTOR_WIDTH, size=N_PARTICLES)
exit_times = np.full(N_PARTICLES, -1, dtype=int)

# --- 4. The Main Simulation Loop ---
time = 0
particles_exited = 0

while particles_exited < N_PARTICLES:
    time += 1

    # Loop through each particle
    for i in range(N_PARTICLES):

        # Skip particles that have already exited
        if exit_times[i] != -1:
            continue
            
        # Get current particle position for checks
        x_pos = particle_positions[i, 0]
        y_pos = particle_positions[i, 1]

        # --- <<< ADDED: DEAD ZONE CHECK >>> ---
        # This check happens FIRST. If a particle is in a dead zone, it might get stuck.
        is_in_dead_zone_x = (DEAD_ZONE_X[0] <= x_pos < DEAD_ZONE_X[1])
        is_in_dead_zone_y = (DEAD_ZONE_Y[0] <= y_pos < DEAD_ZONE_Y[1])
        
        if is_in_dead_zone_x and is_in_dead_zone_y and np.random.rand() < P_STAY_DEAD_ZONE:
            continue  # Particle gets stuck, skip all movement for this time step

        # --- Apply Movement Rules ---
        
        # 1. Convection
        particle_positions[i, 0] += 1
        
        # --- <<< ADDED: CHANNELING CHECK >>> ---
        if y_pos < CHANNEL_WIDTH:
            particle_positions[i, 0] += CHANNEL_SPEED_BONUS # Move extra fast
        
        # 2. Axial Dispersion (Forward/Backward)
        if np.random.rand() < P_DISP_AXIAL:
            if np.random.rand() < 0.5:
                particle_positions[i, 0] += 1  # Jump forward
            else:
                particle_positions[i, 0] -= 1  # Jump backward
                
        # --- <<< ADDED: RADIAL DISPERSION (Up/Down) >>> ---
        if np.random.rand() < P_DISP_RADIAL:
            if np.random.rand() < 0.5:
                particle_positions[i, 1] += 1  # Jump up
            else:
                particle_positions[i, 1] -= 1  # Jump down

        
        # --- Handle Boundaries ---
        # Prevent backflow at inlet
        if particle_positions[i, 0] < 0:
             particle_positions[i, 0] = 0
             
        # --- <<< ADDED: WALL BOUNDARIES (Bounce off top/bottom) >>> ---
        if particle_positions[i, 1] < 0:
             particle_positions[i, 1] = 0
        if particle_positions[i, 1] >= REACTOR_WIDTH:
             particle_positions[i, 1] = REACTOR_WIDTH - 1

        # --- 3. Data Collection (Check for Exit) ---
        if particle_positions[i, 0] >= REACTOR_LENGTH:
            exit_times[i] = time
            particles_exited += 1

    # Safety break
    if time > REACTOR_LENGTH * 20: # Increased timeout for complex flow
        print("Warning: Simulation timed out. Not all particles exited.")
        break
        
# --- 5. Analysis & Plotting ---
print(f"Simulation complete at time {time}")

# Filter out any particles that never exited
final_times = exit_times[exit_times != -1]
if len(final_times) == 0:
    print("Error: No particles exited. Check parameters.")
else:
    print(f"Particles exited: {len(final_times)} / {N_PARTICLES}")
    print(f"Mean Residence Time: {np.mean(final_times):.2f}")
    print(f"Variance: {np.var(final_times):.2f}")

    # Deliverable 2: Comparative Plot
    plt.figure(figsize=(10, 6))
    plt.hist(final_times, bins=80, density=True, edgecolor='black', alpha=0.7) # More bins for detail
    plt.title(f"RTD Curve for Non-Ideal Reactor")
    plt.xlabel("Residence Time (steps)")
    plt.ylabel("E(t) - Probability Density")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.show()