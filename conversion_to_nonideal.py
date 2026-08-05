# --- 1. Initialization ---
import numpy as np
import matplotlib.pyplot as plt

# --- 2. GLOBAL CONSTANTS ---
REACTOR_LENGTH = 100
REACTOR_WIDTH = 20
N_PARTICLES = 10000 # Use high particle count for accuracy
N_TRIALS = 5        # Number of times to run each guess to average out noise
ERROR_TOLERANCE_PERCENT = 5.0 # We want our variance to be within +/- 5%

# --- 3. Simulation Function (Unchanged) ---
def run_simulation(title, channel_speed_bonus, p_disp_axial, p_disp_radial,
                   p_stay_map=None, p_stay_homogeneous=0, dead_zone_x=None, dead_zone_y=None):
    """
    Runs the full RTD simulation and RETURNS mean time and variance.
    """
    n_particles = N_PARTICLES 
    CHANNEL_WIDTH = 3
    
    particle_positions = np.zeros((n_particles, 2), dtype=int)
    particle_positions[:, 1] = np.random.randint(0, REACTOR_WIDTH, size=n_particles)
    exit_times = np.full(n_particles, -1, dtype=int)
    
    time = 0
    particles_exited = 0
    
    while particles_exited < n_particles:
        time += 1
        if time > REACTOR_LENGTH * 30: 
            #print(f"Warning: Simulation '{title}' timed out.")
            break
            
        for i in range(n_particles):
            if exit_times[i] != -1: 
                continue
            
            x_pos = particle_positions[i, 0]
            y_pos = particle_positions[i, 1]
            
            is_stuck = False
            if p_stay_map is not None:
                if x_pos >= REACTOR_LENGTH: 
                    x_pos = REACTOR_LENGTH - 1 
                stickiness = p_stay_map[x_pos, y_pos]
                if np.random.rand() < stickiness: 
                    is_stuck = True
            elif p_stay_homogeneous > 0:
                is_in_dead_zone_x = (dead_zone_x[0] <= x_pos < dead_zone_x[1])
                is_in_dead_zone_y = (dead_zone_y[0] <= y_pos < dead_zone_y[1])
                if is_in_dead_zone_x and is_in_dead_zone_y and np.random.rand() < p_stay_homogeneous:
                    is_stuck = True
            
            if is_stuck: 
                continue 

            particle_positions[i, 0] += 1 
            if y_pos < CHANNEL_WIDTH: 
                particle_positions[i, 0] += channel_speed_bonus 
            if np.random.rand() < p_disp_axial: 
                particle_positions[i, 0] += 1 if np.random.rand() < 0.5 else -1
            if np.random.rand() < p_disp_radial: 
                particle_positions[i, 1] += 1 if np.random.rand() < 0.5 else -1

            if particle_positions[i, 0] < 0: particle_positions[i, 0] = 0
            if particle_positions[i, 1] < 0: particle_positions[i, 1] = 0
            if particle_positions[i, 1] >= REACTOR_WIDTH: particle_positions[i, 1] = REACTOR_WIDTH - 1
            
            if particle_positions[i, 0] >= REACTOR_LENGTH:
                exit_times[i] = time
                particles_exited += 1

    final_times = exit_times[exit_times[exit_times != -1] < (REACTOR_LENGTH * 29)] 
    if len(final_times) == 0:
        print(f"Error in simulation '{title}': No particles exited.")
        return 0, 0 
        
    mean_t = np.mean(final_times)
    var_t = np.var(final_times) 
    return mean_t, var_t

# --- 4. Averaging Wrapper Function (Unchanged) ---
def run_simulation_averaged(n_trials, title, **kwargs):
    """
    Runs the simulation n_trials times and returns the AVERAGE t_bar and var_t.
    """
    all_means = []
    all_vars = []
    for i in range(n_trials):
        mean_t, var_t = run_simulation(f"{title} Trial {i+1}", **kwargs)
        if mean_t > 0: 
            all_means.append(mean_t)
            all_vars.append(var_t)
            
    if not all_means: 
        return 0, 0
        
    avg_mean = np.mean(all_means)
    avg_var = np.mean(all_vars)
    
    return avg_mean, avg_var

