# Run the NR4A3 MD on AWS SageMaker (managed, auto-tears-down)

This is the standard AWS path for the cryptic-pocket MD. SageMaker provisions a GPU, enforces a
**hard MaxRuntime cap**, and **terminates the instance on completion** — nothing to shut off, and it
cannot run away. You only manage credentials.

## ⚠️ Do this FIRST: request a GPU quota (the real blocker for new accounts)
A brand-new AWS account has a **GPU instance quota of 0**, so the first job will be *rejected* until
you raise it. This approval can take **hours to a couple of days** — start it before anything else.
- AWS console → **Service Quotas** → **Amazon SageMaker** → search **`ml.g5.xlarge for processing job usage`**
  → **Request increase** to at least **1**. (If g5 isn't available in your region, request
  `ml.g4dn.xlarge for processing job usage` instead and set that instance in the workflow.)

## One-time setup
1. **Create an AWS account** (aws.amazon.com) — requires a card; basic activation is quick, but see
   the quota note above.
2. **Create the IAM role + CI user** with the provided template (no hand-built IAM):
   - Console → **CloudFormation → Create stack → Upload a template file** → pick
     `deploy/aws-sagemaker.cfn.yaml` → name it `nr4a3-md` → acknowledge "IAM resources" → Create.
   - When it finishes, open the stack's **Outputs** tab — it lists the four values below.
3. **Add three GitHub repo secrets** (repo → Settings → Secrets and variables → Actions → New secret):
   | Secret | Value |
   |---|---|
   | `AWS_ACCESS_KEY_ID` | from stack Outputs |
   | `AWS_SECRET_ACCESS_KEY` | from stack Outputs (shown once) |
   | `SAGEMAKER_ROLE_ARN` | from stack Outputs |

   *(The **region is not a secret** — it's a workflow input that defaults to `us-east-2`. Deploy the
   stack and request the quota in that same region, or override the `region` input at dispatch.)*

## Run it
GitHub → **Actions → "GPU — NR4A3 MD (AWS SageMaker)" → Run workflow** → leave `ns=10` (cheap
validation) → Run. The job submits, SageMaker spins up the GPU, runs the MD, uploads results to
`s3://sagemaker-<region>-<account>/nr4a3-md`, and shuts down.

- **Validation success looks like:** the Action log shows `nvidia-smi` + `OpenMM platform: CUDA`,
  and the S3 prefix has `nr4a3-lbd-md.dcd`. (`nr4a3_md.py` aborts if it can't get CUDA, so it won't
  silently crawl on CPU.)
- Then rerun with **`ns=100`–`200`** for the real cryptic-pocket run.
- Retrieve results: S3 console (or `aws s3 cp s3://.../nr4a3-md ./ --recursive`).

## Cost & safety
- ml.g5.xlarge ≈ $1.4/hr; a 10 ns validation ≈ a few dollars; 100–200 ns ≈ $10–30.
- **Auto-off is triple-covered:** SageMaker terminates the instance when the job ends; the **hard
  `MaxRuntime`** (6 h default, set in `nr4a3_md_sagemaker.py`) kills it if it hangs; and there is no
  long-lived instance to forget.
- To tear everything down later: delete the CloudFormation stack (removes the role + CI user/key).

## Validated working configuration (2026-06-25)
The pipeline has now run end-to-end on GPU: a 10 ns validation MD completed on `ml.g5.xlarge`
(NVIDIA A10G) in **~1h38m**, producing `nr4a3-lbd-md.dcd` (~217 MB) in
`s3://sagemaker-<region>-<account>/nr4a3-md/`. Getting there required six fixes — recorded here so
the **shared ternary pipeline** (`gpu-ternary-aws.yml`, same scaffolding) doesn't re-hit them:

| Symptom | Cause | Fix (committed) |
|---|---|---|
| CloudFormation rejects template | Output logical IDs had underscores (`SAGEMAKER_ROLE_ARN`) | Alphanumeric Output names (`SagemakerRoleArn`…); description says which secret |
| Submit step exits instantly, prints "pip install sagemaker" | `sagemaker>=2.200` now resolves to **v3 SDK**, which dropped `FrameworkProcessor`/`sagemaker.pytorch.PyTorch` import paths | Pin `sagemaker>=2.200,<3` in both AWS workflows |
| `AccessDenied: logs:DescribeLogStreams` after job submits | CI user lacked CloudWatch Logs read; the submit runs `logs=True` | Add `logs:GetLogEvents/DescribeLogStreams/DescribeLogGroups/FilterLogEvents` to the CI user policy (**stack update**) |
| MD aborts: `HTTP 404` fetching the structure | Hardcoded AFDB URL `AF-Q92570-F1-model_v4.pdb` went stale | Resolve the URL from the AFDB **API** (version-agnostic) + versioned fallbacks |
| MD aborts exit 2: `OpenMM platform: CPU` | The **pip** OpenMM wheel has no usable CUDA platform on the DLC | Install OpenMM from **conda-forge** in an isolated env in `entry.py` |
| OpenMM still CPU; CUDA listed but unused | conda pulled CUDA **12.9** runtime vs the box driver's CUDA **12.8** → silent fallback | `CONDA_OVERRIDE_CUDA=12.8` + `cuda-version=12.8` on env create; **force** the CUDA platform in `nr4a3_md.py` so a mismatch errors instead of silently using CPU |

**Net working recipe (already in the committed scripts):** v2 SageMaker SDK · conda-forge OpenMM with
`CONDA_OVERRIDE_CUDA`/`cuda-version` pinned to the **driver's** CUDA version · AFDB API for the
structure · explicit CUDA platform · `entry.py` propagates the MD exit code (so a failed MD fails the
job instead of a false green). If a future DLC ships a newer GPU driver, bump the `12.8` pins in
`sagemaker_src/entry.py` to match `nvidia-smi`'s CUDA version.

Don't run a long (`ns=100+`) job until an `ns=10` validation is green in the target region.
