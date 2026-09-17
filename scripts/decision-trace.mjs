#!/usr/bin/env node
/**
 * decision-trace.mjs — emit an append-only decision-trace record.
 *
 * The LEARN-layer substrate from degrader-startup-plan-exo.md §5 and
 * degrader-moat-decision-traces.md: every spend-gated rung / campaign decision
 * emits one structured trace. The append-only JSONL log is the "log is the agent"
 * substrate beneath the why-layer; the accumulated traces are the reproducibility
 * record that becomes the Value Moat (a competitor can rent the same GPUs but not
 * clone the benchmarked decision history).
 *
 * This mirrors the repo's existing spend-gated ladder (STRATEGY.md rungs) — each
 * GO/NO-GO is exactly a decision trace.
 *
 * Usage (all fields optional except --rung and --decision):
 *   node scripts/decision-trace.mjs \
 *     --rung step1_pilot_cmpd19 --decision GO \
 *     --inputs "cmpd19->cw_ev_5nh2 edge, Modal L4 spot" \
 *     --result "ΔΔG_bind=+1.84 kcal/mol, both legs MBAR-converged" \
 *     --gate "reproducible + receptor-sensitive + pocket stable" \
 *     --cost-usd 22 --gpu-h 3.5 \
 *     --rationale "pilot crux cleared; replicas carried to fan-out" \
 *     --by trimcrae
 *
 * Reads/writes: research/degrader/decision-traces.jsonl (append-only).
 * Timestamps: the runtime forbids Date.now()/new Date() in some harness contexts,
 * so pass --at "2026-07-19T14:30-04:00" to stamp; if omitted the field is left
 * null and can be filled by the caller.
 */

import { appendFileSync, mkdirSync, existsSync, readFileSync } from 'node:fs';

const LOG = 'research/degrader/decision-traces.jsonl';

function parseArgs(argv) {
  const a = {};
  const args = argv.slice(2);
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith('--')) {
      const key = args[i].slice(2);
      const val = args[i + 1] && !args[i + 1].startsWith('--') ? args[++i] : 'true';
      a[key] = val;
    }
  }
  return a;
}

const a = parseArgs(process.argv);

if (a.list) {
  if (!existsSync(LOG)) { console.log('(no traces yet)'); process.exit(0); }
  const lines = readFileSync(LOG, 'utf8').trim().split(/\r?\n/).filter(Boolean);
  console.log(`${lines.length} decision trace(s):`);
  for (const l of lines) {
    try {
      const t = JSON.parse(l);
      console.log(`  [${t.at || 'unstamped'}] ${t.rung} → ${t.decision}  ($${t.cost_usd ?? '?'}, ${t.gpu_h ?? '?'} GPU-h)`);
    } catch { console.log('  (unparseable line)'); }
  }
  process.exit(0);
}

if (!a.rung || !a.decision) {
  console.error('Required: --rung <id> --decision <GO|NO-GO|HOLD|INDETERMINATE|note>');
  console.error('Run with --list to view existing traces.');
  process.exit(2);
}

const DECISIONS = ['GO', 'NO-GO', 'HOLD', 'INDETERMINATE', 'SKIP', 'NOTE'];
if (!DECISIONS.includes(a.decision.toUpperCase())) {
  console.error(`--decision must be one of ${DECISIONS.join(', ')} (got "${a.decision}")`);
  process.exit(2);
}

const trace = {
  schema: 'decision-trace/v1',
  at: a.at || null,                       // ISO-8601 ET; null if unstamped (harness-safe)
  rung: a.rung,                            // STRATEGY.md milestone id
  decision: a.decision.toUpperCase(),      // GO | NO-GO | HOLD | INDETERMINATE | SKIP | NOTE
  inputs: a.inputs || null,                // what was run / which systems
  result: a.result || null,                // the observed result the decision keys on
  gate: a.gate || null,                    // the GO/NO-GO test that was applied
  cost_usd: a.cost_usd != null ? Number(a.cost_usd) : null,   // realized spot $
  gpu_h: a.gpu_h != null ? Number(a.gpu_h) : null,            // realized GPU-hours (COGS input)
  rationale: a.rationale || null,          // why this decision, incl. any caveats
  by: a.by || 'trimcrae',                  // named human owner (Fiduciary Wedge)
  final_call: a.by ? 'human' : 'human',    // human-or-agent final call flag (always human here)
};

mkdirSync('research/degrader', { recursive: true });
appendFileSync(LOG, JSON.stringify(trace) + '\n');
console.log(`Appended decision trace: ${trace.rung} → ${trace.decision}`);
console.log(JSON.stringify(trace, null, 2));
