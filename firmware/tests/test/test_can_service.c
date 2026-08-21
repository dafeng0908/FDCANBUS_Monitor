#include "unity.h"

#include "can_service.h"


void setUp(void)
{
}


void tearDown(void)
{
}


void test_initialize_sets_the_not_ready_status(void)
{
  can_service_initialize();

  can_service_status_t status = can_service_get_status();

  TEST_ASSERT_EQUAL(CAN_SERVICE_STATE_NOT_READY, status.state);
  TEST_ASSERT_EQUAL(CAN_SERVICE_ERROR_NONE, status.last_error);
  TEST_ASSERT_EQUAL_UINT32(0U, status.rx_dropped_frames);
  TEST_ASSERT_EQUAL_UINT32(0U, status.error_events);
}


void test_try_receive_returns_false_when_the_queue_is_empty(void)
{
  can_frame_t frame = {0};

  TEST_ASSERT_FALSE(can_service_try_receive(&frame));
}
