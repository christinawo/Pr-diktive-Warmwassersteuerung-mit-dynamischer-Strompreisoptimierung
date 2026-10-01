class Boiler:
    def __init__(self, params):
        self.temp = params["temp_start"]
        self.mass = params["mass_kg"]
        self.cp = params["cp_water"]
        self.u_value = params["U_value"]
        self.a_value = params["A_value"]
        self.heater_power = params["heater_power_w"]
        self.temp_ambient = params["temp_ambient"]
        self.temp_cold = params["temp_cold"]
        self.temp_max = params["temp_max"]
        self.time_step = params["time_step_seconds"]
    
    def thermical_model(self, heater_on: bool, draw_off: float, dt_s: float):
        # Heat loss to the environment
        p_loss = self.u_value * self.a_value * (self.temp - self.temp_ambient)

        # Heat loss caused by hot-water demand
        p_draw = draw_off * self.cp * (self.temp - self.temp_cold)

        heating_energy_kwh = 0.0

        if heater_on and self.temp < self.temp_max:
            p_net = self.heater_power - p_loss - p_draw

            dT_dt = p_net / (self.mass * self.cp)
            temp_full_step = self.temp + dT_dt * dt_s

            if temp_full_step <= self.temp_max:
                self.temp = temp_full_step
                heating_energy_kwh = (self.heater_power / 1000) * (dt_s / 3600)
            else:
                # Calculate required heating time to reach the maximum temperature
                delta_temp = self.temp_max - self.temp

                if p_net > 0:
                    heating_time_s = delta_temp * self.mass * self.cp / p_net
                    heating_time_s = min(heating_time_s, dt_s)

                    heating_energy_kwh = (self.heater_power / 1000) * (heating_time_s / 3600)

                self.temp = self.temp_max

        else:
            # Temperature change without heating
            p_net = -p_loss - p_draw
            dT_dt = p_net / (self.mass * self.cp)
            self.temp += dT_dt * dt_s

        return self.temp, heating_energy_kwh