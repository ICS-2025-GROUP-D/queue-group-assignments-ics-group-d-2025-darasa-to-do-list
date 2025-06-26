# === Shared Controller: Connects All Modules ===

from shared_job_file import PrintJob
from module1_core_queue import CircularQueue
from module2_priority import PriorityManager
from module3_expiry import ExpiryManager
from module4_concurrent import ConcurrentHandler
from module6_visualizer import Visualizer
from collections import deque
import threading
import concurrent.futures
import time
import uuid
from datetime import datetime


    # <--- (1) RAY -- Core Queue Management --->
def is_full(self) -> bool:
        """
        Checks if the print queue is full.
        """
        print(f"[{self.current_simulation_time}s] DEBUG: is_full called (size={self.size}, capacity={self.capacity}).") # DEBUG PRINT
        result = self.size == self.capacity
        print(f"[{self.current_simulation_time}s] DEBUG: is_full returning {result}.") # DEBUG PRINT
        return result

def is_empty(self) -> bool:
        """
        Checks if the print queue is empty.
        """
        print(f"[{self.current_simulation_time}s] DEBUG: is_empty called (size={self.size}).") # DEBUG PRINT
        result = self.size == 0
        print(f"[{self.current_simulation_time}s] DEBUG: is_empty returning {result}.") # DEBUG PRINT
        return result

def enqueue_job(self, user_id: str, title: str, priority: int = 5) -> bool:
        """
        Adds a new print job to the queue.
        Ensures thread-safe operation.
        """
        print(f"[{self.current_simulation_time}s] DEBUG: Entering enqueue_job for '{title}'.") # DEBUG PRINT
        
        with self.lock: # Lock is acquired here, covering all queue modifications
            print(f"[{self.current_simulation_time}s] DEBUG: Lock acquired in enqueue_job for '{title}'.") # DEBUG PRINT
            if self.is_full(): # Now calls is_full WITHOUT re-acquiring the lock
                print(f"[{self.current_simulation_time}s] Error: Queue is full. Cannot add job '{title}'.")
                return False

            new_job = PrintJob(user_id, title, priority)
            # Store the job in the circular queue at the rear position
            self.queue[self.rear] = new_job
            self.rear = (self.rear + 1) % self.capacity
            self.size += 1 # Increment the count of jobs in the queue

            print(f"[{self.current_simulation_time}s] Job '{new_job.title}' (ID: {new_job.job_id[:8]}...) added to queue (size={self.size}).")
            return True

def dequeue_job(self) -> PrintJob | None:
        """
        Selects and removes the highest priority job from the queue for printing.
        Priority is determined by lowest 'priority' value, then by highest 'waiting_time'.
        Handles removal from a circular array by rebuilding the active portion.
        """
        print(f"[{self.current_simulation_time}s] DEBUG: Entering dequeue_job.") # DEBUG PRINT
        with self.lock: # Lock acquired here
            print(f"[{self.current_simulation_time}s] DEBUG: Lock acquired in dequeue_job.") # DEBUG PRINT
            if self.is_empty():
                print(f"[{self.current_simulation_time}s] No jobs in queue to print.")
                return None

            # First, clean up any expired jobs before attempting to dequeue
            print(f"[{self.current_simulation_time}s] DEBUG: Calling clean_expired_jobs from dequeue.") # DEBUG PRINT
            self.clean_expired_jobs() # This method also operates under the current lock, which is fine.
            print(f"[{self.current_simulation_time}s] DEBUG: Returned from clean_expired_jobs.") # DEBUG PRINT

            if self.is_empty(): # Check again after cleanup
                print(f"[{self.current_simulation_time}s] No valid jobs left in the queue after cleanup.")
                return None

            # Collect all active jobs into a temporary list to sort them
            temp_jobs_list = []
            for i in range(self.size):
                idx = (self.front + i) % self.capacity
                job = self.queue[idx]
                if job: # Only add valid job objects (should always be true if size is accurate)
                    temp_jobs_list.append((job, idx)) # Store job object and its original index

            # If no jobs remain after collection (unlikely if not empty), return None
            if not temp_jobs_list:
                print(f"[{self.current_simulation_time}s] DEBUG: temp_jobs_list is empty after filtering, returning None.") # DEBUG PRINT
                return None

            # Sort the jobs:
            # 1. By priority in ascending order (lower number = higher urgency)
            # 2. For tie-breaking, by waiting_time in descending order (longer waiting = higher urgency)
            temp_jobs_list.sort(key=lambda x: (x[0].priority, -x[0].waiting_time))

            # The job to dequeue is the first element after sorting
            job_to_dequeue, original_index = temp_jobs_list[0]
            print(f"[{self.current_simulation_time}s] DEBUG: Job selected for dequeue: '{job_to_dequeue.title}' at original index {original_index}.") # DEBUG PRINT

            # --- Start removal from circular queue ---
            if original_index == self.front:
                print(f"[{self.current_simulation_time}s] DEBUG: Removing job from front.") # DEBUG PRINT
                self.queue[self.front] = None # Clear the slot
                self.front = (self.front + 1) % self.capacity
                self.size -= 1 # Correct: Only decrement size here if removing from front
            else:
                print(f"[{self.current_simulation_time}s] DEBUG: Rebuilding queue for arbitrary removal.") # DEBUG PRINT
                # Create a new list excluding the job to be dequeued
                current_jobs_list_excluding_dequeued = [
                    job_obj for job_obj, idx in temp_jobs_list if job_obj != job_to_dequeue
                ]

                # Reset the circular queue state
                self.queue = [None] * self.capacity
                self.front = 0
                self.rear = 0
                self.size = 0 # Reset size before rebuilding

                # Re-add all jobs that were not dequeued
                for job in current_jobs_list_excluding_dequeued:
                    self.queue[self.rear] = job
                    self.rear = (self.rear + 1) % self.capacity
                    self.size += 1 # Size is correctly updated here during rebuild
            print(f"[{self.current_simulation_time}s] DEBUG: Queue rebuilt. New size: {self.size}.") # DEBUG PRINT
            # --- End removal from circular queue ---

            # Update job status and print completion message
            job_to_dequeue.status = "printing"
            print(f"[{self.current_simulation_time}s] Printing job: '{job_to_dequeue.title}' (ID: {job_to_dequeue.job_id[:8]}...).")
            print(f"[{self.current_simulation_time}s] Time in queue: {job_to_dequeue.waiting_time:.2f} simulated seconds.")
            
            job_to_dequeue.status = "completed"
            print(f"[{self.current_simulation_time}s] Job '{job_to_dequeue.title}' (ID: {job_to_dequeue.job_id[:8]}...) completed.")
            return job_to_dequeue

