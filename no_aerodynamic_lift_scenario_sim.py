# This is a simplified simulation for craft designed without aerodynamic lift in mind i.e. rockets/missiles
# powered by RAM/SCRAM jet engines(super and hypersonic air breathing engine designs).
# Drag and various craft specific properties are simplified significantly.
import numpy as np
import matplotlib.pyplot as plt

# Constants
g0 = 9.81  # Gravitational constant (m/s^2)
G = 6.67430e-11  # Gravitational constant in m^3 kg^-1 s^-2
M = 5.972e24     # Mass of Earth in kg
R = 6378 * 1000  # Radius of Earth in meters
x0 = 0.0  # Start positions set to zero meters
y0 = 0.0

# Time parameters
dt = 0.01  # Time step size
t_max = 100  # Maximum time

# Air density vs altitude data table
data_table = {
    "Altitude (m)": [-1000, 0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 15000, 20000, 25000, 30000,
                     40000, 50000, 60000, 70000, 80000, 90000],
    "Density (kg/m^3)": [1.347, 1.225, 1.112, 1.007, 0.9093, 0.8194, 0.7364, 0.6601, 0.5900, 0.5258, 0.4671, 0.4135,
                         0.1948, 0.08891, 0.04008, 0.01841, 0.003996, 0.001027, 0.0003097, 0.00008283, 0.00001846, 0.0]
}


# Main function
def main():

    # Get initial conditions
    v0_horizontal, v0_vertical, x, y, mass0, radius, intake_area = get_initial_conditions()

    # Initialize arrays to store results
    time_values = np.arange(0, t_max, dt)
    delta_mass_values = np.zeros((len(time_values), 1))
    acceleration_values = np.zeros((len(time_values), 2))
    velocity_values = np.zeros((len(time_values), 2))
    position_values = np.zeros((len(time_values), 2))
    thrust_values = np.zeros((len(time_values), 1))

    # Initial state
    state = [v0_horizontal, v0_vertical]  # velocities in m/s
    mass = mass0  # mass in Kg
    # Evolve the system forward in time
    for i, t in enumerate(time_values):
        # Calculate acceleration and fuel consumption
        a_horizontal, a_vertical, T, mass_flow_rate_of_fuel, delta_mass = acceleration_function(state, y, mass,
                                                                                                radius,
                                                                                                intake_area)

        # Store acceleration
        acceleration_values[i] = [a_horizontal, a_vertical]
        # Store thrust and mass
        thrust_values[i] = [T]
        delta_mass_values[i] = [delta_mass * dt]

        # Update velocity
        state[0] += a_horizontal * dt
        state[1] += a_vertical * dt

        # Store velocity
        velocity_values[i] = state

        # Update position and mass
        x, y = position_values[i - 1] + velocity_values[i] * dt
        position_values[i] = [x, y]
        mass -= mass_flow_rate_of_fuel * dt
        delta_mass_values[i] = delta_mass

    # Plot results
    plot_results(time_values, acceleration_values, velocity_values, position_values, thrust_values, delta_mass_values,
                 mass0)


# Function to get initial conditions
def get_initial_conditions():
    try:
        mass0 = float(input("Enter the initial mass of the craft (kg): "))
        velocity_mag = float(input(
            "Enter the initial velocity magnitude (m/s) ex: 100 m/s would be the minimum to be within the edge of "
            "believability for Ramjet operation: "))
        angle_of_attack = float(input("Enter the angle of attack (degrees): "))
        radius = float(input("Enter the radius of the cross section presented in direction of travel(m): "))
        area_of_sec = float(input("Enter the percent of cross sectional area taken up by intake (%): "))
        intake_area = (area_of_sec/100) * np.pi * radius**2
        print(intake_area, "(m^2)")
    except ValueError:
        print("Invalid input. Please enter numeric values.")
        return get_initial_conditions()

    v0_horizontal = velocity_mag * np.cos(np.radians(angle_of_attack))  # meters per second (m/s)
    v0_vertical = velocity_mag * np.sin(np.radians(angle_of_attack))  # meters per second (m/s)
    x = 0.0  # meters (m)
    y = 0.0  # meters above sea level (m)

    return v0_horizontal, v0_vertical, x, y, mass0, radius, intake_area


# Function to calculate air density
def air_density_func(y):
    altitudes = data_table["Altitude (m)"]
    densities = data_table["Density (kg/m^3)"]
    return np.interp(y, altitudes, densities)


# Function to calculate thrust
def thrust_function(air_density, velocity, intake_area):  # This could be modified to switch to a traditional rocket
    # thrust calculation once air density reaches either zero or whenever the constant thrust of a rocket engine would
    # be greater than the air breathing engine to mimic the envisioned mode switching capability from air breathing to
    # onboard oxidizer burning required of an SSTO.
    mass_flow_rate_of_oxygen = 0.232 * air_density * intake_area * velocity  # since we are using air density the
    # oxygen content of the atmosphere must be in terms of wt% so instead of .21 we use.23
    methane_to_oxygen_ratio = 1/17.2 # ~17.2 kg of oxygen for every kg of methane
    mass_flow_rate_of_fuel = methane_to_oxygen_ratio * mass_flow_rate_of_oxygen  # fuel consumed per second (Kg/s)
    T = (mass_flow_rate_of_fuel * g0) * 3200
    delta_mass = mass_flow_rate_of_oxygen * dt  # fuel consumed per time step in Kg/.01s
    return T, mass_flow_rate_of_fuel, delta_mass



