# === Shared Controller: Connects All Modules ===

from shared_job_file import PrintJob
from module1_core_queue import CircularQueue
from module2_priority import PriorityManager
from module3_expiry import ExpiryManager
from module4_concurrent import ConcurrentHandler
from module6_visualizer import Visualizer
from collections import deque


# <--- (2) JAKES - Priority and Aging System --->
    def apply_priority_aging(self):
        """
        Iterates through waiting jobs and ages their priority if the aging interval is met.
        Ages by decrementing priority number (making it more urgent).
        """
        print(f"[{self.current_simulation_time}s] DEBUG: Entering apply_priority_aging.") # DEBUG PRINT
        print(f"[{self.current_simulation_time}s] Applying priority aging...")
        for i in range(self.size):
            idx = (self.front + i) % self.capacity
            job = self.queue[idx]
            if job and job.status == "waiting": # Only age jobs that are currently waiting
                if job.waiting_time > 0 and int(job.waiting_time) % self.aging_interval == 0:
                    job.priority = max(1, job.priority - 1)
                    print(f"[{self.current_simulation_time}s] Job {job.job_id[:8]}... '{job.title}' priority aged to {job.priority}.")
        print(f"[{self.current_simulation_time}s] DEBUG: Exiting apply_priority_aging.") # DEBUG PRINT

