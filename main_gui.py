import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import time
import printQueue

# ==============================================================================
#  PLACEHOLDER: Your Queue Logic
#  You can replace this entire class with: from printQueue import PrintQueue
# ==============================================================================
# class PrintQueue:
#     """A placeholder class for the backend queue logic."""
#     def __init__(self, capacity=10, aging_interval=5, expiry_time=15):
#         self.jobs = []
#         self.log = []
#         self.time = 0
#         self.job_id_counter = 1
#         self.capacity = capacity
#         self.aging_interval = aging_interval
#         self.expiry_time = expiry_time
#         self.add_log("Queue initialized.")

#     def add_log(self, message):
#         self.log.append(f"[T:{self.time:03d}] {message}")
#         if len(self.log) > 100: # Keep log from growing indefinitely
#             self.log.pop(0)

#     def get_all_jobs_sorted(self):
#         # Sorts by priority (lower is better), then by wait time (higher is better)
#         return sorted(self.jobs, key=lambda j: (j['priority'], -j['waitTime']))

#     def get_log(self):
#         return self.log

#     def enqueue(self, user_name, priority):
#         if len(self.jobs) >= self.capacity:
#             self.add_log(f"ERROR: Queue is full. Cannot add job for {user_name}.")
#             return False
        
#         job = {
#             'id': f"J{self.job_id_counter:03d}",
#             'userName': user_name,
#             'priority': priority,
#             'waitTime': 0,
#         }
#         self.jobs.append(job)
#         self.add_log(f"SUCCESS: Job {job['id']} added for {user_name} (Priority {priority}).")
#         self.job_id_counter += 1
#         return True

#     def tick(self):
#         self.time += 1
        
#         # 1. Update wait times for all jobs
#         for job in self.jobs:
#             job['waitTime'] += 1

#         # 2. Handle expired jobs
#         expired_jobs = [j for j in self.jobs if j['waitTime'] >= self.expiry_time]
#         for job in expired_jobs:
#             self.add_log(f"EXPIRED: Job {job['id']} for {job['userName']} removed.")
#         self.jobs = [j for j in self.jobs if j['waitTime'] < self.expiry_time]

#         # 3. Handle priority aging
#         if self.time > 0 and self.time % self.aging_interval == 0:
#             self.add_log("AGING: Applying priority aging.")
#             for job in self.jobs:
#                 if job['priority'] > 1:
#                     job['priority'] -= 1
#                     self.add_log(f"  -> Job {job['id']} priority is now {job['priority']}.")
        
#         self.add_log("TICK: Time advanced.")
#         return True

#     def dequeue(self):
#         if not self.jobs:
#             self.add_log("INFO: No jobs in queue to print.")
#             return None
        
#         job_to_print = self.get_all_jobs_sorted()[0]
#         self.jobs.remove(job_to_print)
#         self.add_log(f"PRINTED: Job {job_to_print['id']} for {job_to_print['userName']}.")
#         return job_to_print
    
#     def reset(self):
#         self.__init__(self.capacity, self.aging_interval, self.expiry_time)


