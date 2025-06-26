
# DARASA Print Queue Simulation Assignment Overview

This project simulates a print queue system, managing job submissions, prioritization, aging, and concurrency. The codebase is organized into modules, with each module's primary responsibilities assigned to a team member.

## Team Member Modules:

* **👨🏼‍💻Ray (Module 1): Core Queue Management**

  * Manages fundamental `enqueue_job` (adding jobs) and `print_job` (selecting and removing highest priority jobs) operations.

* **👨🏼‍💻Jakes (Module 2): Priority & Aging System**

  * Implements `apply_priority_aging` logic to increase job urgency based on waiting time.

* **👨🏼‍💻Davis (Module 3): Job Expiry & Cleanup**

  * Handles `remove_expired_jobs`, cleaning the queue of jobs that have exceeded their maximum waiting time.

* **👨🏼‍💻Amani (Module 4): Concurrent Submission Handling**

  * Manages `handle_simultaneous_submissions`, allowing multiple jobs to be added to the queue concurrently.

* **👩🏼‍💻Jolene (Module 5): Event Simulation & Time Management**

  * Controls the `tick` mechanism, simulating the passage of time and triggering time-dependent events like aging and expiry checks.

* **👨🏼‍💻Jeremiah (Module 6): Visualization & Reporting**

  * Provides `show_status` functionality to display a clear, formatted snapshot of the queue's current state in a user friendly way.

## How to Run the Simulation:

1. **Save the Files:**

   * Save the code containing `PrintJob` and `PrintQueueManager` classes as `print_queue_manager.py`.

   * Save the simulation orchestration code (with the `main` function) as `main.py`.

   * Ensure both files are in the same directory.

2. **Execute:**

   * Open a terminal or command prompt.

   * Navigate to the directory where you saved the files.

   * Run the simulation using:

     ```
     python main.py
     
     ```

## Necessary Information:

* The `main.py` script drives the simulation by calling methods on a single instance of `PrintQueueManager`.

* All queue operations (`enqueue`, `print_job`, `aging`, `expiry`) are **thread-safe** to prevent data corruption during concurrent access.

* The simulation provides console output at each step, detailing job additions, removals, priority changes, and queue status.