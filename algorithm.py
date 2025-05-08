import numpy as np

class Drone:
    def __init__(self, env, id, position):
        self.env = env
        self.id = id
        self.position = position
        self.best_position = position.copy()
        self.best_coverage = 0

class User:
    def __init__(self, env, id, position):
        self.env = env
        self.id = id
        self.position = position

# Function to calculate coverage
def calculate_coverage(drones, users, coverage_radius=20):
    coverage = 0
    for user in users:
        if any(np.linalg.norm(drone.position - user.position) <= coverage_radius for drone in drones):
            coverage += 1
    return coverage

# Function to calculate repulsion force
def calculate_repulsion(drones, repulsion_distance=10, repulsion_factor=1.5):
    forces = [np.zeros(2) for _ in range(len(drones))]
    for i in range(len(drones)):
        for j in range(i + 1, len(drones)):
            distance = np.linalg.norm(drones[i].position - drones[j].position)
            if distance < repulsion_distance:
                force_direction = (drones[i].position - drones[j].position) / distance
                force_magnitude = repulsion_factor * (repulsion_distance - distance)
                forces[i] += force_direction * force_magnitude
                forces[j] -= force_direction * force_magnitude
    return forces

def advanced_dfo_algorithm(drones, users, num_iterations=1, coverage_radius=20, alpha=2.0, beta=0.5, gamma=1.0, delta=0.01):
    def update_positions(drones, global_best_position, inertia_weight):
        repulsion_distance = 10  # Minimum allowable distance between drones
        repulsion_forces = calculate_repulsion(drones, repulsion_distance)
        
        for drone, repulsion_force in zip(drones, repulsion_forces):
            # Move towards personal best
            inertia = inertia_weight * (drone.best_position - drone.position)
            drone.position += gamma * inertia
            
            # Add random movement
            random_step = alpha * (np.random.random(2) - 0.5)
            drone.position += random_step
            
            # Move towards global best
            global_attraction = beta * (global_best_position - drone.position)
            drone.position += global_attraction
            
            # Apply repulsion force
            drone.position += repulsion_force
            
            # Ensure the new position is within the bounds (0 to 100 for simplicity)
            drone.position = np.clip(drone.position, 0, 100)
    
    global_best_position = max(drones, key=lambda drone: drone.best_coverage).best_position
    global_best_coverage = max(drones, key=lambda drone: drone.best_coverage).best_coverage
    
    inertia_weight = 0.9  # Initial inertia weight for balancing exploration and exploitation
    inertia_decay = 0.99  # Decay factor for inertia weight
    
    for iteration in range(num_iterations):
        for drone in drones:
            # Calculate current coverage
            current_coverage = calculate_coverage(drones, users, coverage_radius)
            
            # Update personal best
            if current_coverage > drone.best_coverage:
                drone.best_coverage = current_coverage
                drone.best_position = drone.position.copy()
        
        # Update global best
        current_global_best_drone = max(drones, key=lambda drone: drone.best_coverage)
        if current_global_best_drone.best_coverage > global_best_coverage:
            global_best_position = current_global_best_drone.best_position
            global_best_coverage = current_global_best_drone.best_coverage
        
        # Update positions of all drones
        update_positions(drones, global_best_position, inertia_weight)
        
        # Adaptive parameter adjustments
        alpha *= (1 - delta)
        beta *= (1 - delta)
        gamma *= (1 - delta)
        inertia_weight *= inertia_decay  # Decay inertia weight
        
        # Convergence criteria (optional)
        if np.linalg.norm(global_best_position - np.mean([drone.position for drone in drones], axis=0)) < 1e-3:
            break
    
    return drones, global_best_position