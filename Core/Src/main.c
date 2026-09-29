/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2026 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include <stdint.h>

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
TIM_HandleTypeDef htim3;

UART_HandleTypeDef huart2;

/* USER CODE BEGIN PV */

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_TIM3_Init(void);
static void MX_USART2_UART_Init(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{

  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_TIM3_Init();
  MX_USART2_UART_Init();
  /* USER CODE BEGIN 2 */
  uint16_t last_1s_toggle_time = 0; // Variable to store the last toggle time for LED_1
  uint16_t last_2s_toggle_time = 0; // Variable to store the last toggle time for LED_1 and LED_2
  uint16_t last_3s_toggle_time = 0; // Variable to store the last toggle time for LED_1, LED_2, and LED_3

  HAL_TIM_Base_Start(&htim3); // Start the timer
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */

  while (1)
  {
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */

    uint16_t current_time = __HAL_TIM_GET_COUNTER(&htim3); // Get the current timer count

    
    //Button press detection and LED control: Method 3
    //Press Button_1 to turn on LED_1 every 1 second
    if (HAL_GPIO_ReadPin(Button_1_GPIO_Port, Button_1_Pin) == GPIO_PIN_SET)
    {
      // Tell RealTerm that Button_1 is pressed
      uint8_t button_1_pressed_msg[] = "Button_1 is pressed\r\n";
      HAL_UART_Transmit(&huart2, button_1_pressed_msg, sizeof(button_1_pressed_msg) - 1, 100);

      // Button_1 is pressed, toggle LED_1 every  second
      if ((uint16_t)(current_time - last_1s_toggle_time) >= 1000)
      {
        HAL_GPIO_TogglePin(LED_1_GPIO_Port, LED_1_Pin); // Toggle LED_1 state
        last_1s_toggle_time = current_time; // Update the last toggle time for LED_1
      }

      // Tell RealTerm if LED is ON or OFF
      if (HAL_GPIO_ReadPin(LED_1_GPIO_Port, LED_1_Pin) == GPIO_PIN_SET)
      {
        uint8_t led_1_on_msg[] = "LED_1 is ON\r\n";
        HAL_UART_Transmit(&huart2, led_1_on_msg, sizeof(led_1_on_msg) - 1, 100);
      }
      else
      {
        uint8_t led_1_off_msg[] = "LED_1 is OFF\r\n";
        HAL_UART_Transmit(&huart2, led_1_off_msg, sizeof(led_1_off_msg) - 1, 100);
      }
    }

    // Press Button_2 to turn on LED_1 and LED_2 every 2 seconds
    if (HAL_GPIO_ReadPin(Button_2_GPIO_Port, Button_2_Pin) == GPIO_PIN_SET)
    {
      // Tell RealTerm that Button_2 is pressed
      uint8_t button_2_pressed_msg[] = "Button_2 is pressed\r\n";
      HAL_UART_Transmit(&huart2, button_2_pressed_msg, sizeof(button_2_pressed_msg) - 1, 100);

      // Button_2 is pressed, toggle LED_1 and LED_2 every 2 seconds
      if ((uint16_t)(current_time - last_2s_toggle_time) >= 2000)
      {
        HAL_GPIO_TogglePin(LED_1_GPIO_Port, LED_1_Pin); // Toggle LED_1 state
        HAL_GPIO_TogglePin(LED_2_GPIO_Port, LED_2_Pin); // Toggle LED_2 state
        last_2s_toggle_time = current_time; // Update the last toggle time for LED_1 and LED_2
      }

      // Tell RealTerm if LED_2 is ON or OFF
      if (HAL_GPIO_ReadPin(LED_2_GPIO_Port, LED_2_Pin) == GPIO_PIN_SET)
      {
        uint8_t led_2_on_msg[] = "LED_2 is ON\r\n";
        HAL_UART_Transmit(&huart2, led_2_on_msg, sizeof(led_2_on_msg) - 1, 100);
      }
      else
      {
        uint8_t led_2_off_msg[] = "LED_2 is OFF\r\n";
        HAL_UART_Transmit(&huart2, led_2_off_msg, sizeof(led_2_off_msg) - 1, 100);
      }
    }

    // Press Button_3 to turn on LED_1, LED_2, and LED_3 every 3 seconds
    if (HAL_GPIO_ReadPin(Button_3_GPIO_Port, Button_3_Pin) == GPIO_PIN_SET)
    {
      // Tell RealTerm that Button_3 is pressed
      uint8_t button_3_pressed_msg[] = "Button_3 is pressed\r\n";
      HAL_UART_Transmit(&huart2, button_3_pressed_msg, sizeof(button_3_pressed_msg) - 1, 100);

      // Button_3 is pressed, toggle LED_1, LED_2, and LED_3 every 3 seconds
      if ((uint16_t)(current_time - last_3s_toggle_time) >= 3000)
      {
        HAL_GPIO_TogglePin(LED_1_GPIO_Port, LED_1_Pin); // Toggle LED_1 state
        HAL_GPIO_TogglePin(LED_2_GPIO_Port, LED_2_Pin); // Toggle LED_2 state
        HAL_GPIO_TogglePin(LED_3_GPIO_Port, LED_3_Pin); // Toggle LED_3 state
        last_3s_toggle_time = current_time; // Update the last toggle time for LED_1, LED_2, and LED_3
      }

      // Tell RealTerm if LED_3 is ON or OFF
      if (HAL_GPIO_ReadPin(LED_3_GPIO_Port, LED_3_Pin) == GPIO_PIN_SET)
      {
        uint8_t led_3_on_msg[] = "LED_3 is ON\r\n";
        HAL_UART_Transmit(&huart2, led_3_on_msg, sizeof(led_3_on_msg) - 1, 100);
      }
      else
      {
        uint8_t led_3_off_msg[] = "LED_3 is OFF\r\n";
        HAL_UART_Transmit(&huart2, led_3_off_msg, sizeof(led_3_off_msg) - 1, 100);
      }
    }

    /*
    //Button press detection and LED control: Method 2
    //Press Button_1 to turn on LED_1 every 1 second
    if (HAL_GPIO_ReadPin(Button_1_GPIO_Port, Button_1_Pin) == GPIO_PIN_SET)
    {
      // Check if 1 second has passed since the last toggle
      if (__HAL_TIM_GET_COUNTER(&htim3) >= 100)
      {
        HAL_GPIO_TogglePin(LED_1_GPIO_Port, LED_1_Pin); // Toggle LED_1 state
        __HAL_TIM_SET_COUNTER(&htim3, 0); // Reset the timer counter
      }
    }

    //Press Button_2 to turn on LED_1 and LED_2  every 5 seconds
    if (HAL_GPIO_ReadPin(Button_2_GPIO_Port, Button_2_Pin) == GPIO_PIN_SET)
    {
      // Check if 5 seconds have passed since the last toggle
      if (__HAL_TIM_GET_COUNTER(&htim3) >= 500)
      {
        HAL_GPIO_TogglePin(LED_1_GPIO_Port, LED_1_Pin); // Toggle LED_1 state
        HAL_GPIO_TogglePin(LED_2_GPIO_Port, LED_2_Pin); // Toggle LED_2 state
        __HAL_TIM_SET_COUNTER(&htim3, 0); // Reset the timer counter
      }
    }

    // Press Button_3 to turn on LED_1, LED_2 and LED_3 every 10 seconds
    if (HAL_GPIO_ReadPin(Button_3_GPIO_Port, Button_3_Pin) == GPIO_PIN_SET)
    {
      // Check if 10 seconds have passed since the last toggle
      if (__HAL_TIM_GET_COUNTER(&htim3) >= 1000)
      {
        HAL_GPIO_TogglePin(LED_1_GPIO_Port, LED_1_Pin); // Toggle LED_1 state
        HAL_GPIO_TogglePin(LED_2_GPIO_Port, LED_2_Pin); // Toggle LED_2 state
        HAL_GPIO_TogglePin(LED_3_GPIO_Port, LED_3_Pin); // Toggle LED_3 state
        __HAL_TIM_SET_COUNTER(&htim3, 0); // Reset the timer counter
      }
    }
      */


    /*
    // Button press detection and LED control: Method 1
    // Press B1 to turn on LD2
    if (HAL_GPIO_ReadPin(B1_GPIO_Port, B1_Pin) == GPIO_PIN_SET)
    {
      HAL_GPIO_WritePin(LD2_GPIO_Port, LD2_Pin, GPIO_PIN_SET);
    }
    else
    {
      HAL_GPIO_WritePin(LD2_GPIO_Port, LD2_Pin, GPIO_PIN_RESET);
    }

    // Press Button_1 to turn on LED_1
    if (HAL_GPIO_ReadPin(Button_1_GPIO_Port, Button_1_Pin) == GPIO_PIN_SET)
    {
      HAL_GPIO_WritePin(LED_1_GPIO_Port, LED_1_Pin, GPIO_PIN_SET);
    }
    else
    {
      HAL_GPIO_WritePin(LED_1_GPIO_Port, LED_1_Pin, GPIO_PIN_RESET);
    }

    // Press Button_2 to turn on LED_2
    if (HAL_GPIO_ReadPin(Button_2_GPIO_Port, Button_2_Pin) == GPIO_PIN_SET)
    {
      HAL_GPIO_WritePin(LED_2_GPIO_Port, LED_2_Pin, GPIO_PIN_SET);
    }
    else
    {
      HAL_GPIO_WritePin(LED_2_GPIO_Port, LED_2_Pin, GPIO_PIN_RESET);
    }

    // Press Button_3 to turn on LED_3
    if (HAL_GPIO_ReadPin(Button_3_GPIO_Port, Button_3_Pin) == GPIO_PIN_SET)
    {
      HAL_GPIO_WritePin(LED_3_GPIO_Port, LED_3_Pin, GPIO_PIN_SET);
    }
    else
    {
      HAL_GPIO_WritePin(LED_3_GPIO_Port, LED_3_Pin, GPIO_PIN_RESET);
    }
      */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
  RCC_OscInitStruct.PLL.PLLM = 8;
  RCC_OscInitStruct.PLL.PLLN = 96;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
  RCC_OscInitStruct.PLL.PLLQ = 4;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV2;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_1) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief TIM3 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM3_Init(void)
{

  /* USER CODE BEGIN TIM3_Init 0 */

  /* USER CODE END TIM3_Init 0 */

  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};

  /* USER CODE BEGIN TIM3_Init 1 */

  /* USER CODE END TIM3_Init 1 */
  htim3.Instance = TIM3;
  htim3.Init.Prescaler = 48000-1;
  htim3.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim3.Init.Period = 65536-1;
  htim3.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim3.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_Base_Init(&htim3) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim3, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim3, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM3_Init 2 */

  /* USER CODE END TIM3_Init 2 */

}

/**
  * @brief USART2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART2_UART_Init(void)
{

  /* USER CODE BEGIN USART2_Init 0 */

  /* USER CODE END USART2_Init 0 */

  /* USER CODE BEGIN USART2_Init 1 */

  /* USER CODE END USART2_Init 1 */
  huart2.Instance = USART2;
  huart2.Init.BaudRate = 115200;
  huart2.Init.WordLength = UART_WORDLENGTH_8B;
  huart2.Init.StopBits = UART_STOPBITS_1;
  huart2.Init.Parity = UART_PARITY_NONE;
  huart2.Init.Mode = UART_MODE_TX_RX;
  huart2.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart2.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart2) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART2_Init 2 */

  /* USER CODE END USART2_Init 2 */

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};
  /* USER CODE BEGIN MX_GPIO_Init_1 */

  /* USER CODE END MX_GPIO_Init_1 */

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOH_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOA, LD2_Pin|LED_2_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOC, LED_3_Pin|LED_1_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin : B1_Pin */
  GPIO_InitStruct.Pin = B1_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(B1_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pins : LD2_Pin LED_2_Pin */
  GPIO_InitStruct.Pin = LD2_Pin|LED_2_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

  /*Configure GPIO pin : Button_2_Pin */
  GPIO_InitStruct.Pin = Button_2_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_PULLDOWN;
  HAL_GPIO_Init(Button_2_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pins : LED_3_Pin LED_1_Pin */
  GPIO_InitStruct.Pin = LED_3_Pin|LED_1_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

  /*Configure GPIO pin : Button_1_Pin */
  GPIO_InitStruct.Pin = Button_1_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_PULLDOWN;
  HAL_GPIO_Init(Button_1_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pin : Button_3_Pin */
  GPIO_InitStruct.Pin = Button_3_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(Button_3_GPIO_Port, &GPIO_InitStruct);

  /* USER CODE BEGIN MX_GPIO_Init_2 */

  /* USER CODE END MX_GPIO_Init_2 */
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}
#ifdef USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
