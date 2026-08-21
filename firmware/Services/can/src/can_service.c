#include "can_service.h"

static can_service_status_t can_service_status;

void can_service_initialize(void)
{
  can_service_status.state = CAN_SERVICE_STATE_NOT_READY;
  can_service_status.last_error = CAN_SERVICE_ERROR_NONE;
  can_service_status.rx_dropped_frames = 0U;
  can_service_status.error_events = 0U;
}

bool can_service_try_receive(can_frame_t *frame)
{
  (void)frame;

  return false;
}

can_service_status_t can_service_get_status(void)
{
  return can_service_status;
}
