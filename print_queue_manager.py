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