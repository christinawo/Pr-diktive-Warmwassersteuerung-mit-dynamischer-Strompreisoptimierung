import random

def shower_event():
    volume_liters = random.gauss(40.0, 10.0)
    volume_liters = max(20.0, min(volume_liters, 60.0))
    target_temperature = 40.0
    return volume_liters, target_temperature

def bathing_event():
    volume_liters = random.gauss(140.0, 20.0)
    volume_liters = max(100.0, min(volume_liters, 180.0))
    target_temperature = 40.0
    return volume_liters, target_temperature

# This could be for example a short handwashing event
def small_draw_event():
    volume_liters = random.gauss(1.0, 0.5)
    volume_liters = max(0.1, volume_liters)
    target_temperature = 40.0
    return volume_liters, target_temperature

# This could be for example a dishwashing event
def medium_draw_event():
    volume_liters = random.gauss(6.0, 2.0)
    volume_liters = max(0.5, volume_liters)
    target_temperature = 50.0
    return volume_liters, target_temperature
