import threading
import time
from datetime import datetime
import uuid
import concurrent.futures
from collections import deque 

# This is the shared data class.
class PrintJob:
    """
    Represents a single print job with its metadata.
    This class stores details like user, title, priority, submission time,
    unique ID, current status, and simulated waiting time.
    """
    def __init__(self, user_id: str, title: str, priority: int = 5):
        
        self.job_id = str(uuid.uuid4())# A unique identifier for the print job, generated using UUID.
        self.user_id = user_id
        self.title = title # The title of the job.
        self.priority = priority # The priority of the job (lower number = higher urgency).
        self.created_at = datetime.now() # Timestamp when the job object was created.
        self.status = "waiting" # The current status of the job.
        self.waiting_time = 0.0 # Waiting initially set to 0 seconds

    def __str__(self):
        """
        String representation for a PrintJob
        It provides a concise summary of the job's key attributes.
        """
        return (f"Job ID: {self.job_id[:8]}..., Name: '{self.title}', User: {self.user_id}, "
                f"Priority: {self.priority}, Submitted: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}, "
                f"Status: {self.status}, Waiting: {self.waiting_time:.1f}s")


class PrintQueueManager:
    """
    Manages a print queue system, handling job submissions, prioritization,
    and concurrent operations in a simulated environment. It uses a circular
    array structure for the queue.
    """
    def __init__(self, capacity: int = 10, expiry_time: int = 300, aging_interval: int = 5):
        # --- Core Queue Attributes ---
        
        self.capacity = capacity # Maximum number of jobs the queue can hold.
        self.queue = [None] * capacity # The underlying circular array storage for print jobs.
        self.front = 0  # Index of the first (oldest) job in the queue.
        self.rear = 0  # Index where the next job will be added.
        self.size = 0 # Current number of jobs in the queue.
        self.lock = threading.Lock() # A threading.Lock to ensure thread-safe access to the queue for modifications.

        # --- Simulation Attributes ---
        self.current_simulation_time = 0 # Tracks the current simulated time in seconds.
        self.default_expiry_time_seconds = expiry_time # Default time in seconds for job expiry.
        self.priority_aging_interval = aging_interval # Interval in seconds at which job priorities are aged (made more urgent).

        print(f"[{self.current_simulation_time}s] INFO: PrintQueueManager initialized with capacity={capacity}, "
              f"expiry={expiry_time}s, aging_interval={aging_interval}s.")


    # ======================================================================
    # MODULE 1: CORE QUEUE MANAGEMENT
    # Owner: RAY KINGORI
    # Goal: Manage the fundamental enqueue and dequeue operations.
    # ======================================================================

    def is_full(self) -> bool:
        """
        Checks if the print queue is full.
        Returns:
            bool: True if the queue is full, False otherwise.
        """
        return self.size == self.capacity

    def is_empty(self) -> bool:
        """
        Checks if the print queue is empty.
        Returns:
            bool: True if the queue is empty, False otherwise.
        """
        return self.size == 0

    def enqueue_job(self, user_id: str, title: str, priority: int = 5) -> bool:
        """
        Adds a new print job to the back of the queue. Its also thread-safe.
            bool: True if the job was successfully enqueued, False if the queue is full.
        """
        with self.lock: # Acquire lock to ensure thread safety during queue modification
            if self.is_full():
                print(f"[{self.current_simulation_time}s] ERROR: Queue is full. Cannot add job '{title}'.")
                return False

            new_job = PrintJob(user_id, title, priority)
            self.queue[self.rear] = new_job
            self.rear = (self.rear + 1) % self.capacity
            self.size += 1
            print(f"[{self.current_simulation_time}s] INFO: Job '{new_job.title}' (ID: {new_job.job_id[:8]}...) added to queue. (Size: {self.size}/{self.capacity})")
            return True

    def print_job(self) -> PrintJob | None:
        """
        Finds, removes, and "prints" the highest priority job from the queue (lower number = higher urgency).
        Returns:
            PrintJob | None: The PrintJob object that was printed, or None if the queue is empty.
        """
        with self.lock: 
            if self.is_empty():
                print(f"[{self.current_simulation_time}s] INFO: No jobs in queue to print.")
                return None

            
            active_jobs = [self.queue[(self.front + i) % self.capacity] for i in range(self.size) if self.queue[(self.front + i) % self.capacity] is not None]

            
            if not active_jobs:
                print(f"[{self.current_simulation_time}s] INFO: No valid jobs found in queue after internal check.")
                return None

            
            active_jobs.sort(key=lambda job: (job.priority, -job.waiting_time))

            # The job to print is the first item in the sorted list.
            job_to_print = active_jobs.pop(0) # Get and remove the highest priority job from the temporary list

            # Rebuild the circular queue with the remaining jobs after popping the active job.
            self.queue = [None] * self.capacity # Reset the queue array
            self.front = 0 # Reset front pointer
            self.rear = 0 # Reset rear pointer
            self.size = 0 # Reset size

            for job in active_jobs:
                # Re-add each remaining job to the queue, preserving relative order.
                self.queue[self.rear] = job
                self.rear = (self.rear + 1) % self.capacity
                self.size += 1

            # Update the status of the printed job.
            job_to_print.status = "completed"
            print(f"[{self.current_simulation_time}s] INFO: Printing job: '{job_to_print.title}' "
                  f"(ID: {job_to_print.job_id[:8]}..., Priority: {job_to_print.priority}, "
                  f"Wait Time: {job_to_print.waiting_time:.1f}s). Current queue size: {self.size}.")
            return job_to_print


    # ======================================================================
    # MODULE 2: PRIORITY & AGING SYSTEM
    # Owner: JAKES KISILU
    # Goal: Increase job priority over time.
    # ======================================================================

    def apply_priority_aging(self):
        """
        Increases the priority of jobs that have been waiting for a long time.
        """
        print(f"[{self.current_simulation_time}s] INFO: Applying priority aging...")
        with self.lock: # Ensure thread safety while iterating and modifying jobs
            for i in range(self.size):
                idx = (self.front + i) % self.capacity
                job = self.queue[idx]
                
                # Ensure the job exists and is currently waiting before applying aging.
                if job and job.status == "waiting":
                    if job.waiting_time > 0 and int(job.waiting_time) % self.priority_aging_interval == 0:
                        # Decrease priority (lower number = higher urgency), ensuring it doesn't go below 1.
                        old_priority = job.priority
                        job.priority = max(1, job.priority - 1)
                        if job.priority < old_priority: # Only print if priority actually changed
                            print(f"[{self.current_simulation_time}s] INFO: Job '{job.title}' (ID: {job.job_id[:8]}...) priority aged from {old_priority} to {job.priority}.")
        print(f"[{self.current_simulation_time}s] INFO: Priority aging check complete.")


    # ======================================================================
    # MODULE 3: JOB EXPIRY & CLEANUP
    # Owner: DAVIS MUTUA
    # Goal: Remove jobs that have waited too long.
    # ======================================================================

    def remove_expired_jobs(self):
        """
        Checks for and removes jobs that have exceeded their configured expiry time.
        """
        print(f"[{self.current_simulation_time}s] INFO: Checking for expired jobs...")
        with self.lock: # Ensure thread safety during queue modification
            jobs_to_keep = []
            expired_jobs_count = 0

            # Iterate through all current jobs in the queue
            for i in range(self.size):
                idx = (self.front + i) % self.capacity
                job = self.queue[idx]
                
                if job is None:
                    continue

                # Check if the job's waiting_time has exceeded the default expiry time
                is_expired = job.waiting_time >= self.default_expiry_time_seconds
                
                if is_expired and job.status == "waiting": # Only expire jobs that are currently waiting
                    self._notify_expiry(job)
                    expired_jobs_count += 1
                else:
                    # If not expired (e.g., printing/completed), keep it.
                    jobs_to_keep.append(job)
            
            # If any jobs were expired, rebuild the queue with only the jobs to keep.
            if expired_jobs_count > 0:
                self.queue = [None] * self.capacity # Reset the queue array
                self.front = 0 # Reset front pointer
                self.rear = 0 # Reset rear pointer
                self.size = 0 # Reset size

                for job in jobs_to_keep:
                    # Re-add each non-expired job to the queue.
                    self.queue[self.rear] = job
                    self.rear = (self.rear + 1) % self.capacity
                    self.size += 1
                print(f"[{self.current_simulation_time}s] INFO: --- {expired_jobs_count} job(s) removed due to expiry. Current queue size: {self.size}. ---")
            else:
                print(f"[{self.current_simulation_time}s] INFO: No expired jobs to remove.")


    def _notify_expiry(self, job: PrintJob):
        """
        Helper method to log that a job has expired.
        Args:
            job (PrintJob): The job object that has expired.
        """
        job.status = "expired"
        print(f"[{self.current_simulation_time}s] WARNING: [JOB EXPIRED] Job '{job.title}' (ID: {job.job_id[:8]}...) for user '{job.user_id}' has expired and been removed from the queue.")


    # ======================================================================
    # MODULE 4: CONCURRENT SUBMISSION HANDLING
    # Owner: AMANI KOROS
    # Goal: Handle simultaneous job submissions safely.
    # ======================================================================

    def handle_simultaneous_submissions(self, jobs_data: list[tuple]) -> list[str]:
        """
        Handles multiple job submissions concurrently using a ThreadPoolExecutor.
        Each job_info tuple should be (user_id, title, priority).
        Args:
            jobs_data (list[tuple]): A list of tuples, where each tuple contains
                                     (user_id, title, priority) for a job.
        Returns:
            list[str]: A list of outcome messages for each submission.
        """
        all_submissions_outcomes = []
        print(f"\n[{self.current_simulation_time}s] INFO: --- Handling simultaneous job submissions ---")
        # Use ThreadPoolExecutor to run enqueue_job calls concurrently.
        # max_workers=5 allows up to 5 submission tasks to run in parallel.
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            
            future_to_job = {executor.submit(self.enqueue_job, user, title, prio): title for user, title, prio in jobs_data}
            
            # Iterate over futures as they complete to collect results or handle exceptions.
            for future in concurrent.futures.as_completed(future_to_job):
                job_title = future_to_job[future]
                try:
                    #result of the enqueue operation (True/False).
                    result = future.result()
                    if result:
                        all_submissions_outcomes.append(f"Successfully processed concurrent submission for '{job_title}'.")
                    else:
                        all_submissions_outcomes.append(f"Failed to process concurrent submission for '{job_title}'.")
                except Exception as exc:
                    print(f"[{self.current_simulation_time}s] ERROR: Concurrent job submission for '{job_title}' raised an exception: {exc}")
                    all_submissions_outcomes.append(f"Concurrent submission for '{job_title}' failed with exception: {exc}")

        print(f"[{self.current_simulation_time}s] INFO: --- All concurrent job submissions processed. ---")
        return all_submissions_outcomes


    # ======================================================================
    # MODULE 5: EVENT SIMULATION & TIME MANAGEMENT
    # Owner: JOLENE SITENEI
    # Goal: Simulate the passage of time and trigger time-based events.
    # ======================================================================

    def tick(self):
        """
        Simulates the passage of one unit of time.
        This function updates the waiting time for all jobs, then triggers
        priority aging and expired job cleanup processes.
        """
        # Increment the simulated current time.
        self.current_simulation_time += 1
        print(f"\n[{self.current_simulation_time}s] INFO: TICK! Simulating 1 second passing.")

        # Update waiting times for all jobs currently in the queue that are in 'waiting' status.
        with self.lock: # Acquire lock before iterating and modifying job properties
            for i in range(self.size):
                idx = (self.front + i) % self.capacity
                job = self.queue[idx]
                if job and job.status == "waiting": # Only update waiting time for jobs that are still waiting
                    job.waiting_time += 1
                    print(f"[{self.current_simulation_time}s] INFO: Job '{job.title}' (ID: {job.job_id[:8]}...) waiting time updated to {job.waiting_time:.1f}s.")

        # Trigger priority aging for jobs.
        self.apply_priority_aging()

        # Trigger cleanup for expired jobs.
        self.remove_expired_jobs()
        print(f"[{self.current_simulation_time}s] INFO: Tick processing complete.")


    # ======================================================================
    # MODULE 6: VISUALIZATION & REPORTING
    # Owner: JEREMIAH SENTOMERO
    # Goal: Display the current queue status in a clear, user-friendly format.
    # ======================================================================

    def show_status(self):
        """
        Prints a formatted, user-friendly snapshot of the current queue status.
        Jobs are displayed sorted by priority (lowest number first) and then
        by waiting time (longest waiting first, for tie-breaking).
        """
        print(f"\n=== Print Queue Status (Time: {self.current_simulation_time}s) ===")
        with self.lock: # Acquire lock to get a consistent snapshot of the queue
            if self.is_empty():
                print("The queue is empty.")
                print("="*80)
                return
            
            # Collect jobs currently in the queue for display.
            # Filter out any None values, though with correct size tracking, there shouldn't be any.
            jobs_to_display = [self.queue[(self.front + i) % self.capacity] for i in range(self.size) if self.queue[(self.front + i) % self.capacity] is not None]

            # Sort jobs for display based on priority and waiting time (same logic as `print_job`).
            jobs_to_display.sort(key=lambda j: (j.priority, -j.waiting_time))

            # Print table header
            print(f"{'ID':<10} | {'User':<8} | {'Title':<20} | {'Prio':<5} | {'Wait (s)':<9} | {'Status':<10} | {'Expiry (s)':<11}")
            print("-" * 100) # Adjusted separator length for new column

            # Print each job's details
            for job in jobs_to_display:
                # Calculate remaining expiry time, showing 0 if already expired or if job is completed.
                # This makes the expiry info more user-friendly.
                remaining_expiry = self.default_expiry_time_seconds - job.waiting_time
                expiry_info = f"{max(0, remaining_expiry):<10.1f}" if job.status == "waiting" else "N/A" # Only show expiry for waiting jobs
                
                print(f"{job.job_id[:8]:<10} | {job.user_id:<8} | {job.title:<20} | {job.priority:<5} | {job.waiting_time:<9.1f} | {job.status:<10} | {expiry_info}")
            
            print("-" * 100) # Adjusted separator length
            print(f"Queue Size: {self.size}/{self.capacity}")
            print("="*80)

    def get_queue_snapshot(self) -> dict:
        """
        Returns a dictionary representing the current state of the queue.
        Returns:
            dict: A dictionary containing the queue snapshot.
        """
        snapshot = {
           'current_time': self.current_simulation_time,
           'queue_size': self.size,
           'queue_capacity': self.capacity,
           'jobs': []
        }

        with self.lock: # Acquire lock to get a consistent snapshot of the queue
            # Iterate through active jobs to add their data to the snapshot
            for i in range(self.size):
                actual_index = (self.front + i) % self.capacity
                job = self.queue[actual_index]
                if job: # Defensive check, ensures we only process valid job objects
                    # Create a dictionary representation of the job for the snapshot
                    job_data = {
                        'job_id': job.job_id,
                        'user_id': job.user_id,
                        'title': job.title,
                        'priority': job.priority,
                        'created_at': job.created_at.isoformat(), # ISO format for datetime for easy parsing
                        'status': job.status,
                        'waiting_time': job.waiting_time
                    }
                    snapshot['jobs'].append(job_data)

        return snapshot
