import pandas as pd
import glob
import os
import numpy as np

CRASH_NODE = "5002"
CRASH_TIME = None

logs = {}

for file in glob.glob("gossip_node*.csv"):
    node = file.replace(".csv", "")
    df = pd.read_csv(file)
    logs[node] = df

for df in logs.values():
    crash_rows = df[df["event"] == "CRASH"]
    if len(crash_rows) > 0:
        CRASH_TIME = crash_rows.iloc[0]["time"]

if CRASH_TIME is None:
    raise RuntimeError("Crash time missing")

total_suspects = 0
latencies = []

fp_by_observer = {}
fp_by_target = {}

send_counts = {}
durations = {}

for node, df in logs.items():
    if not df.empty:
        durations[node] = df["time"].max() - df["time"].min()
    else:
        durations[node] = 0.0

    send_counts[node] = (df["event"] == "SEND").sum()

    suspects = df[df["event"] == "SUSPECT"]

    for _, row in suspects.iterrows():
        total_suspects += 1
        target = str(row["target"])
        t = row["time"]

        if target != CRASH_NODE:
            fp_by_observer[node] = fp_by_observer.get(node, 0) + 1
            fp_by_target[target] = fp_by_target.get(target, 0) + 1

        if target == CRASH_NODE and t >= CRASH_TIME:
            latencies.append(t - CRASH_TIME)

print("=== GOSSIP RESULTS ===")
print("Total SUSPECT events:", total_suspects)

all_times = []
for df in logs.values():
    if not df.empty:
        all_times.append(df["time"].min())
        all_times.append(df["time"].max())

if len(all_times) >= 2:
    total_duration = max(all_times) - min(all_times)
else:
    total_duration = 0.0


failures = sum((df["event"] == "CRASH").sum() for df in logs.values())

print("Detection latencies:", [round(float(x), 3) for x in latencies])

detection = False
mean_latency = median_latency = p99_latency = p999_latency  = None
if len(latencies) > 0:
    detection = True
    lat_arr = np.array(latencies)
    mean_latency = float(lat_arr.mean())
    median_latency = float(np.median(lat_arr))
    p99_latency = float(np.percentile(lat_arr, 99))
    p999_latency = float(np.percentile(lat_arr, 99.9))
    print(f"Detection: {detection}")
    print("Mean latency:", round(mean_latency, 3))
    print("Median latency:", round(median_latency, 3))
    print("99th percentile latency:", round(p99_latency, 3))
    print("99.9th percentile latency:", round(p999_latency, 3))
else:
    print(f"Detection: {detection}")
    print("Mean latency: N/A (no detections of crashed node)")
    print("Median latency: N/A")
    print("99th percentile latency: N/A")
    print("99.9th percentile latency: N/A")
    print("Mann–Whitney U statistic: N/A (no detections)")
    print("p value: N/A (no detections)")

message_rates = {}
for node, send_count in send_counts.items():
    dur = durations.get(node, 0.0)
    if dur > 0:
        message_rates[node] = float(send_count) / float(dur)
    else:
        message_rates[node] = 0.0

pretty_rates = {node: round(rate, 3) for node, rate in message_rates.items()}
print("Message overhead (messages per node per second):", pretty_rates)

avg_msg_rate = float(sum(message_rates.values()) / len(message_rates)) if message_rates else None

summary_file = "gossip_experiments.csv"
summary_exists = os.path.exists(summary_file)

latency_file = "gossip_all_latencies.csv"
latency_df = pd.DataFrame({"latency": [float(x) for x in latencies]})
if os.path.exists(latency_file):
    existing_lat = pd.read_csv(latency_file)
    combined_lat = pd.concat([existing_lat, latency_df], ignore_index=True)
    combined_lat.to_csv(latency_file, index=False)
else:
    latency_df.to_csv(latency_file, index=False)

summary_row = {
    "total_suspects": total_suspects,
    "mean_latency": mean_latency,
    "median_latency": median_latency,
    "p99_latency": p99_latency,
    "p999_latency": p999_latency,
    "duration_seconds": total_duration,
    "avg_msg_rate_per_node_per_sec": avg_msg_rate,
    "Detection": detection
}

summary_df = pd.DataFrame([summary_row])
if summary_exists:
    existing = pd.read_csv(summary_file)
    combined = pd.concat([existing, summary_df], ignore_index=True)
    combined.to_csv(summary_file, index=False)
else:
    summary_df.to_csv(summary_file, index=False)

concise_file = "experiments_concise.csv"
concise_exists = os.path.exists(concise_file)

trial_number = 1
if concise_exists:
    existing_concise = pd.read_csv(concise_file)
    protocol_rows = existing_concise[existing_concise["Protocol"] == "gossip"]
    trial_number = int(protocol_rows["Trial"].max()) + 1 if not protocol_rows.empty else 1

latencies_str = ",".join(str(round(float(x), 6)) for x in latencies) if latencies else ""
message_overhead = avg_msg_rate

concise_row = {
    "Protocol": "gossip",
    "Nodes": len(logs),
    "Trial": trial_number,
    "Latencies": latencies_str,
    "Mean Latency": mean_latency,
    "Message Overhead": message_overhead,
    "Detection": detection
}

concise_df = pd.DataFrame([concise_row])
if concise_exists:
    existing_concise = pd.read_csv(concise_file)
    combined_concise = pd.concat([existing_concise, concise_df], ignore_index=True)
    combined_concise.to_csv(concise_file, index=False)
else:
    concise_df.to_csv(concise_file, index=False)
