import threading
import time
from datetime import datetime
import uuid
import concurrent.futures

# This is a shared data class. It holds all the information for a single print job.
class PrintJob:
    """Represents a single print job with its metadata."""
    def __init__(self, user_id: str, title: str, priority: int):
        self.job_id = str(uuid.uuid4())
        self.user_id = user_id
        self.title = title
        self.priority = priority
        self.created_at = datetime.now()
        self.status = "waiting"
        self.waiting_time = 0.0
        self.current_time=0

class PrintQueueManager:
    """
    Manages a print queue system, handling job submissions, prioritization,
    and concurrent operations in a simulated environment.
    """
    def __init__(self, capacity: int, expiry_time: int, aging_interval: int):
        # --- Core Attributes ---
        self.capacity = capacity
        self.queue = [None] * capacity
        self.front = 0
        self.rear = 0
        self.size = 0
        self.lock = threading.Lock()

        # --- Simulation Attributes ---
        self.current_simulation_time = 0
        self.default_expiry_time_seconds = expiry_time
        self.priority_aging_interval = aging_interval


    # ======================================================================
    # MODULE 1: CORE QUEUE MANAGEMENT (Owner: Member 1)
    # Goal: Manage the fundamental enqueue and dequeue operations.
    # ======================================================================

    def is_full(self) -> bool:
        """Checks if the print queue is full."""
        return self.size == self.capacity

    def is_empty(self) -> bool:
        """Checks if the print queue is empty."""
        return self.size == 0

    def enqueue_job(self, user_id: str, title: str, priority: int = 5) -> bool:
        """
        Adds a new print job to the back of the queue.
        This operation is thread-safe.
        """
        # TODO (Member 1): Your task is to understand and test this function.
        # No new code is required, but you are responsible for making sure it works.
        # 1. The 'with self.lock' ensures only one thread can modify the queue at a time.
        # 2. It checks if the queue is full before adding a new job.
        # 3. A new PrintJob object is created.
        # 4. The job is placed at the 'rear' of the circular queue, and pointers are updated.
        with self.lock:
            if self.is_full():
                print(f"[{self.current_simulation_time}s] Error: Queue is full. Cannot add '{title}'.")
                return False

            new_job = PrintJob(user_id, title, priority)
            self.queue[self.rear] = new_job
            self.rear = (self.rear + 1) % self.capacity
            self.size += 1
            print(f"[{self.current_simulation_time}s] Job '{new_job.title}' added to queue.")
            return True

    def print_job(self) -> PrintJob | None:
        """
        Finds, removes, and "prints" the highest priority job.
        Priority is determined by the lowest 'priority' value, then by the longest 'waiting_time'.
        """
        # TODO (Member 1): Your task is to understand and test this complex function.
        # 1. It locks the queue to work safely.
        # 2. It gathers all active jobs from the circular queue into a simple list.
        # 3. It sorts that list to find the highest priority job. Tie-breaking is done by waiting time.
        # 4. It rebuilds the queue *without* the job that is being printed. This is how an item
        #    is removed from the middle of the circular queue.
        # 5. It marks the job as "completed" and returns it.
        with self.lock:
            if self.is_empty():
                return None

            active_jobs = [self.queue[(self.front + i) % self.capacity] for i in range(self.size)]
            active_jobs.sort(key=lambda job: (job.priority, -job.waiting_time))
            job_to_print = active_jobs.pop(0) # Get and remove the best job

            # Rebuild the queue with the remaining jobs
            self.queue = [None] * self.capacity
            self.front = 0
            self.rear = 0
            self.size = 0
            for job in active_jobs:
                self.queue[self.rear] = job
                self.rear = (self.rear + 1) % self.capacity
                self.size += 1

            job_to_print.status = "completed"
            print(f"[{self.current_simulation_time}s] Printing job: '{job_to_print.title}' (Priority: {job_to_print.priority}, Wait Time: {job_to_print.waiting_time:.1f}s)")
            return job_to_print


    # ======================================================================
    # MODULE 2: PRIORITY & AGING SYSTEM (Owner: Member 2)
    # Goal: Increase job priority over time.
    # ======================================================================

    def apply_priority_aging(self):
        """
        Increases the priority of jobs that have been waiting for a long time.
        """
        # TODO (Member 2): Implement the priority aging logic here.
        # This function will be called by the `tick` event.
        #
        # 1. Use 'with self.lock:' to ensure thread safety.
        # 2. Loop through every job currently in the queue.
        #    (A 'for' loop from 0 to self.size is a good way to do this).
        # 3. For each job, check if its status is 'waiting'.
        # 4. Check if the job's `waiting_time` has surpassed a multiple of `self.priority_aging_interval`.
        #    A simple way is to see if `job.waiting_time % self.priority_aging_interval` is close to 0,
        #    but a more robust method is needed to handle variable tick durations.
        #    A better check might be to store how many times aging has been applied to a job.
        # 5. If it has, decrease its `priority` number by 1 (e.g., from 5 to 4).
        # 6. Make sure the priority does not go below 1 (the highest priority).
        # 7. Add a print statement to announce when a job's priority has been upgraded.
        pass # Replace 'pass' with your implementation.


    # ======================================================================
    # MODULE 3: JOB EXPIRY & CLEANUP (Owner: Member 3)
    # Goal: Remove jobs that have waited too long.
    # ======================================================================

    def remove_expired_jobs(self):
        """
        Checks for and removes jobs that have exceeded their expiry time.
        """
        # TODO (Member 3): Your task is to understand and test this function.
        # This function is called by the `tick` event.
        # 1. It gathers all jobs that have *not* expired into a new list called `jobs_to_keep`.
        # 2. Any job whose `waiting_time` is greater than or equal to `self.default_expiry_time_seconds` is considered expired.
        # 3. For expired jobs, it calls the `_notify_expiry` helper method.
        # 4. If any jobs were expired, it rebuilds the queue using only the jobs from `jobs_to_keep`.
        with self.lock:
            jobs_to_keep = []
            expired_jobs_count = 0

            for i in range(self.size):
                job = self.queue[(self.front + i) % self.capacity]
                if job.waiting_time >= self.default_expiry_time_seconds and job.status == "waiting":
                    self._notify_expiry(job)
                    expired_jobs_count += 1
                else:
                    jobs_to_keep.append(job)
            
            if expired_jobs_count > 0:
                self.queue = [None] * self.capacity
                self.front = 0
                self.rear = 0
                self.size = 0
                for job in jobs_to_keep:
                    self.queue[self.rear] = job
                    self.rear = (self.rear + 1) % self.capacity
                    self.size += 1
                print(f"[{self.current_simulation_time}s] --- {expired_jobs_count} job(s) removed due to expiry. ---")

    def _notify_expiry(self, job: PrintJob):
        """Helper method to log that a job has expired."""
        job.status = "expired"
        print(f"[{self.current_simulation_time}s] [JOB EXPIRED] Job '{job.title}' for user '{job.user_id}' has been removed.")


    # ======================================================================
    # MODULE 4: CONCURRENT SUBMISSION HANDLING (Owner: Member 4)
    # Goal: Handle simultaneous job submissions safely.
    # ======================================================================

    def handle_simultaneous_submissions(self, jobs_data: list[tuple]):
        """
        Handles multiple job submissions concurrently using a thread pool.
        """
        # TODO (Member 4): Your task is to understand and test this function.
        # 1. It uses a `ThreadPoolExecutor` to create a pool of worker threads.
        # 2. It iterates through the list of jobs to be submitted (`jobs_data`).
        # 3. For each job, it submits the `self.enqueue_job` method to the thread pool.
        #    This means the `enqueue_job` method for different jobs will run on different threads.
        # 4. Because `enqueue_job` has a lock, these concurrent calls are safe and won't corrupt the queue.
        print(f"\n[{self.current_simulation_time}s] --- Handling simultaneous submissions ---")
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Submit each job to the thread pool for processing
            future_to_job = {executor.submit(self.enqueue_job, user, title, prio): title for user, title, prio in jobs_data}
            for future in concurrent.futures.as_completed(future_to_job):
                try:
                    future.result() # Check if any exceptions occurred during the task
                except Exception as exc:
                    print(f"[{self.current_simulation_time}s] A job submission generated an exception: {exc}")
        print(f"[{self.current_simulation_time}s] --- Concurrent submissions handled. ---")


    # ======================================================================
    # MODULE 5: EVENT SIMULATION & TIME MANAGEMENT (Owner: Member 5)
    # Goal: Simulate the passage of time and trigger time-based events.
    # ======================================================================

