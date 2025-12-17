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
    
    print("Starting heartbeat nodes...")
    launcher = subprocess.Popen(
        [PYTHON, os.path.join(BASE_DIR, "launcher.py")],
        cwd=BASE_DIR
    )
    launcher.wait()
    
    time.sleep(1)
    
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
    
    print("Starting gossip nodes...")
    launcher = subprocess.Popen(
        [PYTHON, os.path.join(BASE_DIR, "gossip_launcher.py")],
        cwd=BASE_DIR
    )
    launcher.wait()
    
    time.sleep(1)
    
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
    
    print("\n>>> Starting Heartbeat Trials <<<")
    for i in range(1, NUM_TRIALS + 1):
        run_heartbeat_trial(i)
        time.sleep(2)
    
    print("\n>>> Starting Gossip Trials <<<")
    for i in range(1, NUM_TRIALS + 1):
        run_gossip_trial(i)
        time.sleep(2)
    
    print("\n" + "="*60)
    print("All trials completed!")
    print("="*60)
    print(f"\nConcise results appended to: {CONCISE_FILE}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTrials interrupted by user.")
        sys.exit(1)

