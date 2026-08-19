# file-format: 1.0.0
if(CMAKE_BUILD_TYPE STREQUAL "debug_GCC_NUCLEO-C542RC")
  target_sources(${CMAKE_PROJECT_NAME} PRIVATE
    main.c
    main.h
    ../BSP/src/bsp_platform.c
    ../Services/can/src/can_service.c
    ../App/src/app_runtime.c
  )
  target_include_directories(${CMAKE_PROJECT_NAME} PRIVATE
    ${CMAKE_SOURCE_DIR}
    ../BSP/include
    ../Services/can/include
    ../App/include
  )
endif()
