import subprocess
import sys

PYTHON = sys.executable

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
        "gossip_node.py",
        name,
        str(port),
        ",".join(peers),
        crash_flag
    ]

    print("Starting", name, "on port", port)
    processes.append(subprocess.Popen(cmd))

try:
    for p in processes:
        p.wait()
except KeyboardInterrupt:
    for p in processes:
        p.terminate()