# <--- (6) Jeremiah - Visualization and Status Display --->
def show_status(self):
        """
        Prints a formatted, user-friendly snapshot of the current queue status.
        Jobs are displayed sorted by priority and waiting time.
        """
        print(f"\n=== Print Queue Status (Time: {self.current_simulation_time}s) ===")
        print(f"[{self.current_simulation_time}s] DEBUG: show_status called. Current size: {self.size}.") # DEBUG PRINT
        
        if self.is_empty():
            print("The queue is empty.")
            return
     
        # Collect jobs currently in the queue
        jobs_to_display = []
        for i in range(self.size):
            index = (self.front + i) % self.capacity
            job = self.queue[index]
            if job: # Defensive check, should always be true if size is accurate
                jobs_to_display.append(job)

        # Sort jobs for display based on priority and waiting time (same logic as dequeue)
        jobs_to_display.sort(key=lambda j: (j.priority, -j.waiting_time))

        # Print table header
        print(f"{'ID':<10} | {'User':<8} | {'Title':<20} | {'Prio':<5} | {'Wait (s)':<9} | {'Status':<10} | {'Expiry (s)':<10}")
        print("-" * 100)

        # Print each job's details
        for job in jobs_to_display:
            if self.start_simulation_timestamp is None:
                time_since_submission_sim = 0
            else:
                time_since_submission_real = job.created_at.timestamp() - self.start_simulation_timestamp
                time_since_submission_sim = self.current_simulation_time # A simpler approach for simulation time
                                                                         
            remaining_expiry = self.default_expiry_time_seconds - job.waiting_time
            expiry_info = f"{max(0, remaining_expiry):.1f}" if not job.status == "completed" else "N/A"
            
            print(f"{job.job_id[:8]:<10} | {job.user_id:<8} | {job.title:<20} | {job.priority:<5} | {job.waiting_time:<9.1f} | {job.status:<10} | {expiry_info:<10}")
        print("-" * 100)
        print(f"[{self.current_simulation_time}s] DEBUG: Exiting show_status.") # DEBUG PRINT


def get_queue_snapshot(self) -> dict:
        """
        Returns a dictionary representing the current state of the queue.
        Useful for external reporting or logging.
        """
        snapshot = {
           'current_time': self.current_simulation_time,
           'queue_size': self.size,
           'queue_capacity': self.capacity,
            'jobs': []
        }

        # Iterate through active jobs to add their data to the snapshot
        for i in range(self.size):
            actual_index = (self.front + i) % self.capacity
            job = self.queue[actual_index]
            if job: # Defensive check
                # Create a dict representation of the job for the snapshot
                job_data = {
                    'job_id': job.job_id,
                    'user_id': job.user_id,
                    'title': job.title,
                    'priority': job.priority,
                    'created_at': job.created_at.isoformat(), # ISO format for datetime
                    'status': job.status,
                    'waiting_time': job.waiting_time
                }
                snapshot['jobs'].append(job_data)

        return snapshot

