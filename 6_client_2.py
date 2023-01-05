import socket
import random
from time import sleep, time
from threading import current_thread, Thread
from multiprocessing import current_process, Process, Queue, Pipe
from json import dumps



HOST = "127.0.0.1"
PORT = 65429


def thread_task_1(strok, queue, input, output):
    start = time()
    delay = random.random()
    sleep(delay)
    additive = ''
    if input != 0:
        additive = input.recv()
    strok = ' '.join(i + '\\n' for i in strok.split())
    thread_name = current_thread().name
    process_name = current_process().name
    data = f'{additive} {strok}'
    queue.put([f'Thread {thread_name} in process {process_name} done with result {data}', start, time(), delay])
    output.send(data)
    # queue.put(f'Sent {data} to next thread')


def thread_task_2(queue, input, output):
    start = time()
    delay = random.random()
    sleep(delay)
    strok = input.recv()
    data = ' '.join(f'{i+1}: {val}' for i, val in enumerate(strok.split()))
    thread_name = current_thread().name
    process_name = current_process().name
    queue.put([f'Thread {thread_name} in process {process_name} done with result {data}', start, time(), delay])
    output.send(data)
    # queue.put(f'Sent {data} to next thread')


def process_task(queue):
    start = time()
    conn1, conn2 = Pipe(duplex=True)
    conn3, conn4 = Pipe()
    conn5, conn6 = Pipe()
    stringa = 'Too hard to beat'
    stringb = 'them up'
    thread1 = Thread(target=thread_task_1, args=([stringa, queue, 0, conn1]))
    thread2 = Thread(target=thread_task_1, args=([stringb, queue, conn2, conn3]))
    thread3 = Thread(target=thread_task_2, args=([queue, conn4, conn5]))
    thread1.start()
    thread2.start()
    thread3.start()
    thread1.join()
    thread2.join()
    thread3.join()
    item = conn6.recv()
    # queue.put(f'Finally {item}')
    process_name = current_process().name
    queue.put([f'Process {process_name} done.', start, time(), 0])


if __name__ == '__main__':
    queue = Queue()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(bytes(dumps(['Client 2 started.', 0, 0, 0]) + '###', encoding='utf-8'))
        processes = [Process(target=process_task, args=(queue,)) for i in range(2)]
        for process in processes:
            process.start()
        for process in processes:
            process.join()
        while not queue.empty():
            item = queue.get()
            print(f'{item}')
            b = bytes(dumps(item) + '###', encoding='utf-8')
            s.sendall(b)
        s.sendall(bytes(dumps(['Client 2 done.', 0, 0, 0]) + '###', encoding='utf-8'))
