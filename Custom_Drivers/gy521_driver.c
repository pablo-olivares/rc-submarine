#include "gy521_driver.h"
#include "stm32f4xx_hal_def.h"

/** 
 * @brief Initializes the MPU-6050 with advanced g-resolution and low-pass filtering.
 * @param hi2c: Pointer to a HAL I2C handle structure.
 * @return HAL Status
 */
HAL_StatusTypeDef GY521_Init_Advanced(I2C_HandleTypeDef *hi2c)
{
    uint8_t reg_val;
    HAL_StatusTypeDef status;

    // 1. Wake up the MPU6050 by writing 0 to the PWR_MGMT_1 register
    reg_val = 0x00;
    status = HAL_I2C_Mem_Write(hi2c, MPU6050_I2C_ADDR, REG_PWR_MGMT_1, 1, &reg_val, 1, 100);
    if (status != HAL_OK) return status;

    // 2. Set DLPF (Digital Low Pass Filter) to ~44Hz (Configuration 3)
    // Filters out high-frequency inductive thruster motor noise mechanically
    reg_val = 0x03;
    status = HAL_I2C_Mem_Write(hi2c, MPU6050_I2C_ADDR, REG_CONFIG, 1, &reg_val, 1, 100);
    if (status != HAL_OK) return status;

    // 3. Set Gyro Sensitivity to +-250 DPS (Maximum Resolution)
    reg_val = 0x00;
    status = HAL_I2C_Mem_Write(hi2c, MPU6050_I2C_ADDR, REG_GYRO_CONFIG, 1, &reg_val, 1, 100);
    if (status != HAL_OK) return status;

    // 4. Set Accel Sensitivity to +-2g (Matches Python /16384 scaling)
    reg_val = 0x00;
    status = HAL_I2C_Mem_Write(hi2c, MPU6050_I2C_ADDR, REG_ACCEL_CONFIG, 1, &reg_val, 1, 100);
    if (status != HAL_OK) return status;

    return HAL_OK;
}

/** 
 * @brief Executes a fast 14-byte I2C burst read to capture complete raw inertial metrics. 
 * @param hi2c: Pointer to a HAL I2C handle structure.
 * @param data: Pointer to a custom structured data object.
 * @return HAL Status
 */
HAL_StatusTypeDef GY521_Read_Burst(I2C_HandleTypeDef *hi2c, GY521_Data_t *data)
{
    uint8_t buffer[14];
    HAL_StatusTypeDef status;

    // Execute single 14-byte sequential burst read starting at ACCEL_XOUT_H (0x3B)
    status = HAL_I2C_Mem_Read(hi2c, MPU6050_I2C_ADDR, REG_ACCEL_XOUT_H, I2C_MEMADD_SIZE_8BIT, buffer, 14, 100); 
    if (status != HAL_OK) return status;

    // Combine High and Low bytes (Big-Endian configuration native to MPU-6050 registers)
    data->raw_ax = (int16_t)(buffer[0] << 8 | buffer[1]);
    data->raw_ay = (int16_t)(buffer[2] << 8 | buffer[3]);
    data->raw_az = (int16_t)(buffer[4] << 8 | buffer[5]);
    data->raw_temp = (int16_t)(buffer[6] << 8 | buffer[7]);
    data->raw_gx = (int16_t)(buffer[8] << 8 | buffer[9]);
    data->raw_gy = (int16_t)(buffer[10] << 8 | buffer[11]);
    data->raw_gz = (int16_t)(buffer[12] << 8 | buffer[13]);

    // Apply scaling divisors to convert raw registers to standard SI unit representations
    data->ax = (float)data->raw_ax / ACCEL_SENS_2G;
    data->ay = (float)data->raw_ay / ACCEL_SENS_2G;
    data->az = (float)data->raw_az / ACCEL_SENS_2G;

    // Native temperature conversion formula from MPU-6050 specs sheet
    data->temperature = ((float)data->raw_temp / 340.0f) + 36.53f;

    data->gx = (float)data->raw_gx / GYRO_SENS_250DPS;
    data->gy = (float)data->raw_gy / GYRO_SENS_250DPS;
    data->gz = (float)data->raw_gz / GYRO_SENS_250DPS;

    return HAL_OK;
}