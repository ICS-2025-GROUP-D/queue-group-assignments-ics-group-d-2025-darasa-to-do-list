import threading
import time
from datetime import datetime
import uuid
import concurrent.futures

    # ======================================================================
    # MODULE 6: VISUALIZATION & REPORTING (Owner: Member 6)
    # Goal: Display the current queue status in a clear, user-friendly format.
    # ======================================================================

    def show_status(self):
        """
        Prints a user-friendly snapshot of the current queue status.
        """
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
