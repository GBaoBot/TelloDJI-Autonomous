import yaml

class PID:
    def __init__(self, normalisation_scale, param_file):
        self.normalisation_scale = normalisation_scale  # equate to 1 if don't need to normalize
        self.compute_for_windup_limits_ready = False
        self.upper_windup_limit = 0
        self.lower_windup_limit = 0
        self.integral_sum = 0.0
        self.dt = 0.015  # should be set to the same rate as your yolo inference topic
        self.e_prev = 0
        self.enabled = True  # PID is enabled by default

        # Load PID parameters from the YAML file
        with open(param_file, 'r') as file:
            params = yaml.safe_load(file)
            self.Kp = params['pid_params']['Kp']
            self.Ki = params['pid_params']['Ki']
            self.Kd = params['pid_params']['Kd']
            self.Kp_depth = params['pid_params']['Kp_depth']
            self.Ki_depth = params['pid_params']['Ki_depth']
            self.Kd_depth = params['pid_params']['Kd_depth']

    def control_effort(self, setpoint, feedback):
        if not self.enabled:
            return 0, 0  # Return (0, 0) if PID is disabled

        # Normalize error to vary from -0.5 to 0.5 -> -1 to 1
        error = (setpoint - feedback) / self.normalisation_scale

        # Derivative term
        derivative = (error - self.e_prev) / self.dt
        D_control = self.Kd * derivative

        # Compute windup limits
        if not self.compute_for_windup_limits_ready:
            self.upper_windup_limit = 0.05 * setpoint  # about 5% settling criterion
            self.lower_windup_limit = -0.05 * setpoint
            self.compute_for_windup_limits_ready = True
            print(f"self.upper_windup_limit:{self.upper_windup_limit}")
            print(f"self.lower_windup_limit:{self.lower_windup_limit}")

        # Integral control components
        self.integral_sum += 0.5 * self.Ki * self.dt * (error + self.e_prev)
        self.integral_sum = self.clamp(self.integral_sum, self.lower_windup_limit, self.upper_windup_limit)

        self.e_prev = error  # Update previous error for the next derivative calculation

        total_control_effort = self.Kp * error + D_control + self.integral_sum

        return total_control_effort, error

    def control_effort_depth(self, setpoint, feedback):
        if not self.enabled:
            return 0, 0  # Return (0, 0) if PID is disabled

        # Normalize error to vary from -0.5 to 0.5 -> -1 to 1
        error = (setpoint - feedback) / self.normalisation_scale

        # Derivative term
        derivative = (error - self.e_prev) / self.dt
        D_control = self.Kd_depth * derivative

        # Compute windup limits
        if not self.compute_for_windup_limits_ready:
            self.upper_windup_limit = 0.05 * setpoint  # about 5% settling criterion
            self.lower_windup_limit = -0.05 * setpoint
            self.compute_for_windup_limits_ready = True
            print(f"self.upper_windup_limit:{self.upper_windup_limit}")
            print(f"self.lower_windup_limit:{self.lower_windup_limit}")

        # Integral control components
        self.integral_sum += 0.5 * self.Ki_depth * self.dt * (error + self.e_prev)
        self.integral_sum = self.clamp(self.integral_sum, self.lower_windup_limit, self.upper_windup_limit)

        total_control_effort = self.Kp_depth * error + D_control + self.integral_sum

        self.e_prev = error  # Update previous error for the next derivative calculation

        return total_control_effort, error

    def clamp(self, value, lowest_limit, highest_limit):
        return max(min(value, highest_limit), lowest_limit)

    def enable(self):
        """Enable the PID controller."""
        self.enabled = True

    def disable(self):
        """Disable the PID controller."""
        self.enabled = False

    def reset(self):
        """Reset the PID controller internals."""
        self.integral_sum = 0.0
        self.e_prev = 0
        self.compute_for_windup_limits_ready = False