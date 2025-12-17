import socket
import threading
import time
import random
import sys
import csv

NODE_ID = sys.argv[1]
PORT = int(sys.argv[2])
PEERS = [int(p) for p in sys.argv[3].split(",")]
CRASH = sys.argv[4] == "true"

GOSSIP_INTERVAL = 0.5
TIMEOUT = 15.0
RUN_TIME = 120
CRASH_TIME = 30
LOSS_PROB = 0.1

alive = {p: time.time() for p in PEERS}
suspected = set()
start_time = time.time()

csv_file = open(f"gossip_{NODE_ID}.csv", "w", newline="")
writer = csv.writer(csv_file)
writer.writerow(["time", "event", "target", "latency"])

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", PORT))
sock.settimeout(0.2)


def log(event, target, latency=None):
    if latency is None:
        writer.writerow([time.time(), event, target, ""])
    else:
        writer.writerow([time.time(), event, target, latency])
    csv_file.flush()

def listener():
    while time.time() - start_time < RUN_TIME:
        try:
            data, _ = sock.recvfrom(4096)
            msg = data.decode().split("|")
            sender = int(msg[0])

            for item in msg[1:]:
                pid, ts = item.split(",")
                pid = int(pid)
                ts = float(ts)
                alive[pid] = max(alive.get(pid, 0), ts)

            alive[sender] = time.time()

        except socket.timeout:
            continue
        except OSError as e:
            winerr = getattr(e, "winerror", None)
            if winerr in (10054, 10038):
                break
            raise

def gossiper():
    while time.time() - start_time < RUN_TIME:
        if CRASH and time.time() - start_time > CRASH_TIME:
            log("CRASH", NODE_ID)
            return

        peer = random.choice(PEERS)
        if random.random() < LOSS_PROB:
            time.sleep(GOSSIP_INTERVAL)
            continue

        payload = [str(PORT)]
        for p, ts in alive.items():
            payload.append(f"{p},{ts}")

        msg = "|".join(payload).encode()
        sock.sendto(msg, ("127.0.0.1", peer))
        log("SEND", peer)

        time.sleep(GOSSIP_INTERVAL)

def detector():
    while time.time() - start_time < RUN_TIME:
        now = time.time()
        for p, ts in alive.items():
            if now - ts > TIMEOUT and p not in suspected:
                suspected.add(p)
                latency = now - ts
                log("SUSPECT", p, latency)
        time.sleep(0.5)

threads = [
    threading.Thread(target=listener),
    threading.Thread(target=gossiper),
    threading.Thread(target=detector),
]

for t in threads:
    t.start()

for t in threads:
    t.join()

csv_file.close()
sock.close()
