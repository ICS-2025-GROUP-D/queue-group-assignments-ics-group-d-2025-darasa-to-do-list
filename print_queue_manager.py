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


class PrintQueueManager:

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
