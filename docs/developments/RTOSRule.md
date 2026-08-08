# RTOS rules

ISR handlers must not block or allocate memory. Use the designated ISR-safe queue or
notification APIs to hand work to tasks, and document the required priority and latency.