# 3-DAVIS-JOB-EXPIRY
def clean_expired_jobs(self):
        """
        Checks for and removes jobs that have exceeded their default expiry time.
        Notifies when a job expires.
        """
        print(f"[{self.current_simulation_time}s] DEBUG: Entering clean_expired_jobs.") # DEBUG PRINT
        print(f"[{self.current_simulation_time}s] Checking for expired jobs...")
        
        jobs_to_keep = []
        expired_jobs_count = 0

        # Iterate through all current jobs in the queue
        for i in range(self.size):
            idx = (self.front + i) % self.capacity
            job = self.queue[idx]
            
            if job is None: # Should not happen if self.size is accurate, but good for robustness
                print(f"[{self.current_simulation_time}s] DEBUG: Found None at index {idx} in clean_expired_jobs.") # DEBUG PRINT
                continue

            # Check if the job's waiting_time has exceeded the default expiry time
            is_expired = job.waiting_time >= self.default_expiry_time_seconds
            print(f"[{self.current_simulation_time}s] DEBUG: Job '{job.title}' (ID: {job.job_id[:8]}...) wait={job.waiting_time}, is_expired={is_expired}.") # DEBUG PRINT

            if is_expired and job.status == "waiting": # Only expire jobs that are waiting
                self._notify_expiry(job)
                expired_jobs_count += 1
            else:
                # If not expired, or not a waiting job (e.g., printing/completed), keep it.
                jobs_to_keep.append(job)
        
        if expired_jobs_count > 0:
            print(f"[{self.current_simulation_time}s] DEBUG: Rebuilding queue after expiry. Jobs to keep: {len(jobs_to_keep)}.") # DEBUG PRINT
            # If jobs were expired, rebuild the queue with only the jobs to keep
            self.queue = [None] * self.capacity
            self.front = 0
            self.rear = 0
            self.size = 0
            for job in jobs_to_keep:
                self.queue[self.rear] = job
                self.rear = (self.rear + 1) % self.capacity
                self.size += 1
            print(f"[{self.current_simulation_time}s] --- {expired_jobs_count} job(s) removed due to expiry. ---")
        else:
            print(f"[{self.current_simulation_time}s] No expired jobs to clean.")
        print(f"[{self.current_simulation_time}s] DEBUG: Exiting clean_expired_jobs. Current size: {self.size}.") # DEBUG PRINT


def _notify_expiry(self, job: PrintJob):
        """
        Helper method to notify when a job has expired.
        """
        print(f"[{self.current_simulation_time}s] [JOB EXPIRED] Job '{job.title}' (ID: {job.job_id[:8]}...) has expired and been removed from the queue.")




 # <--- (4) AMANI - Concurrent Job Submission Handling --->
def process_single_job(self, user_id: str, title: str, priority: int) -> str:
        """
        Wrapper method to enqueue a single job. Designed to be called by thread pool executor.
        """
        print(f"[{self.current_simulation_time}s] DEBUG: Entering process_single_job for '{title}'.") # DEBUG PRINT
        # Call the main enqueue_job method, which is already thread-safe due to internal locking.
        enqueued_successfully = self.enqueue_job(user_id, title, priority)
        if enqueued_successfully:
            return f"Successfully submitted job '{title}' for user {user_id}."
        else:
            return f"Failed to submit job '{title}' for user {user_id} (Queue full)."

def handle_simultaneous_submissions(self, jobs_data: list[tuple]) -> list[str]:
        """
        Handles multiple job submissions concurrently using a ThreadPoolExecutor.
        Each job_info tuple should be (user_id, title, priority).
        """
        all_submissions_outcomes = []

        print(f"\n[{self.current_simulation_time}s] --- Handling simultaneous submissions ---")
        print(f"[{self.current_simulation_time}s] DEBUG: Entering handle_simultaneous_submissions.") # DEBUG PRINT
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for job_info in jobs_data: # job_info is expected to be (user_id, title, priority)
                # Submit each job to the thread pool for processing
                future = executor.submit(self.process_single_job, job_info[0], job_info[1], job_info[2])
                futures.append(future)

            # Collect results as they complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    all_submissions_outcomes.append(result)
                except Exception as exc:
                    # Log any exceptions that occur during job processing
                    print(f"[{self.current_simulation_time}s] One of the jobs raised an unhandled exception: {exc}")
                    all_submissions_outcomes.append(f"Job failed with exception: {exc}")

        print(f"[{self.current_simulation_time}s] --- All concurrent job submissions completed.---")
        print(f"[{self.current_simulation_time}s] DEBUG: Exiting handle_simultaneous_submissions.") # DEBUG PRINT
        return all_submissions_outcomes
