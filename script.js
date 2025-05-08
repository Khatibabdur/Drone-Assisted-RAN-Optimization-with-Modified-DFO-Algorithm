let dronePositions = [];
let userPositions = [];
let coverage = 0;
let canvas;
let intervalId;

function setup() {
    const canvasContainer = document.getElementById('simulation');
    const size = Math.min(canvasContainer.clientWidth, canvasContainer.clientHeight);
    canvas = createCanvas(size, size);
    canvas.parent('simulation');
    frameRate(10);
    console.log('Canvas setup complete');
}

function draw() {
    background(240);

    // Draw gridlines
    stroke(220);
    strokeWeight(1);
    const gridSize = 20;
    const step = width / gridSize;

    for (let i = 0; i <= width; i += step) {
        line(i, 0, i, height);
        line(0, i, width, i);
    }

    // Draw the users
    fill(255, 0, 0);
    noStroke();
    for (let user of userPositions) {
        ellipse(user[0] * (width / 100), user[1] * (height / 100), 10, 10);
    }

    // Draw the drones and their coverage radius
    const coverageRadius = document.getElementById('coverage_radius').value; // Get the current coverage radius

    for (let i = 0; i < dronePositions.length; i++) {
        // Draw coverage radius
        fill(173, 216, 230, 100); // Light blue color with transparency
        noStroke();
        ellipse(dronePositions[i][0] * (width / 100), dronePositions[i][1] * (height / 100), coverageRadius * 2 * (width / 100), coverageRadius * 2 * (height / 100)); // Scale dynamically

        // Draw the drone itself
        fill(0, 0, 255);
        noStroke();
        ellipse(dronePositions[i][0] * (width / 100), dronePositions[i][1] * (height / 100), 10, 10);
    }

    // Display coverage
    document.getElementById('coverage').innerText = `${coverage}`;
}

document.getElementById('start_simulation').addEventListener('click', function() {
    const num_drones = document.getElementById('num_drones').value;
    const num_users = document.getElementById('num_users').value;
    const coverage_radius = document.getElementById('coverage_radius').value;

    console.log('Starting simulation with', num_drones, 'drones and', num_users, 'users and coverage radius', coverage_radius);
    
    fetch('/start_simulation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ num_drones, num_users, coverage_radius }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'started') {
            console.log('Simulation started');
            userPositions = data.user_positions;
            console.log('Initial User Positions:', userPositions);

            // Clear any existing interval
            clearInterval(intervalId);

            intervalId = setInterval(() => {
                fetch('/positions')
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'finished') {
                            clearInterval(intervalId);
                            console.log('Simulation finished');
                            return;
                        }
                        dronePositions = data.positions;
                        coverage = data.coverage;
                    });
            }, 500);  // Update every 500 ms
        }
    });
});

document.getElementById('stop_simulation').addEventListener('click', function() {
    console.log('Stopping simulation');
    
    fetch('/stop_simulation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'stopped') {
            console.log('Simulation stopped');
            clearInterval(intervalId);
        }
    });
});

document.getElementById('reset_simulation').addEventListener('click', function() {
    console.log('Resetting simulation');

    // Clear drone and user positions
    dronePositions = [];
    userPositions = [];
    coverage = 0;
    clearInterval(intervalId);
    redraw(); // Redraw the canvas to show the reset state

    fetch('/reset_simulation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'reset') {
            console.log('Simulation reset');
        }
    });
});
