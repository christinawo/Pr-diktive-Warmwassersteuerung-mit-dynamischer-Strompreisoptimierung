# Boiler dimensions are based on the VGE Eco Tank series
# Emission factor is based on a paper from the umweltbundesamt (https://www.umweltbundesamt.at/fileadmin/site/publikationen/rep0888.pdf)

PARAMS = {
    "volume_liters": 200.0,
    "mass_kg": 200.0,
    "cp_water": 4186.0,
    "heater_power_w": 2000.0,
    "temp_start": 60.0,
    "temp_min": 45.0,
    "temp_max": 65.0,
    "temp_ambient": 22.0,
    "temp_cold": 12.0,
    "U_value": 0.4,
    "A_value": 2.82,
    "time_step_seconds": 900,
    "simulation_hours": 24,
    "emission_factor": 0.226
}


BOILER_SIZES = {
    100: {"volume_liters": 100.0, "mass_kg": 100.0, "A_value": 1.87},
    200: {"volume_liters": 200.0, "mass_kg": 200.0, "A_value": 2.82},
    300: {"volume_liters": 300.0, "mass_kg": 300.0, "A_value": 3.51}
}