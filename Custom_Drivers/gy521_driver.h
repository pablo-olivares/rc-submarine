#ifndef CUSTOM_DRIVRS_GY521_DRIVER_H
#define CUSTOM_DRIVRS_GY521_DRIVER_H

#include "stm32f4xx_hal.h"

/* I2C Device Address (Shifted left for HAL 7-bit addressing)
   The MPU6050's 7-bit I2C address is 0x68. For STM32 HAL functions, we left-shift it by 1 to accommodate the read/write bit. */
#define MPU6050_I2C_ADDR    0x68 << 1

/* Register Map
   The MPU6050 has a variety of registers for configuration and data retrieval. Below are some key registers used in this driver. */
#define REG_CONFIG          0x1A
#define REG_GYRO_CONFIG     0x1B
#define REG_ACCEL_CONFIG    0x1C   
#define REG_ACCEL_XOUT_H    0x3B
#define REG_PWR_MGMT_1      0x6B

/* Calibration / Sensitivity Divisors
   These values are used to convert raw sensor data into meaningful physical units. */
#define ACCEL_SENS_2G      16384.0f
#define GYRO_SENS_250DPS   131.0f

/* Structured Telemtry Data Payload 
   This structure holds both the raw and processed data from the MPU6050 sensor. It includes accelerometer, gyroscope, and temperature readings. */
typedef struct {
    int16_t raw_ax, raw_ay, raw_az;
    int16_t raw_temp;
    int16_t raw_gx, raw_gy, raw_gz;

    float ax, ay, az;
    float temperature;
    float gx, gy, gz;
} GY521_Data_t;

/* Driver Functions 
   These functions provide an interface to initialize the MPU6050 sensor and read data from it. */
HAL_StatusTypeDef GY521_Init_Advanced(I2C_HandleTypeDef *hi2c);
HAL_StatusTypeDef GY521_Read_Burst(I2C_HandleTypeDef *hi2c, GY521_Data_t *data);

#endif // CUSTOM_DRIVRS_GY521_DRIVER_H