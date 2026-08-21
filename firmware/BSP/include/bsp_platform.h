#ifndef BSP_PLATFORM_H
#define BSP_PLATFORM_H

typedef enum
{
  BSP_PLATFORM_STATUS_OK = 0,
  BSP_PLATFORM_STATUS_INITIALIZATION_FAILED
} bsp_platform_status_t;

/* This function owns generated platform initialisation and its HAL dependency. */
bsp_platform_status_t bsp_platform_initialize(void);

#endif /* BSP_PLATFORM_H */
