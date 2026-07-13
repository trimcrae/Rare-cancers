#!/usr/bin/env python3
"""Pull SageMaker-published GPU/CPU utilization from CloudWatch for a running training job.

Purpose (2026-07-13): the congeneric RBFE complex leg trains ~3x slower than estimated (30 GPU-h, iter times
swing 8s->40s). Before spending on the A3 fleet, determine whether that is GPU-BOUND (heavy alchemical MD =
unavoidable cost) or CPU-BOUND overhead (GPU idling on MBAR/IO/setup = fixable cheaply with more vCPU, e.g.
g5.2xlarge). SageMaker auto-publishes GPUUtilization / CPUUtilization / GPUMemoryUtilization to CloudWatch
namespace /aws/sagemaker/TrainingJobs (dimension Host=<job>/algo-1) — no SSH needed. Read it on the LIVE job so
we have a slow workload to measure. Pure boto3 (runs in CI with the AWS secrets).

Reading: GPU util ~90-100% during slow stretches -> GPU-bound (accept the cost). GPU util dipping to 30-60%
while CPU util is high -> CPU-bound overhead -> a higher-vCPU instance likely cuts wall-clock + cost.
"""
import datetime
import os
import sys

import boto3


def main() -> int:
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")
    tag = os.environ.get("JOB_TAG", "nr4a3-congeneric-rbfe-complex")
    job = os.environ.get("JOB_NAME", "").strip()
    minutes = int(os.environ.get("MINUTES", "90"))
    sm = boto3.client("sagemaker", region_name=region)
    cw = boto3.client("cloudwatch", region_name=region)

    if not job:
        summ = sm.list_training_jobs(StatusEquals="InProgress", MaxResults=100,
                                     SortBy="CreationTime", SortOrder="Descending")["TrainingJobSummaries"]
        cand = [j["TrainingJobName"] for j in summ if tag in j["TrainingJobName"]]
        if not cand:
            print(f"[gpuutil] no InProgress training job matching '{tag}'. In-progress jobs:")
            for j in summ[:20]:
                print("   ", j["TrainingJobName"], j.get("TrainingJobStatus"))
            return 0
        job = cand[0]

    # confirm it is actually training (metrics only flow while Training, not Starting/Downloading)
    d = sm.describe_training_job(TrainingJobName=job)
    sec = d.get("SecondaryStatus")
    print(f"[gpuutil] job: {job}\n[gpuutil] SecondaryStatus: {sec}  (metrics flow only while 'Training')")
    print(f"[gpuutil] window: last {minutes} min, per-minute CloudWatch stats\n")

    end = datetime.datetime.utcnow()
    start = end - datetime.timedelta(minutes=minutes)
    host = f"{job}/algo-1"
    results = {}
    for metric in ["GPUUtilization", "GPUMemoryUtilization", "CPUUtilization", "MemoryUtilization"]:
        r = cw.get_metric_statistics(
            Namespace="/aws/sagemaker/TrainingJobs", MetricName=metric,
            Dimensions=[{"Name": "Host", "Value": host}],
            StartTime=start, EndTime=end, Period=60, Statistics=["Average", "Maximum", "Minimum"])
        pts = sorted(r.get("Datapoints", []), key=lambda p: p["Timestamp"])
        results[metric] = pts
        if not pts:
            print(f"{metric:22}: no datapoints (job may be Starting, or metric not published)")
            continue
        avg = sum(p["Average"] for p in pts) / len(pts)
        lo = min(p["Minimum"] for p in pts)
        hi = max(p["Maximum"] for p in pts)
        print(f"{metric:22}: n={len(pts):3}  avg={avg:5.1f}  min={lo:5.1f}  max={hi:5.1f}")
        # compact per-minute Average sparkline (values) so we can see dips during slow stretches
        print("   per-min avg: " + " ".join(f"{p['Average']:.0f}" for p in pts))

    # verdict heuristic
    g = results.get("GPUUtilization", [])
    c = results.get("CPUUtilization", [])
    if g:
        gavg = sum(p["Average"] for p in g) / len(g)
        cavg = (sum(p["Average"] for p in c) / len(c)) if c else float("nan")
        print("\n[gpuutil] READ:")
        if gavg >= 85:
            print(f"  GPU avg {gavg:.0f}% -> GPU-BOUND: the A10G is saturated; the ~3x cost is real alchemical-MD "
                  f"cost, not fixable by more vCPU. Lever = window-sharding / fewer ns (only if reduce allows).")
        elif gavg <= 65:
            print(f"  GPU avg {gavg:.0f}% (CPU avg {cavg:.0f}%) -> GPU is IDLING a meaningful fraction -> likely "
                  f"CPU-BOUND overhead (MBAR/IO/setup). A higher-vCPU instance (g5.2xlarge, same A10G) likely "
                  f"cuts wall-clock + cost. Worth a shakeout before the A3 fleet.")
        else:
            print(f"  GPU avg {gavg:.0f}% (CPU avg {cavg:.0f}%) -> MIXED; check the per-min dips above against the "
                  f"iteration-time swings. Lean CPU-bound if GPU dips coincide with the 40s iters.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
