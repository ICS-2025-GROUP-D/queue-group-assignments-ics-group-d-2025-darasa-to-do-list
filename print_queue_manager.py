# === Shared Controller: Connects All Modules ===

from shared_job_file import PrintJob
from module1_core_queue import CircularQueue
from module2_priority import PriorityManager
from module3_expiry import ExpiryManager
from module4_concurrent import ConcurrentHandler
from module6_visualizer import Visualizer
from collections import deque

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

