# Heartbeat and Gossip Simulation

This project simulates a distributed system to demonstrate and compare **Heartbeat** and **Gossip** protocols for failure detection. It allows you to spin up a local cluster of nodes, simulate node crashes, and analyze the detection latency and network overhead.

## Overview

- **Heartbeat Protocol**: Nodes periodically send "I'm alive" messages to their peers. If a message isn't received within a timeout, the peer is suspected of failure.
- **Gossip Protocol**: Nodes periodically share their view of the network state (who is alive) with random peers. This information propagates (gossips) through the network.

## Project Structure

- **`node.py`**: Implementation of a node using the Heartbeat protocol.
- **`gossip_node.py`**: Implementation of a node using the Gossip protocol.
- **`launcher.py`**: Helper script to launch a cluster of Heartbeat nodes.
- **`gossip_launcher.py`**: Helper script to launch a cluster of Gossip nodes.
- **`run_trials.py`**: Main driver script to run automated experiments (multiple trials of both protocols) and aggregate results.
- **`analyse.py`**: Analyzes the CSV logs from a Heartbeat trial.
- **`analyze_gossip.py`**: Analyzes the CSV logs from a Gossip trial.

## Getting Started

### Prerequisites

- Python 3.x
- Standard Python libraries (`socket`, `threading`, `time`, `random`, `subprocess`, `csv`, `os`, `sys`, `signal`)

### Running a Full Experiment

To run a complete set of experiments (by default, 10 trials for each protocol) and generate a summary of results:

```bash
python run_trials.py
```

This will:
1.  Launch the simulation multiple times.
2.  Inject a crash (simulated failure).
3.  Collect logs from all nodes.
4.  Analyze detection times and message counts.
5.  Append concise results to `experiments_concise.csv`.

### Running a Single Simulation Manually

You can also run a single instance of the simulation to see it in action.

**For Heartbeat:**
```bash
python launcher.py
```

**For Gossip:**
```bash
python gossip_launcher.py
```

*Note: The launcher scripts are configured to start 5 nodes, wait for a crash (in `node2`), and then terminate.*

## Configuration

You can tweak simulation parameters by editing the constants in `node.py` and `gossip_node.py`:

- **`HEARTBEAT_INTERVAL` / `GOSSIP_INTERVAL`**: How often nodes send messages.
- **`TIMEOUT`**: Time without a message before a peer is suspected of failure.
- **`PACKET_LOSS` / `LOSS_PROB`**: Probability of a simulated packet drop (network unreliability).
- **`RUN_TIME`**: Total duration of the simulation.
- **`CRASH_TIME`**: Time (in seconds) after start when the crash occurs.

## Output

Each node produces a CSV log file (e.g., `node1_heartbeat.csv` or `gossip_node1.csv`) recording events like:
- `SEND`: Message sent.
- `RECOVERY`: Node recovered (or seen again).
- `SUSPECT`: Node suspected of failure (with latency).
- `CRASH`: Node intentionally crashed.

The analysis scripts read these files to determine how quickly the crashed node was detected by others.
