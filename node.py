import socket
import time
import threading
import csv
import sys
import random
import os
import signal

NODE_ID = sys.argv[1]
PORT = int(sys.argv[2])
PEERS = [int(p) for p in sys.argv[3].split(",")]
CRASH_NODE = sys.argv[4] == "true"

HEARTBEAT_INTERVAL = 0.5    
TIMEOUT = 6.0             
RUN_TIME = 240              
CRASH_TIME = 60             
PACKET_LOSS = 0.1           

last_seen = {}
suspected = set()
start_time = time.time()
crashed = False

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", PORT))
sock.settimeout(0.2)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

csv_file = open(f"{NODE_ID}_heartbeat.csv", "w", newline="")
writer = csv.writer(csv_file)
writer.writerow(["time", "event", "target", "latency"])


def log_event(event, target, latency=None):
    """
    Write an event to the CSV.
    latency is expected to be a float (seconds) or None.
    """
    if latency is None:
        writer.writerow([time.time(), event, target, ""])
    else:
        writer.writerow([time.time(), event, target, latency])
    csv_file.flush()

def listener():
    while time.time() - start_time < RUN_TIME and not crashed:
        try:
            data, _ = sock.recvfrom(1024)
            peer = data.decode()
            last_seen[peer] = time.time()

            if peer in suspected:
                suspected.remove(peer)
                log_event("RECOVERY", peer)

        except socket.timeout:
            pass
        except OSError as e:
            winerr = getattr(e, "winerror", None)
            if winerr in (10054, 10038):
                break
            raise

def sender():
    while time.time() - start_time < RUN_TIME and not crashed:
        for p in PEERS:
            if random.random() < PACKET_LOSS:
                continue
            sock.sendto(NODE_ID.encode(), ("127.0.0.1", p))
            log_event("SEND", p)
        time.sleep(HEARTBEAT_INTERVAL)

def detector():
    while time.time() - start_time < RUN_TIME and not crashed:
        now = time.time()
        for peer_id, last in list(last_seen.items()):
            if now - last > TIMEOUT and peer_id not in suspected:
                suspected.add(peer_id)
                latency = now - last
                log_event("SUSPECT", peer_id, latency)
        time.sleep(0.1)

def crash_injector():
    global crashed
    if not CRASH_NODE:
        return

    time.sleep(CRASH_TIME)
    log_event("CRASH", NODE_ID)
    crashed = True
    csv_file.flush()
    csv_file.close()
    sock.close()
    os.kill(os.getpid(), signal.SIGTERM)

threads = [
    threading.Thread(target=listener),
    threading.Thread(target=sender),
    threading.Thread(target=detector),
    threading.Thread(target=crash_injector),
]

for t in threads:
    t.start()

for t in threads:
    t.join()
