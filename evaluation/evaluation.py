import matplotlib.pyplot as plt

def calculate_comfort(temps, temp_min):
    comfortable_steps = sum(
        1 for temp in temps if temp >= temp_min
    )
    
    return comfortable_steps / len(temps) * 100

def evaluation_plots(times, temps, energy_history, strategy):
    figure, (plot1, plot2) = plt.subplots(2, 1)
    figure.subplots_adjust(hspace=0.5)
    plot1.plot(times, temps)
    plot1.set_title(f"Temperature over time [{strategy}]")
    plot1.set_xlabel("Time [h]")
    plot1.set_ylabel("Temperature [°C]")
    plot1.grid()

    plot2.plot(times, energy_history)
    plot2.set_title("Energy usage over time")
    plot2.set_xlabel("Time [h]")
    plot2.set_ylabel("Energy [kWh]")
    plot2.grid()

    plt.show()
