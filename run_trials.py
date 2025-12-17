import subprocess
import sys
import os
import time

PYTHON = sys.executable
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

NUM_TRIALS = 5

CONCISE_FILE = os.path.join(BASE_DIR, "experiments_concise.csv")


def _assert_concise_created(protocol: str):
    """Ensure experiments_concise.csv exists after each analysis step."""
    if not os.path.exists(CONCISE_FILE):
        raise RuntimeError(
            f"{protocol} analysis did not produce '{CONCISE_FILE}'. "
            "Check analyse/analyze_gossip for errors."
        )


def run_heartbeat_trial(trial_num):
    """Run one heartbeat trial: launch nodes, wait for completion, then analyze."""
    print(f"\n{'='*60}")
    print(f"HEARTBEAT TRIAL {trial_num}/{NUM_TRIALS}")
    print(f"{'='*60}")
    
    # Run the launcher
    print("Starting heartbeat nodes...")
    launcher = subprocess.Popen(
        [PYTHON, os.path.join(BASE_DIR, "launcher.py")],
        cwd=BASE_DIR
    )
    launcher.wait()
    
    # Wait a moment for files to be written
    time.sleep(1)
    
    # Run analysis
    print("Analyzing heartbeat trial...")
    analyzer = subprocess.Popen(
        [PYTHON, os.path.join(BASE_DIR, "analyse.py")],
        cwd=BASE_DIR
    )
    analyzer.wait()
    _assert_concise_created("heartbeat")
    
    print(f"Heartbeat trial {trial_num} completed.")

def run_gossip_trial(trial_num):
    """Run one gossip trial: launch nodes, wait for completion, then analyze."""
    print(f"\n{'='*60}")
    print(f"GOSSIP TRIAL {trial_num}/{NUM_TRIALS}")
    print(f"{'='*60}")
    
    # Run the launcher
    print("Starting gossip nodes...")
    launcher = subprocess.Popen(
        [PYTHON, os.path.join(BASE_DIR, "gossip_launcher.py")],
        cwd=BASE_DIR
    )
    launcher.wait()
    
    # Wait a moment for files to be written
    time.sleep(1)
    
    # Run analysis
    print("Analyzing gossip trial...")
    analyzer = subprocess.Popen(
        [PYTHON, os.path.join(BASE_DIR, "analyze_gossip.py")],
        cwd=BASE_DIR
    )
    analyzer.wait()
    _assert_concise_created("gossip")
    
    print(f"Gossip trial {trial_num} completed.")

def main():
    print("="*60)
    print(f"Running {NUM_TRIALS} trials each for Heartbeat and Gossip")
    print("="*60)
    
    # Run heartbeat trials
    # Comment out heartbeat trials for now
    print("\n>>> Starting Heartbeat Trials <<<")
    for i in range(1, NUM_TRIALS + 1):
        run_heartbeat_trial(i)
        time.sleep(2)
    
    # Run gossip trials
    print("\n>>> Starting Gossip Trials <<<")
    for i in range(1, NUM_TRIALS + 1):
        run_gossip_trial(i)
        time.sleep(2)  # Brief pause between trials
    
    print("\n" + "="*60)
    print("All trials completed!")
    print("="*60)
    print(f"\nConcise results appended to: {CONCISE_FILE}")
    print("\nYou can now run:")
    print("  - aggregate_heartbeat_latencies.py (to see aggregated heartbeat results)")
    print("  - aggregate_gossip_latencies.py (to see aggregated gossip results)")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTrials interrupted by user.")
        sys.exit(1)

