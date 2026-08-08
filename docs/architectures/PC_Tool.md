# PC tool architecture

The future Qt6 application owns presentation, user actions, and local monitoring views. It
communicates only through a versioned host transport interface and does not import firmware
code or STM32 headers.
