/* AUTO GENERATED FILE. DO NOT EDIT.
 * Source: protocol/protocol.json
 * Source SHA256: 3bf6f9382c14057e87c4e97c5bd8e992e111a59f50792bc44065f2a971964d91
 */
#ifndef CAN_PROTOCOL_GENERATED_H
#define CAN_PROTOCOL_GENERATED_H

#include <stdbool.h>
#include <stdint.h>

#define CAN_BMS_STATUS_ID (0x180u)
#define CAN_BMS_STATUS_DLC (8u)

typedef struct
{
    float pack_voltage;
    float pack_current;
    float soc;
} can_bms_status_t;

bool can_bms_status_encode(const can_bms_status_t *message, uint8_t data[CAN_BMS_STATUS_DLC]);
bool can_bms_status_decode(const uint8_t data[CAN_BMS_STATUS_DLC], can_bms_status_t *message);

#endif /* CAN_PROTOCOL_GENERATED_H */
