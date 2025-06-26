# === Shared PrintJob Class ===
# This class is used across all modules to represent a job.

class PrintJob:
    def __init__(self, user_id, job_id, priority):
        self.user_id = user_id
        self.job_id = job_id
        self.priority = priority
        self.wait_time = 0
        self.expired = False

    def __str__(self):
        return f"JobID:{self.job_id} | User:{self.user_id} | Priority:{self.priority} | Wait:{self.wait_time}s"
