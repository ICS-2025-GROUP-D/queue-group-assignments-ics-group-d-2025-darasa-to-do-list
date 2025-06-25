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
