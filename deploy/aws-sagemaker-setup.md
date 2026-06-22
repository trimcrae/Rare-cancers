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

## Notes / expect iteration
This pipeline is built but **untested from the dev sandbox** (no AWS access here). The most likely
first-run snags are the **GPU quota** (above) and the SageMaker DLC `framework_version`/`py_version`
pairing in `nr4a3_md_sagemaker.py` — if the job won't start, paste the Action-log error and it's a
quick fix. Don't run a long (`ns=100+`) job until the `ns=10` validation is green.
