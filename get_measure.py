from sensirion_i2c_driver import I2cConnection
from sensirion_i2c_scd.device import Scd4xI2cDevice
from smbus2 import SMBus
import time

# Abre la conexión I2C
i2c_bus = SMBus(1)  # I2C bus 1 es el estándar en Raspberry Pi
i2c_connection = I2cConnection(i2c_bus)
scd = Scd4xI2cDevice(i2c_connection)

# Iniciar el sensor
scd.stop_periodic_measurement()
scd.start_periodic_measurement()
print("Esperando datos del sensor...")

for _ in range(10):
    if scd.read_data_ready_flag().data_ready:
        measurement = scd.read_measurement()
        print(f"CO2: {measurement.co2} ppm")
        print(f"Temperature: {measurement.temperature} °C")
        print(f"Humidity: {measurement.humidity} %")
        print("----------")
    else:
        print("Datos no listos aún.")
    time.sleep(5)

scd.stop_periodic_measurement()
