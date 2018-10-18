#!/usr/bin/python

import sys
# Prevents the creation of .pyc files - which appear broken on zee
sys.dont_write_bytecode = True

import Queue
import threading
import time
from pydispatch import dispatcher

WORKER_SIGNAL='worker_signal'
WORKER_SENDER='worker_sender'
BOSS_SIGNAL='boss_signal'
BOSS_SENDER='boss_sender'

class workerThread (threading.Thread):
   def __init__(self, threadID, name, q):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.q = q
      dispatcher.connect(self.receiveMessage, signal=self.name, sender=BOSS_SENDER)
   #run function runs when the thread spawns
   def run(self):
      print("Starting " + self.name)
      process_data(self.name, self.q)

   def receiveMessage(self, message):
      print(self.name + " has received message: " + message)
      newMessage = "thread " + self.name + " got a message from the boss!"
      dispatcher.send(message=newMessage, signal=WORKER_SIGNAL, sender=self.name)

class bossThread (threading.Thread):
   def __init__(self, threadID, name):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.threadList = []
   #run function runs when the thread spawns
   def run(self):
      print("Starting " + self.name)

   def addWorker(self, thread):
      newMessage = "Boss just added thread " + thread.name
      dispatcher.connect(self.receiveMessage, signal=WORKER_SIGNAL, sender=thread.name)
      dispatcher.send(message=newMessage, signal=thread.name, sender=BOSS_SENDER)
      self.threadList.append(thread)

   def closeWorkers(self):
      for t in self.threadList:
         print("Closing out thread " + t.name)
         t.join()

   def receiveMessage(self, message):
      print(self.name + " has received message: " + message)


exitFlag = 0

#basic function that runs when thread is spawned
def process_data(threadName, q):
   while not exitFlag:
      #Acquire the queuelock so we can get a job from the queue
      queueLock.acquire()
      if not workQueue.empty():
        data = q.get()
        queueLock.release()
        #print("%s processing %s" % (threadName, data))
      else:
        queueLock.release()
        #Trivial wait for the final thread that does not have work
        time.sleep(1)

boss = bossThread(0, "Boss")
boss.start()

threadList = ["Thread-1", "Thread-2", "Thread-3"]
dataList = ["One", "Two", "Three", "Four", "Five"]
#queueLock will allow the threads to safely access the workQueue
queueLock = threading.Lock()
workQueue = Queue.Queue(10)
threadID = 1

# Create new threads
for tName in threadList:
   thread = workerThread(threadID, tName, workQueue)
   thread.start()
   boss.addWorker(thread)
   threadID += 1

# Fill the queue
queueLock.acquire()
for word in dataList:
   workQueue.put(word)
queueLock.release()

# Wait for queue to empty
while not workQueue.empty():
   pass

exitFlag = 1

#Close out the worker threads
boss.closeWorkers()

#Join the last boss thread
boss.join()

print("Exiting Main Thread")
