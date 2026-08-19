# Description
The host protocol is not defined during bootstrap. Before implementation, define message
framing, versioning, error handling, and compatibility rules in this document and link the
corresponding execution plan and tests.

# Protocol architecture
version 0.0.1 loopback, receive any msaaage(id and data), sent the same id and data +1, ex. device 01 sent 001 00000000, we sent back 001 00000001
