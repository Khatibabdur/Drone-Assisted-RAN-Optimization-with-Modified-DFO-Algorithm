from flask import Flask, render_template, request, jsonify
import numpy as np
import simpy
from threading import Thread
from algorithm import Drone, User, advanced_dfo_algorithm, calculate_coverage

app = Flask(__name__)

positions = []
user_positions = []
coverage_data = [0]
simulation_running = False

def simulation_process(env, drones, users, positions, coverage_data, coverage_radius=20):
    global simulation_running
    for _ in range(100):
        if not simulation_running:
            break
        drones, _ = advanced_dfo_algorithm(drones, users, coverage_radius=coverage_radius)
        positions[:] = [[drone.position[0], drone.position[1]] for drone in drones]
        coverage = calculate_coverage(drones, users, coverage_radius)
        coverage_data[0] = coverage
        yield env.timeout(1)
    
    simulation_running = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_simulation', methods=['POST'])
def start_simulation():
    global positions, user_positions, coverage_data, simulation_running
    simulation_running = True

    data = request.json
    num_drones = int(data['num_drones'])
    num_users = int(data['num_users'])
    coverage_radius = int(data['coverage_radius'])

    env = simpy.Environment()
    drones = [Drone(env, i, np.random.random(2) * 100) for i in range(num_drones)]
    users = [User(env, i, np.random.random(2) * 100) for i in range(num_users)]
    positions = [[drone.position[0], drone.position[1]] for drone in drones]
    user_positions = [[user.position[0], user.position[1]] for user in users]
    coverage_data = [0]

    env.process(simulation_process(env, drones, users, positions, coverage_data, coverage_radius))
    sim_thread = Thread(target=env.run)
    sim_thread.start()

    return jsonify({"status": "started", "user_positions": user_positions})

@app.route('/stop_simulation', methods=['POST'])
def stop_simulation():
    global simulation_running
    simulation_running = False
    return jsonify({"status": "stopped"})

@app.route('/reset_simulation', methods=['POST'])
def reset_simulation():
    global positions, user_positions, coverage_data, simulation_running
    positions = []
    user_positions = []
    coverage_data = [0]
    simulation_running = False
    return jsonify({"status": "reset"})

@app.route('/positions')
def get_positions():
    global simulation_running
    if not simulation_running:
        return jsonify({"status": "finished"})
    return jsonify(positions=positions, coverage=coverage_data[0])

if __name__ == '__main__':
    app.run(debug=True)