def tick(self):
    #showing that a minute has passed
    print(f"Tick! Time is now {self.current_time} minutes")

    #making all jobs a minute older
    for job in self.queue:
        job.waiting_time += 1

        print(f"Job {job.job_id} now waiting {job.waiting_time} minutes")

    #aging jobs every 5 minutes
    if self.current_time % 5 == 0:
        print("Time for aging jobs")
        self.apply_priority_aging()

    #checking for expired jobs every 5 minutes
    if self.current_time % 5 == 0:
        print("Removing expired jobs")
        #removing them
        self.remove_expired_jobs()

    #updating the current time for the system
    self.current_time += 1

    # ======================================================================
    # MODULE 6: VISUALIZATION & REPORTING (Owner: Member 6)
    # Goal: Display the current queue status in a clear, user-friendly format.
    # ======================================================================

    def show_status(self):
        """
        Prints a user-friendly snapshot of the current queue status.
        """
        # TODO (Member 6): Your task is to ensure this output is clear and provides all needed info.
        # You can modify the print statements to make the table look better or add more details.
        # 1. It collects all jobs from the queue.
        # 2. It sorts them according to print order (priority, then waiting time).
        # 3. It prints a formatted table header.
        # 4. It loops through the sorted jobs and prints their details.
        print(f"\n=== Print Queue Status (Time: {self.current_simulation_time}s) ===")
        if self.is_empty():
            print("The queue is empty.")
            print("="*80)
            return
     
        jobs_to_display = [self.queue[(self.front + i) % self.capacity] for i in range(self.size)]
        jobs_to_display.sort(key=lambda j: (j.priority, -j.waiting_time))

        print(f"{'ID':<10} | {'User':<8} | {'Title':<20} | {'Prio':<5} | {'Wait (s)':<9} | {'Status':<10}")
        print("-" * 80)

        for job in jobs_to_display:
            print(f"{job.job_id[:8]:<10} | {job.user_id:<8} | {job.title:<20} | {job.priority:<5} | {job.waiting_time:<9.1f} | {job.status:<10}")
        
        print(f"\nQueue Size: {self.size}/{self.capacity}")
        print("="*80)