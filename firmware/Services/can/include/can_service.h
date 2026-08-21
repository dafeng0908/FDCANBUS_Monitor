#ifndef CAN_SERVICE_H
#define CAN_SERVICE_H

#include <stdbool.h>
#include <stdint.h>

#include "can_frame.h"

#define CAN_SERVICE_RX_QUEUE_CAPACITY (32U)

typedef enum
{
  CAN_SERVICE_STATE_NOT_READY = 0,
  CAN_SERVICE_STATE_READY,
  CAN_SERVICE_STATE_BUS_OFF,
  CAN_SERVICE_STATE_ERROR
} can_service_state_t;

typedef enum
{
  CAN_SERVICE_ERROR_NONE = 0,
  CAN_SERVICE_ERROR_STARTUP,
  CAN_SERVICE_ERROR_CONTROLLER
} can_service_error_t;

typedef struct
{
  can_service_state_t state;
  can_service_error_t last_error;
  uint32_t rx_dropped_frames;
  uint32_t error_events;
} can_service_status_t;

void can_service_initialize(void);
bool can_service_try_receive(can_frame_t *frame);
can_service_status_t can_service_get_status(void);

#endif /* CAN_SERVICE_H */
