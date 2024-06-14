import csv
import matplotlib.pyplot as plt
import numpy as np


# Function to calculate the total acceleration from accelerometer data
def calculate_total_acceleration(ax, ay, az):
    return np.sqrt(ax**2 + ay**2 + az**2)


def read_accelerometer_data(file_path="accelerometer.csv"):
    """
    Reads accelerometer data from a CSV file and calculates the force for each row.

    :param file_path: Path to the CSV file.
    :return: List of tuples containing (total_acceleration, force) for each row.
    """
    results = []
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for row in reader:
            if reader.line_num == 1:
                continue
            if len(row) != 3:
                print(f"Skipping invalid row: {row}")
                continue
            results.append(list(map(float, row)))
            try:
                pass
            except ValueError:
                print(f"Skipping invalid row: {row}")
                raise ValueError("Invalid csv file")

    return results


def plot_total_accelerations(accelerations):
    """
    Побудова графіка загальних прискорень.

    :param accelerations: Список загальних прискорень.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(accelerations, marker='o', linestyle='-', color='b')
    plt.title("Графік загальних прискорень")
    plt.xlabel("Часовий індекс")
    plt.ylabel("Загальне прискорення (м/с^2)")
    plt.grid(True)
    plt.show()


data = read_accelerometer_data()
total_accelerations = [np.sqrt(row[0] ** 2 + row[1] ** 2 + row[2] ** 2) for row in data]

total_x = [row[0] for row in data]
total_y = [row[1] for row in data]
total_z = [row[2] for row in data]

plot_total_accelerations(total_accelerations)
plot_total_accelerations(total_x)
plot_total_accelerations(total_y)
plot_total_accelerations(total_z)
