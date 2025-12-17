import subprocess
import sys
import os
import signal
import time

PYTHON = sys.executable
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

NODES = [
    ("node1", 5001),
    ("node2", 5002),
    ("node3", 5003),
    ("node4", 5004),
    ("node5", 5005),
]

CRASH_NODE = "node2"
processes = []

for name, port in NODES:
    peers = [str(p) for n, p in NODES if n != name]
    crash_flag = "true" if name == CRASH_NODE else "false"

    cmd = [
        PYTHON,
        os.path.join(BASE_DIR, "node.py"),
        name,
        str(port),
        ",".join(peers),
        crash_flag,
    ]

    print("Starting", name, "on port", port)
    p = subprocess.Popen(
        cmd,
        cwd=BASE_DIR,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )
    processes.append(p)
    time.sleep(0.5)

try:
    for p in processes:
        p.wait()
except KeyboardInterrupt:
    print("Stopping all nodes")
    for p in processes:
        try:
            p.send_signal(signal.CTRL_BREAK_EVENT)
        except Exception:
            p.terminate()