# --- 5. NEW: Main Solver Function ---
def find_non_ideality_parameter(target_t, target_var, model_name):
    """
    Runs the binary search to find the p_stay that matches the target_t,
    then validates the result against the target_var.
    """
    print(f"\n--- Analyzing Case: {model_name} ---")
    print(f"Target Practical Data: Mean t = {target_t}, Variance = {target_var}")
    print("Searching for 'p_stay_homogeneous' that matches Mean t...")
    
    search_low = 0.0
    search_high = 0.95 
    iterations = 8     
    best_fit_p_stay = 0.0

    for i in range(iterations):
        p_guess = (search_low + search_high) / 2
        
        sim_params = {
            'channel_speed_bonus': 1,
            'p_disp_axial': 0.2,
            'p_disp_radial': 0.3,
            'p_stay_homogeneous': p_guess,
            'dead_zone_x': [30, 60],
            'dead_zone_y': [5, 15]
        }
        avg_t, avg_var = run_simulation_averaged(N_TRIALS, f"{model_name} Search {i+1}", **sim_params)
        
        if avg_t < target_t:
            search_low = p_guess
        else:
            search_high = p_guess
            
        best_fit_p_stay = (search_low + search_high) / 2

    print(f"Search complete. Best-fit p_stay = {best_fit_p_stay:.4f}")

    # --- Final Verification ---
    #print("Running final verification...")
    final_params = {
        'channel_speed_bonus': 1,
        'p_disp_axial': 0.2,
        'p_disp_radial': 0.3,
        'p_stay_homogeneous': best_fit_p_stay,
        'dead_zone_x': [30, 60],
        'dead_zone_y': [5, 15]
    }
    final_t, final_var = run_simulation_averaged(N_TRIALS, "Final Fit", **final_params)

    variance_error = final_var - target_var
    variance_error_pct = (variance_error / target_var) * 100.0
    
    # Check if our model's variance is within the tolerance
    if abs(variance_error_pct) <= ERROR_TOLERANCE_PERCENT:
        conclusion = "Good Fit"
    else:
        conclusion = "POOR Fit"

    # Return all results for the final summary table
    return best_fit_p_stay, final_t, final_var, conclusion

# --- 6. Main Execution ---

# Define the three sets of "Practical Data" we want to test
# (Based on your "Sensitivity Analysis" plot)
practical_data_sets = [
    {
        "name": "Low Non-Ideality",
        "target_t": 96.9,
        "target_var": 422.8
    },
    {
        "name": "Medium Non-Ideality",
        "target_t": 112.2,
        "target_var": 1084.4
    },
    {
        "name": "High Non-Ideality",
        "target_t": 220.0,
        "target_var": 18003.1
    }
]

# Store the final results
final_results = []

for data in practical_data_sets:
    p_stay, sim_t, sim_var, conclusion = find_non_ideality_parameter(
        data["target_t"], data["target_var"], data["name"]
    )
    final_results.append({
        "name": data["name"],
        "target_t": data["target_t"],
        "target_var": data["target_var"],
        "found_p_stay": p_stay,
        "sim_t": sim_t,
        "sim_var": sim_var,
        "conclusion": conclusion
    })

# --- 7. Final Summary Report ---
print("\n" + "=" * 80)
print("--- FINAL SUMMARY: INVERSE PROBLEM SOLVER ---")
print("=" * 80)
print(f"{'Case':<20} {'Target t':<12} {'Found p_stay':<14} {'Result t':<12} {'Target Var':<12} {'Result Var':<12} {'Fit':<10}")
print("-" * 80)

for res in final_results:
    print(f"{res['name']:<20} {res['target_t']:<12.1f} {res['found_p_stay']:<14.4f} {res['sim_t']:<12.2f} {res['target_var']:<12.1f} {res['sim_var']:<12.2f} {res['conclusion']:<10}")