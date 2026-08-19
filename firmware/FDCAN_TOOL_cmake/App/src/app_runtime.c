#include "app_runtime.h"

#include "can_service.h"

void app_runtime_initialize(void)
{
  can_service_initialize();
}

void app_runtime_poll(void)
{
  can_frame_t frame;

  (void)can_service_try_receive(&frame);
}