# ==============================================================================
#  MAIN TKINTER APPLICATION
# ==============================================================================
class QueueSimulatorApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # --- Backend Instance ---
        # IMPORTANT: Replace the line below with your own class instance
        self.queue = PrintQueue()

        # --- Window Configuration ---
        self.title("Print Queue Simulator")
        self.geometry("900x600")
        self.configure(bg="#f0f2f5")

        # --- Style Configuration ---
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#f0f2f5")
        style.configure("TLabel", background="#f0f2f5", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"))
        style.configure("Card.TFrame", background="white", borderwidth=1, relief="solid")
        style.configure("Treeview", rowheight=25, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        # --- Main Layout ---
        self.main_frame = ttk.Frame(self, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create two main columns
        self.controls_frame = ttk.Frame(self.main_frame)
        self.display_frame = ttk.Frame(self.main_frame)
        
        self.controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self._create_controls_widgets()
        self._create_display_widgets()

        # --- Initial UI Update ---
        self.update_display()

    def _create_card(self, parent, title):
        card = ttk.Frame(parent, style="Card.TFrame", padding=15)
        card.pack(fill=tk.X, pady=5)
        
        title_label = ttk.Label(card, text=title, style="Header.TLabel", background="white")
        title_label.pack(fill=tk.X, pady=(0, 10), anchor="w")
        
        separator = ttk.Separator(card, orient='horizontal')
        separator.pack(fill='x', pady=(0, 10))

        return card

    def _create_controls_widgets(self):
        # --- Add Job Card ---
        add_job_card = self._create_card(self.controls_frame, "Add New Job")
        
        ttk.Label(add_job_card, text="User Name:", background="white").pack(anchor="w")
        self.user_name_entry = ttk.Entry(add_job_card, width=30)
        self.user_name_entry.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(add_job_card, text="Priority:", background="white").pack(anchor="w")
        self.priority_var = tk.StringVar(value="2")
        priority_options = ttk.OptionMenu(add_job_card, self.priority_var, "2", "1", "2", "3")
        priority_options.pack(fill=tk.X, pady=(0, 15))

        ttk.Button(add_job_card, text="Add Job", command=self.add_job).pack(fill=tk.X)

        # --- Controls Card ---
        controls_card = self._create_card(self.controls_frame, "Controls")

        ttk.Button(controls_card, text="Advance Time (Tick)", command=self.tick_time).pack(fill=tk.X, pady=4)
        ttk.Button(controls_card, text="Print Next Job", command=self.print_job).pack(fill=tk.X, pady=4)
        ttk.Button(controls_card, text="Reset Queue", command=self.reset_queue, style="Danger.TButton").pack(fill=tk.X, pady=4)
        style = ttk.Style()
        style.configure("Danger.TButton", background="#dc3545", foreground="white")
        style.map("Danger.TButton", background=[('active', '#c82333')])


    def _create_display_widgets(self):
        # --- Queue Display Card ---
        queue_card = self._create_card(self.display_frame, "Current Queue")
        
        cols = ('pos', 'id', 'user', 'priority', 'wait')
        self.tree = ttk.Treeview(queue_card, columns=cols, show='headings', height=10)
        
        # Define headings
        self.tree.heading('pos', text='Pos')
        self.tree.heading('id', text='Job ID')
        self.tree.heading('user', text='User')
        self.tree.heading('priority', text='Priority')
        self.tree.heading('wait', text='Wait Time')
        
        # Configure column widths
        self.tree.column('pos', width=40, anchor=tk.CENTER)
        self.tree.column('id', width=80, anchor=tk.CENTER)
        self.tree.column('user', width=150)
        self.tree.column('priority', width=60, anchor=tk.CENTER)
        self.tree.column('wait', width=80, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)

        # --- Activity Log Card ---
        log_card = self._create_card(self.display_frame, "Activity Log")

        self.log_text = tk.Text(log_card, height=10, state=tk.DISABLED, wrap=tk.WORD, font=("Courier New", 9), bg="#f8f9fa")
        self.log_text.pack(fill=tk.BOTH, expand=True)


    def update_display(self):
        """Refreshes all GUI elements with the latest data from the queue."""
        
        # Update window title with current time
        self.title(f"Print Queue Simulator - Time: {self.queue.time}")

        # Update job queue table (Treeview)
        # Clear existing items
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        # Add new items from the sorted job list
        sorted_jobs = self.queue.get_all_jobs_sorted()
        for i, job in enumerate(sorted_jobs):
            values = (i + 1, job['id'], job['userName'], job['priority'], job['waitTime'])
            self.tree.insert('', tk.END, values=values)

        # Update activity log
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete('1.0', tk.END)
        log_entries = self.queue.get_log()
        for entry in reversed(log_entries): # Show newest first
            self.log_text.insert(tk.END, entry + "\n")
        self.log_text.config(state=tk.DISABLED)


    # --- Action Handlers ---
    
    def add_job(self):
        user_name = self.user_name_entry.get()
        if not user_name:
            messagebox.showwarning("Input Error", "Please enter a user name.")
            return
        
        priority = int(self.priority_var.get())
        
        # Call the backend method
        self.queue.enqueue(user_name, priority)
        
        # Clear entry and refresh display
        self.user_name_entry.delete(0, tk.END)
        self.update_display()
        
    def tick_time(self):
        self.queue.tick()
        self.update_display()

    def print_job(self):
        self.queue.dequeue()
        self.update_display()

    def reset_queue(self):
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset the entire queue?"):
            self.queue.reset()
            self.update_display()


if __name__ == "__main__":
    app = QueueSimulatorApp()
    app.mainloop()
