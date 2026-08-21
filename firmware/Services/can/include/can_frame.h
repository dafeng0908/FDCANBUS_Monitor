#ifndef CAN_FRAME_H
#define CAN_FRAME_H

#include <stdbool.h>
#include <stdint.h>

#define CAN_FRAME_MAX_PAYLOAD_BYTES (64U)

typedef enum
{
  CAN_FRAME_IDENTIFIER_STANDARD = 0,
  CAN_FRAME_IDENTIFIER_EXTENDED
} can_frame_identifier_type_t;

typedef struct
{
  uint32_t identifier;
  can_frame_identifier_type_t identifier_type;
  uint8_t payload_length;
  uint8_t payload[CAN_FRAME_MAX_PAYLOAD_BYTES];
  bool bit_rate_switch;
} can_frame_t;

#endif /* CAN_FRAME_H */
