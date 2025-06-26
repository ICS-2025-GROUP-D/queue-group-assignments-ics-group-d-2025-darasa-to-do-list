
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