import numpy as np
import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Problem-specific parameters
N_users = 100  # Number of users
N_drones = 15   # Number of drones
coverage_radius = 100  # Coverage radius of each drone
max_iterations = 100   # Max iterations for the algorithm
dimension = 2          # Each drone has 2D coordinates (x, y)
population_size = 20   # Number of flies in the swarm
search_space = [0, 500]  # Assuming the area is a 500x500 grid

# DFO parameters
sigma = 0.1  # Dispersion factor (random walk intensity)
alpha = 0.5  # Influence of neighboring flies (optional)

# Fitness function: max coverage and resource allocation
def fitness_function(drone_positions, user_locations):
    coverage = calculate_coverage(drone_positions, user_locations)
    resource_allocation = calculate_resource_allocation(drone_positions, user_locations)
    
    # Weighted sum of coverage and resource allocation
    w1, w2 = 0.7, 0.3  # Adjust these weights based on the problem's needs
    fitness_value = w1 * coverage + w2 * resource_allocation
    
    return fitness_value

# Function to calculate user coverage
def calculate_coverage(drone_positions, user_locations):
    covered_users = 0
    for user in user_locations:
        # Check if any drone covers this user
        for drone in drone_positions:
            distance = np.linalg.norm(user - drone)  # Euclidean distance
            if distance <= coverage_radius:
                covered_users += 1
                break  # Once covered, no need to check other drones
    
    # Calculate the percentage of users covered
    coverage_percentage = covered_users / len(user_locations)
    return coverage_percentage

# Function to calculate resource allocation efficiency
def calculate_resource_allocation(drone_positions, user_locations):
    user_resource_allocation = 0
    drone_user_count = np.zeros(N_drones)
    
    # Count how many users are assigned to each drone
    for user in user_locations:
        distances = np.linalg.norm(user - drone_positions, axis=1)
        assigned_drone = np.argmin(distances)  # User connects to the closest drone
        if distances[assigned_drone] <= coverage_radius:
            drone_user_count[assigned_drone] += 1
    
    # Simulate resource allocation for each drone
    for drone_index in range(N_drones):
        if drone_user_count[drone_index] > 0:
            user_resource_allocation += 1 / drone_user_count[drone_index]
    
    resource_efficiency = user_resource_allocation / N_drones
    return resource_efficiency

# Initialize population of flies (random drone positions)
def initialize_population():
    population = []
    for _ in range(population_size):
        drones = np.random.uniform(low=search_space[0], high=search_space[1], size=(N_drones, dimension))
        population.append(drones)
    return population

# Evaluate fitness for the entire population
def evaluate_population(population, user_locations):
    fitness_values = []
    for fly in population:
        fitness_values.append(fitness_function(fly, user_locations))
    return fitness_values

# Main DFO algorithm
def dfo_algorithm():
    population = initialize_population()
    user_locations = np.random.uniform(low=search_space[0], high=search_space[1], size=(N_users, dimension))
    fitness_values = evaluate_population(population, user_locations)
    
    # Best fly (solution) initialization
    best_fly_index = np.argmax(fitness_values)
    best_fly = population[best_fly_index]
    best_fitness = fitness_values[best_fly_index]
    
    all_positions = []
    for iteration in range(max_iterations):
        new_population = []
        
        for i in range(population_size):
            # Perform random walk (dispersion)
            new_fly = population[i] + sigma * (np.random.uniform(-1, 1, size=(N_drones, dimension)))
            
            # Optional: Fly towards the best fly
            if np.random.rand() < alpha:
                new_fly += alpha * (best_fly - population[i])
            
            # Apply boundary constraints
            new_fly = np.clip(new_fly, search_space[0], search_space[1])
            
            new_population.append(new_fly)
        
        new_fitness_values = evaluate_population(new_population, user_locations)
        
        # Update the best fly if a better solution is found
        new_best_fly_index = np.argmax(new_fitness_values)
        new_best_fitness = new_fitness_values[new_best_fly_index]
        
        if new_best_fitness > best_fitness:
            best_fly = new_population[new_best_fly_index]
            best_fitness = new_best_fitness
        
        population = new_population
        all_positions.append([drone for drone in best_fly])  # Store positions for animation

    return best_fly, best_fitness, user_locations, all_positions

# Animation function
def animate_dfo():
    best_fly, best_fitness, user_locations, all_positions = dfo_algorithm()

    fig, ax = plt.subplots()
    ax.set_xlim(0, 500)
    ax.set_ylim(0, 500)
    
    # Scatter plot for drones and users
    user_scatter = ax.scatter(user_locations[:, 0], user_locations[:, 1], color='red', label="Users")
    drone_scatter = ax.scatter([], [], color='blue', label="Drones")
    
    # Circle representing drone coverage area
    coverage_circles = [plt.Circle((0, 0), coverage_radius, color='blue', fill=False, alpha=0.3) for _ in range(N_drones)]
    for circle in coverage_circles:
        ax.add_patch(circle)
    
    def update(frame):
        drone_positions = all_positions[frame]
        drone_scatter.set_offsets(drone_positions)

        # Update the coverage circles
        for i, circle in enumerate(coverage_circles):
            circle.center = (drone_positions[i][0], drone_positions[i][1])

        return drone_scatter, *coverage_circles

    ani = FuncAnimation(fig, update, frames=len(all_positions), interval=500, blit=True, repeat=False)
    
    plt.legend()
    plt.title(f"Dispersive Flies Optimization (DFO) - Final Fitness: {best_fitness}")
    plt.show()

if __name__ == "__main__":
    print("Starting DFO Optimization with Animation")
    animate_dfo()
