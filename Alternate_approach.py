import numpy as np
import matplotlib.pyplot as plt

# Air density vs altitude data table
data_table = {
    "Altitude (m)": [-1000, 0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 15000, 20000, 25000, 30000,
                     40000, 50000, 60000, 70000, 80000, 90000],
    "Density (kg/m^3)": [1.347, 1.225, 1.112, 1.007, 0.9093, 0.8194, 0.7364, 0.6601, 0.5900, 0.5258, 0.4671, 0.4135,
                         0.1948, 0.08891, 0.04008, 0.01841, 0.003996, 0.001027, 0.0003097, 0.00008283, 0.00001846, 0.0]
}


def get_air_density(altitude):
    return np.interp(altitude, data_table["Altitude (m)"], data_table["Density (kg/m^3)"])


def get_initial_conditions():
    try:
        mass0 = float(input("Enter the initial mass of the craft, 200 kg minimum mass above this is considered fuel available (kg): "))
        velocity_mag = float(input(
            "Enter the initial velocity magnitude (m/s) ex: 100 m/s would be the minimum to be within the edge of "
            "believability for Ramjet operation: "))
        angle_of_attack = float(input("Enter the angle of attack (degrees): "))
        radius = float(input("Enter the radius of the cross section presented in direction of travel(m): "))
        area_of_sec = float(input("Enter the percent of cross sectional area taken up by intake (%): "))
        intake_area = (area_of_sec / 100) * np.pi * radius ** 2
        print(intake_area, "(m^2)")
    except ValueError:
        print("Invalid input. Please enter numeric values.")
        return get_initial_conditions()
    velocity_mag0 = velocity_mag
    unit_v_x0 = velocity_mag0 * np.cos(np.radians(angle_of_attack))/ velocity_mag0
    unit_v_y0 = velocity_mag0 * np.sin(np.radians(angle_of_attack))/ velocity_mag0
    air_density0 = 1.347
    mass_flow_rate_of_oxygen0 = 0.232 * air_density0 * intake_area * velocity_mag  # since we are using air density the
    # oxygen content of the atmosphere must be in terms of wt% so instead of .21 we use.23
    methane_to_oxygen_ratio= 1/17.2 # ~17.2 kg of oxygen for every kg of methane
    mass_flow_rate_of_fuel0 = methane_to_oxygen_ratio * mass_flow_rate_of_oxygen0  # fuel consumed per second (Kg/s)
    thrust_mag0 = (mass_flow_rate_of_fuel0 * 9.81) * 3200
    drag_mag0 = 0.5 * .025 * air_density0 * velocity_mag ** 2 * np.pi * (radius ** 2)  # Drag calculation

    thrust_x0 = thrust_mag0 * unit_v_x0
    thrust_y0 = thrust_mag0 * unit_v_y0
    drag_x0 = -drag_mag0 * unit_v_x0
    drag_y0 = -drag_mag0 * unit_v_y0
    a0_x =(thrust_x0 + drag_x0) / mass0
    a0_y = (thrust_y0 + drag_y0 - 9.81 * mass0) / mass0
    v0_x = velocity_mag0 * np.cos(np.radians(angle_of_attack))  # meters per second (m/s)
    v0_y = velocity_mag0 * np.sin(np.radians(angle_of_attack))  # meters per second (m/s)
    x0 = 0.0  # meters (m)
    y0 = 0.0  # meters above sea level (m)

    return [x0, y0, v0_x, v0_y, a0_x, a0_y, mass0, air_density0, radius, intake_area]


def state_function(state, dt):
    x, y, v_x, v_y, a_x, a_y, mass, air_density, radius, intake_area = state

    air_density = get_air_density(y)  # Update air density based on altitude

    velocity_mag = np.sqrt(v_x ** 2 + v_y ** 2)
    unit_v_x = v_x / velocity_mag if velocity_mag != 0 else 0
    unit_v_y = v_y / velocity_mag if velocity_mag != 0 else 0
    mass_flow_rate_of_oxygen = 0.232 * air_density * intake_area * velocity_mag  # since we are using air density the
    # oxygen content of the atmosphere must be in terms of wt% so instead of .21 we use.23
    methane_to_oxygen_ratio = 1/17.2 # ~17.2 kg of oxygen for every kg of methane
    if mass <= 200:
        mass_flow_rate_of_fuel = 0  # Stop fuel consumption when mass is below 200 kg
    else:
        mass_flow_rate_of_fuel = methane_to_oxygen_ratio * mass_flow_rate_of_oxygen  # fuel consumed per second (Kg/s)
    thrust_mag = (mass_flow_rate_of_fuel * 9.81) * 3200
    drag_mag = 0.5 * .025 * air_density * velocity_mag ** 2 * np.pi * (radius ** 2)  # Drag calculation

    thrust_x = thrust_mag * unit_v_x
    thrust_y = thrust_mag * unit_v_y
    drag_x = -drag_mag * unit_v_x
    drag_y = -drag_mag * unit_v_y

    a_x_new = (thrust_x + drag_x) / mass
    a_y_new = (thrust_y + drag_y - 9.81 * mass) / mass
    mass_new = mass - mass_flow_rate_of_fuel * dt
    v_x_new = v_x + a_x_new * dt
    v_y_new = v_y + a_y_new * dt
    x_new = x + v_x * dt
    y_new = y + v_y * dt

    return [x_new, y_new, v_x_new, v_y_new, a_x_new, a_y_new, mass_new, air_density, radius, intake_area]


# Get initial conditions from user input
initial_state = get_initial_conditions()
dt = 0.01  # Time step

time_steps = 1000
trajectory = [initial_state]

for _ in range(time_steps):
    new_state = state_function(trajectory[-1], dt)
    trajectory.append(new_state)

trajectory = np.array(trajectory)
print(trajectory[:, 6])

time_values = np.linspace(0, time_steps * dt, len(trajectory))

plt.figure(figsize=(12, 12))

plt.subplot(4, 2, 1)
plt.plot(time_values, trajectory[:, 5])
plt.xlabel('Time (s)')
plt.ylabel('Acceleration (m/s^2)')
plt.title('Vertical Acceleration vs Time')
plt.grid()

plt.subplot(4, 2, 2)
plt.plot(time_values, trajectory[:, 4])
plt.xlabel('Time (s)')
plt.ylabel('Acceleration (m/s^2)')
plt.title('Horizontal Acceleration vs Time')
plt.grid()

plt.subplot(4, 2, 3)
plt.plot(time_values, trajectory[:, 3])
plt.xlabel('Time (s)')
plt.ylabel('Velocity (m/s)')
plt.title('Vertical Velocity vs Time')
plt.grid()

plt.subplot(4, 2, 4)
plt.plot(time_values, trajectory[:, 2])
plt.plot(time_values, 460 + trajectory[:, 2])
plt.xlabel('Time (s)')
plt.ylabel('Velocity (m/s)')
plt.title('Horizontal Velocity vs Time')
plt.grid()

plt.subplot(4, 2, 5)
plt.plot(time_values, trajectory[:, 1])
plt.xlabel('Time (s)')
plt.ylabel('Position (m)')
plt.title('Vertical Position vs Time')
plt.grid()

plt.subplot(4, 2, 6)
plt.plot(time_values, trajectory[:, 0])
plt.xlabel('Time (s)')
plt.ylabel('Position (m)')
plt.title('Ground distance traveled vs Time')
plt.grid()

plt.tight_layout()
plt.show()
