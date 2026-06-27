#!/usr/bin/env python3
"""
Verify what the metad runs actually produced — did NR4A1/NR4A2/NR4A3 30 ns jobs COMPLETE and upload
their opened-ensemble outputs to S3, or were they killed by the SageMaker MaxRuntime cap before the
script finished (in which case ProcessingOutput is NOT uploaded and the prefix is empty/partial)?

Lists each s3://<default-bucket>/<prefix>-metad/ and reports the recent SageMaker processing jobs'
status + exit message + MaxRuntime, so we can tell Completed vs Stopped(MaxRuntimeExceeded). Read-only.
"""
import os
import sys


def main():
    try:
        import boto3
    except ImportError:
        sys.exit("pip install boto3")
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")
    s3, sm, sts = boto3.client("s3"), boto3.client("sagemaker"), boto3.client("sts")
    acct = sts.get_caller_identity()["Account"]
    bucket = os.environ.get("BUCKET") or f"sagemaker-{region}-{acct}"
    print(f"bucket = {bucket}", flush=True)

    need = {"nr4a3-lbd-metad.dcd", "metad_manifest.json", "fes.dat"}
    for prefix in ("nr4a3-metad", "nr4a1-metad", "nr4a2-metad"):
        print(f"\n=== s3://{bucket}/{prefix}/ ===")
        resp = s3.list_objects_v2(Bucket=bucket, Prefix=prefix + "/")
        keys = [(o["Key"].split("/")[-1], o["Size"]) for o in resp.get("Contents", [])]
        if not keys:
            print("  (EMPTY — no outputs uploaded)")
        else:
            for name, size in keys:
                print(f"  {name}  {size} bytes")
            have = {n for n, _ in keys}
            missing = need - have
            print(f"  COMPLETE-SET: {'YES' if not missing else 'NO — missing ' + ', '.join(sorted(missing))}")

    print("\n=== recent SageMaker processing jobs ===")
    for frag in ("nr4a1-metad", "nr4a2-metad", "nr4a3-metad"):
        try:
            jobs = sm.list_processing_jobs(NameContains=frag, SortBy="CreationTime",
                                           SortOrder="Descending", MaxResults=2)["ProcessingJobSummaries"]
        except Exception as e:  # noqa: BLE001
            print(f"  {frag}: list failed: {e}"); continue
        for j in jobs:
            d = sm.describe_processing_job(ProcessingJobName=j["ProcessingJobName"])
            cap = d.get("StoppingCondition", {}).get("MaxRuntimeInSeconds")
            print(f"  {j['ProcessingJobName']}: {d['ProcessingJobStatus']}"
                  f" / {d.get('ProcessingJobStatus') == 'Completed' and 'ok' or d.get('ExitMessage', '')[:70]}"
                  f" | MaxRuntime={cap}s")


if __name__ == "__main__":
    main()
