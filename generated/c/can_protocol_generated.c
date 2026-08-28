/* AUTO GENERATED FILE. DO NOT EDIT.
 * Source: protocol/protocol.json
 * Source SHA256: 3bf6f9382c14057e87c4e97c5bd8e992e111a59f50792bc44065f2a971964d91
 */
#include "can_protocol_generated.h"

static uint32_t protocol_read_le(const uint8_t *data, uint8_t length)
{
    uint32_t value = 0u;
    uint8_t index;
    for (index = 0u; index < length; ++index)
    {
        value |= ((uint32_t)data[index]) << (8u * index);
    }
    return value;
}

static void protocol_write_le(uint8_t *data, uint8_t length, uint32_t value)
{
    uint8_t index;
    for (index = 0u; index < length; ++index)
    {
        data[index] = (uint8_t)(value >> (8u * index));
    }
}

static int32_t protocol_sign_extend(uint32_t value, uint8_t bits)
{
    if ((bits < 32u) && ((value & (1u << (bits - 1u))) != 0u))
    {
        value |= (~0u) << bits;
    }
    return (int32_t)value;
}

bool can_bms_status_encode(const can_bms_status_t *message, uint8_t data[CAN_BMS_STATUS_DLC])
{
    uint8_t index;
    if ((message == 0) || (data == 0))
    {
        return false;
    }
    for (index = 0u; index < CAN_BMS_STATUS_DLC; ++index)
    {
        data[index] = 0u;
    }
    {
        const float physical = message->pack_voltage;
        if ((physical < 0.0f) || (physical > 1000.0f))
        {
            return false;
        }
        const int32_t raw_signed = (int32_t)((physical - 0.0f) / 0.1f);
        protocol_write_le(&data[0], 2u, (uint32_t)raw_signed);
    }
    {
        const float physical = message->pack_current;
        if ((physical < -3200.0f) || (physical > 3200.0f))
        {
            return false;
        }
        const int32_t raw_signed = (int32_t)((physical - 0.0f) / 0.1f);
        protocol_write_le(&data[2], 2u, (uint32_t)raw_signed);
    }
    {
        const float physical = message->soc;
        if ((physical < 0.0f) || (physical > 100.0f))
        {
            return false;
        }
        const int32_t raw_signed = (int32_t)((physical - 0.0f) / 0.5f);
        protocol_write_le(&data[4], 1u, (uint32_t)raw_signed);
    }
    return true;
}

bool can_bms_status_decode(const uint8_t data[CAN_BMS_STATUS_DLC], can_bms_status_t *message)
{
    if ((data == 0) || (message == 0))
    {
        return false;
    }
    message->pack_voltage = ((float)protocol_read_le(&data[0], 2u) * 0.1f) + 0.0f;
    message->pack_current = ((float)protocol_sign_extend(protocol_read_le(&data[2], 2u), 16u) * 0.1f) + 0.0f;
    message->soc = ((float)protocol_read_le(&data[4], 1u) * 0.5f) + 0.0f;
    return true;
}
