
# creating a PrintQueueManager instance and calling its methods.

from print_queue_manager import PrintQueueManager
import time

def main():
    """
    Main function to set up and run a condensed print queue simulation.
    This version directly calls methods on the PrintQueueManager instance
    based on a defined sequence of events.
    """
    print("INFO: main() function started for Print Queue Simulation.")
    # Note:
    #   capacity: Maximum number of jobs the queue can hold.
    #   expiry_time: Simulated time in seconds after which a waiting job expires.
    #   aging_interval: Simulated time in seconds after which a job's priority increases.
    pq_manager = PrintQueueManager(capacity=5, expiry_time=60, aging_interval=10)
    print("INFO: PrintQueueManager instance created.")

    # Define a streamlined sequence of events for the simulation.
    # Each event is a tuple: (event_type, *args).
    # The `main` function now directly orchestrates these events,
    # replacing the `run_simulation` method from the PrintQueueManager.
    simulation_events = [
        ("comment", "--- Phase 1: Initial Enqueues & Queue Status ---"),
        ("enqueue", "Amani ", "Document A (P3)", 3), # Enqueue with priority 3
        ("enqueue", "Jeremiah ", "Document B (P1)", 1),   # Enqueue with highest priority 1
        ("enqueue", "Davis ", "Document C (P5)", 5),# Enqueue with lowest priority 5
        ("show_status",), # Display the initial queue state

        ("comment", "\n--- Phase 2: Time Progression, Aging, & First Print ---"),
        ("tick",), # Simulate 1 second passing. This will update waiting times.
        ("tick",), # Simulate another 1 second.
        ("tick",), # ...
        ("tick",),
        ("tick",), # Total 5 ticks. This should trigger priority aging for some jobs if wait time conditions met.
        ("show_status",),
        ("print_job",), # Print the highest priority job (should be Bob's - Document B)
        ("show_status",),

        ("comment", "\n--- Phase 3: Concurrent Submissions ---"),
        ("simultaneous_submit", [ # Simulate multiple users submitting jobs at the same time
            ("Ray ", "Document D (P4)", 4),
            ("Jakes ", "Document E (P2)", 2),
            ("Jolene ", "Document F (P5)", 5),
        ]),
        ("show_status",),

        ("comment", "\n--- Phase 4: Extended Time & Job Expiry ---"),
        # Simulate significant time passing to trigger job expiry.
        # Since each 'tick' is 1 second, 55 ticks will bring total simulation time to 60s+ for older jobs.
        *[("tick",) for _ in range(55)], # Simulate 55 additional seconds
        ("show_status",), # Display status after time has passed, expecting some jobs to expire.

        ("comment", "\n--- Phase 5: Final Prints & Empty Queue ---"),
        ("print_job",), # Print next highest priority job
        ("show_status",),
        ("print_job",), # Print next highest priority job
        ("show_status",),
        ("print_job",), # Print next highest priority job
        ("show_status",),

        ("comment", "\n--- Phase 6: Final Check (Empty Queue) ---"),
        ("tick",), # A final tick to ensure no issues with empty queue.
        ("show_status",),
    ]
    print("INFO: Simulation events defined.")

    # Process each event in the simulation sequence.
    for i, (event_type, *args) in enumerate(simulation_events):
        print(f"\n--- Processing Event {i+1}: {event_type.replace('_', ' ').title()} ---")
        # time.sleep(0.1) # Optional: Uncomment to slow down simulation output for easier reading.

        # Use if-elif-else to call the appropriate method on the pq_manager instance.
        if event_type == "enqueue":
            # Arguments for enqueue: user_id, title, priority
            pq_manager.enqueue_job(*args)
        elif event_type == "tick":
            # The tick method in PrintQueueManager now manages its own time increment (1 second per call).
            pq_manager.tick()
        elif event_type == "print_job":
            pq_manager.print_job()
        elif event_type == "show_status":
            pq_manager.show_status()
        elif event_type == "simultaneous_submit":
            # Arguments for simultaneous_submit: list of (user_id, title, priority) tuples
            pq_manager.handle_simultaneous_submissions(*args)
        elif event_type == "comment":
            # Simply print the comment string provided in args.
            print(f"\n{args[0]}")
        else:
            print(f"ERROR: Unknown event type encountered: {event_type}")
        print(f"INFO: Finished event {i+1}. Current simulation time: {pq_manager.current_simulation_time}s.")

    print("\n--- Print Queue Simulation Complete ---")
    print("INFO: main() function finished.")

# This ensures the main() function is called only when the script is executed directly,
# not when imported as a module.
if __name__ == "__main__":
    print("INFO: Script execution started.")
    main()
    print("INFO: Script execution finished.")
