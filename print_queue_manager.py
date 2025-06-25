# === Shared Controller: Connects All Modules ===

from shared_job_file import PrintJob
from module1_core_queue import CircularQueue
from module2_priority import PriorityManager
from module3_expiry import ExpiryManager
from module4_concurrent import ConcurrentHandler
from module6_visualizer import Visualizer
from collections import deque


class PrintQueueManager:
    def __init__(self):
        self.queue = CircularQueue(capacity=10)
        self.priority_mgr = PriorityManager()
        self.expiry_mgr = ExpiryManager()
        self.visualizer = Visualizer()
        self.concurrent = ConcurrentHandler(self)

    def enqueue_job(self, user_id, job_id, priority):
        job = PrintJob(user_id, job_id, priority)
        if self.queue.enqueue(job):
            print(f"[+] Job {job_id} enqueued.")
        else:
            print(f"[!] Queue full. Job {job_id} rejected.")

    def tick(self):
        print("[Tick] Time advancing...")
        jobs = self.queue.status()
        for job in jobs:
            job.wait_time += 1
        self.priority_mgr.apply_aging(jobs)
        jobs = self.expiry_mgr.remove_expired(jobs)
        jobs = self.priority_mgr.sort_by_priority(jobs)
        self.queue.queue = deque(jobs, maxlen=self.queue.capacity)
        self.visualizer.show(self.queue.status())

    def print_job(self):
        job = self.queue.dequeue()
        if job:
            print(f"[✓] Printed job: {job.job_id}")
        else:
            print("[!] No job to print.")

    def show_status(self):
        self.visualizer.show(self.queue.status())

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