# Function to calculate acceleration
def acceleration_function(state, y, mass, radius, intake_area):
    v_horizontal, v_vertical = state
    # Avoid division by zero when computing unit vectors
    denominator = np.sqrt((v_horizontal ** 2) + (v_vertical ** 2)) + 1e-8
    horizontal_mult = v_horizontal / denominator
    vertical_mult = v_vertical / denominator
    air_density = air_density_func(y)

    # Calculate thrust
    T, mass_flow_rate_of_fuel, delta_mass = thrust_function(air_density, v_horizontal, intake_area)

    # Calculate drag
    # Simple cross-sectional drag only (keeps us from needing to define more about the hull design)
    drag_coefficient = 0.025
    cross_sectional_area =  np.pi * radius ** 2  # Possibly the most extreme simplification I've made
    drag_horizontal = 0.5 * drag_coefficient * air_density * cross_sectional_area * v_horizontal ** 2
    drag_vertical = 0.5 * drag_coefficient * air_density * cross_sectional_area * v_vertical ** 2
    # Calculate gravitational force
    g = G * (M / (R + y) ** 2)
    gravity_force = mass * g

    # Calculate horizontal acceleration ignoring lift's effect in the horizontal (would include for more detailed sims)
    a_horizontal = (T * horizontal_mult - drag_horizontal) / mass

    # Calculate vertical acceleration
    a_vertical = (T * vertical_mult - gravity_force - drag_vertical) / mass

    return a_horizontal, a_vertical, T, mass_flow_rate_of_fuel, delta_mass


# Function to plot results
def plot_results(time_values, acceleration_values, velocity_values, position_values, thrust_values, delta_mass_values,
                 mass0):
    print("start and end values:")
    print("t:", time_values)
    print("accel:", acceleration_values)
    print("vel:", velocity_values)
    print("x,y:", position_values)
    print("mass(negative value means you needed more mass than your entire initial crafts mass):", mass0 - np.cumsum(delta_mass_values))
    print("Tons of onboard oxidizer saved:", (17.2 * np.cumsum(delta_mass_values))/1000)
    print("Use horizontal velocity associated with time (s) that resulted in positive vertical velocity as launch speed"
          " if it results indicate vertical hits negative.")
    plt.figure(figsize=(12, 12))

    plt.subplot(4, 2, 1)
    plt.plot(time_values, acceleration_values[:, 1])
    plt.xlabel('Time (s)')
    plt.ylabel('Acceleration (m/s^2)')
    plt.title('Vertical Acceleration vs Time')
    plt.grid()

    plt.subplot(4, 2, 2)
    plt.plot(time_values, acceleration_values[:, 0])
    plt.xlabel('Time (s)')
    plt.ylabel('Acceleration (m/s^2)')
    plt.title('Horizontal Acceleration vs Time')
    plt.grid()

    plt.subplot(4, 2, 3)
    plt.plot(time_values, velocity_values[:, 1])
    plt.xlabel('Time (s)')
    plt.ylabel('Velocity (m/s)')
    plt.title('Vertical Velocity vs Time')
    plt.grid()

    plt.subplot(4, 2, 4)
    plt.plot(time_values, velocity_values[:, 0])
    plt.plot(time_values, 460 + velocity_values[:, 0]) # 460m/s is earths rotation, assume launch direction aligns
    plt.xlabel('Time (s) Orange:Orbital vel,Blu:Speed over ground')
    plt.ylabel('Velocity (m/s)')
    plt.title('Horizontal Velocity vs Time')
    plt.grid()

    plt.subplot(4, 2, 5)
    plt.plot(time_values, position_values[:, 1])
    plt.xlabel('Time (s)')
    plt.ylabel('Position (m)')
    plt.title('Vertical Position vs Time')
    plt.grid()

    plt.subplot(4, 2, 6)
    plt.plot(time_values, position_values[:, 0])
    plt.xlabel('Time (s)')
    plt.ylabel('Position (m)')
    plt.title('Ground distance traveled vs Time')
    plt.grid()

    plt.subplot(4, 2, 7)
    plt.plot(time_values, thrust_values[:, 0])
    plt.xlabel('Time (s)')
    plt.ylabel('Newtons (N)')
    plt.title('Thrust vs Time')
    plt.grid()

    plt.subplot(4, 2, 8)
    plt.plot(time_values, delta_mass_values)
    plt.xlabel('Time (s)')
    plt.ylabel('Mass (Kg/s)')
    plt.title('Fuel consumption vs Time')
    plt.grid()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
