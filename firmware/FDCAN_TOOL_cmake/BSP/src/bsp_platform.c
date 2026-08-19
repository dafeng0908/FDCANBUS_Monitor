#include "bsp_platform.h"

#include "main.h"

bsp_platform_status_t bsp_platform_initialize(void)
{
  if (mx_system_init() != SYSTEM_OK)
  {
    return BSP_PLATFORM_STATUS_INITIALIZATION_FAILED;
  }

  return BSP_PLATFORM_STATUS_OK;
}
