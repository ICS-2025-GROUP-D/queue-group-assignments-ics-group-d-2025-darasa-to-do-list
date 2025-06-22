# === Main Program: Interacts with the system ===

from print_queue_manager import PrintQueueManager
import threading
pq_manager= PrintQueueManager()
t1 = threading.Thread(target= pq_manager.concurrent.submit,args=(1,"J334",3))# Show queue
t2 = threading.Thread(target= pq_manager.concurrent.submit,args=(1,"J334",3))# Show queue

t1.start()
t2.start()
t1.join()
t2.join()

pq_manager.show_status()