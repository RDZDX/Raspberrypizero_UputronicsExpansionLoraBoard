#!/usr/bin/env python3

import lgpio
import time

RED = 6
GREEN = 13

# Open GPIO chip 0
h = lgpio.gpiochip_open(0)

# Set pins as output
lgpio.gpio_claim_output(h, RED)
lgpio.gpio_claim_output(h, GREEN)

# Set PWM frequency (Hz)
FREQ = 1000

# Initialize PWM (0 duty)
lgpio.tx_pwm(h, RED, FREQ, 0)
lgpio.tx_pwm(h, GREEN, FREQ, 0)

try:
    while True:
        # Fade up
        for duty in range(0, 101, 2):
            lgpio.tx_pwm(h, RED, FREQ, duty)
            lgpio.tx_pwm(h, GREEN, FREQ, 100 - duty)
            time.sleep(0.02)

        # Fade down
        for duty in range(100, -1, -2):
            lgpio.tx_pwm(h, RED, FREQ, duty)
            lgpio.tx_pwm(h, GREEN, FREQ, 100 - duty)
            time.sleep(0.02)

except KeyboardInterrupt:
    pass

# Stop PWM (set duty to 0)
lgpio.tx_pwm(h, RED, 0, 0)
lgpio.tx_pwm(h, GREEN, 0, 0)

# Release GPIO
lgpio.gpiochip_close(h)
