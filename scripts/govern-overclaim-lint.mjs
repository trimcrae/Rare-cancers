#!/usr/bin/env node
/**
 * GOVERN/ASSURE over-claim linter — the "Trusted Evals" pillar for the
 * NR4A3-degrader program, made runnable.
 *
 * It encodes the language-discipline rules from STRATEGY.md ("Language discipline
 * (apply everywhere, incl. the manuscript at fold time)") and the repo's
 * medical-integrity rule as automatic checks over any outward-facing artifact
 * (manuscript, SI, preprint, grant text, client deliverable, outreach email).
 *
 * Purpose (per degrader-startup-plan-exo.md §5): catch the single existential
 * risk for a solo, integrity-first computational shop — a credibility-destroying
 * over-claim (implied efficacy / safety / clinical readiness / unconditional
 * binding / "recovered degradation") drifting into a shipped artifact. This is
 * the Quiet-Drift guard: a hedge quietly softened over many edits is exactly what
 * a human review misses and a linter catches.
 *
 * Usage:
 *   node scripts/govern-overclaim-lint.mjs [file ...]        # lint named files
 *   node scripts/govern-overclaim-lint.mjs                    # lint the default outward-facing set
 *   node scripts/govern-overclaim-lint.mjs --all              # lint all research/manuscripts/*.md
 *
 * Exit code: 0 if no ERROR-severity findings; 1 if any ERROR found. WARN/INFO
 * never fail the run (they are prompts for a human judgment call).
 *
 * NOTE: this is a lexical guard, not a semantic one. It reduces the surface for
 * over-claims; it does NOT replace the red-team + human sign-off gate. A clean
 * lint is necessary, not sufficient.
 */

import { readFileSync, existsSync } from 'node:fs';
import { globSync } from 'node:fs';

// ---- Rule table -------------------------------------------------------------
// severity: ERROR = banned language (must fix before an artifact ships)
//           WARN  = disciplined-form preferred; confirm it's the allowed usage
//           INFO  = presence check / reminder
// Each rule: {id, severity, re, why, fix}. `re` is matched case-insensitively per line.
// `guard` (optional): a same-line regex that, if present, SUPPRESSES the finding
// (an allowed context, e.g. an explicit "conditional"/"predicted" hedge already there).

const RULES = [
  // --- Efficacy / clinical / safety: never imply (STRATEGY.md "Never imply ...") ---
  { id: 'efficacy', severity: 'ERROR',
    re: /\befficac(y|ious)\b/, why: 'Implies therapeutic benefit; never claim efficacy.',
    fix: 'Delete or reframe as a computational/biochemical prediction.' },
  { id: 'therapeutic-window', severity: 'ERROR',
    re: /\btherapeutic window\b/, why: 'Implies a clinical safety/efficacy margin.',
    fix: 'Remove; not supported by in-silico work.' },
  { id: 'clinical-readiness', severity: 'ERROR',
    re: /\b(clinical(ly)? readiness|ready for (the )?clinic|clinic[- ]ready|clinically ready)\b/,
    why: 'Implies clinical readiness.', fix: 'Remove; the asset is a computational prediction.' },
  { id: 'safe-claim', severity: 'ERROR',
    re: /\b(is safe|proven safe|well[- ]tolerated|favorable safety|safety profile)\b/,
    why: 'Implies a safety claim.', fix: 'Remove any safety assertion.' },
  { id: 'cure', severity: 'ERROR',
    re: /\bcur(e|es|ed|ative)\b/, why: 'Implies a cure.', fix: 'Remove.' },
  { id: 'proteome-wide-selectivity', severity: 'ERROR',
    re: /\bproteome[- ]wide selectiv/, why: 'Un-demonstrable selectivity claim.',
    fix: 'Scope to the tested paralogues/anti-targets only.' },

  // --- Binding / affinity: conditional discipline (Mandatory Change 2 & 3) ---
  { id: 'binds-at-all', severity: 'ERROR',
    re: /\b(binds at all|does bind\b|proven to bind|confirms? binding|demonstrates binding)\b/,
    why: 'ABFE/RBFE do NOT prove a compound "binds at all".',
    fix: 'Use "compatible with the hypothesized conditional bound state".' },
  { id: 'true-binding-stronger', severity: 'ERROR',
    re: /\b(true binding (is )?likely stronger|likely binds (more )?strong|binding is likely stronger)\b/,
    why: 'STRATEGY.md deletes this — preselecting a rare open state usually OMITS a positive penalty.',
    fix: 'Delete; bias can go either way.' },
  { id: 'unconditional-affinity', severity: 'WARN',
    re: /\b(absolute|unconditional) (binding )?affinit/,
    why: 'Affinity in a pre-opened pocket is conditional (ΔG_bind|open), not observable.',
    guard: /\bconditional\b/,
    fix: 'Label as conditional on the chosen open state, or integrate ΔG_open.' },

  // --- Degradation language (Mandatory Change 4) ---
  { id: 'recovered-degradation', severity: 'ERROR',
    re: /\brecover(ed|s|ing)? degradation\b/,
    why: 'Never say the workflow "recovered degradation".',
    fix: 'Use "produced a surrogate score concordant with the reported outcome".' },
  { id: 'degrades-claim', severity: 'WARN',
    re: /\b(degrades|degradation of) NR4A3\b/, guard: /\bpredict|surrogate|concordan|in silico|computational/,
    why: 'Ensure degradation is framed as predicted/surrogate, not demonstrated.',
    fix: 'Qualify: predicted / surrogate-concordant, not experimentally shown.' },

  // --- Candidate / hit language (Language discipline list) ---
  { id: 'selective-hit', severity: 'WARN',
    re: /\bselective hit\b/, why: '"selective hit" → "predicted selective candidate".',
    fix: 'Use "predicted selective candidate".' },
  { id: 'nr4a3-selective-bare', severity: 'INFO',
    re: /\bNR4A3[- ]selective\b/, guard: /\bpredicted\b/,
    why: 'Prefer "predicted NR4A-paralogue-selective".',
    fix: 'Prepend "predicted" and scope to paralogues tested.' },
  { id: 'synthesis-ready', severity: 'WARN',
    re: /\bsynthesis[- ]ready\b/,
    why: '"synthesis-ready" is only earned with exact structures, routes, building-block availability, etc.',
    fix: 'Use "computationally prioritized, structure-defined and retrosynthetically annotated candidate matrix".' },
  { id: 'selective-drug', severity: 'ERROR',
    // Exclude medchem terms (drug-like, drug-likeness, druggable, drug repurposing,
    // drug discovery/design) via negative lookahead; suppress when the line is about
    // an EXISTING/approved/repurposed real drug (not our asset).
    re: /\b(selective drug|a drug|the drug|our drug)\b(?!-?lik|gab|\s+repurpos|\s+discover|\s+design)/,
    guard: /\b(existing|approved|marketed|repurpos|known drug|off[- ]the[- ]shelf)\b/,
    why: 'The asset is not a drug.', fix: 'Use "predicted selective candidate" / "compound".' },

  // --- Matrix arithmetic reminder (INFO) ---
  { id: 'matrix-6-12', severity: 'INFO',
    re: /\b6[-–]12\b/, guard: /downselect|downselection|after (a )?cheap|preregistered/,
    why: 'The primary matrix is 24–36 before controls; 6–12 requires a preregistered downselection.',
    fix: 'State the 24–36 primary count and the downselection explicitly.' },
];

// ---- File selection ---------------------------------------------------------
// The default set is the actual outward-facing CLAIM artifacts. Strategy/meta docs
// (STRATEGY.md, degrader-startup-plan-exo.md) intentionally name the forbidden terms
// to prohibit them, so they are NOT linted by default — pass them explicitly if needed.
// Grant drafts and client deliverables should be added here as they are created.
const DEFAULT_OUTWARD = [
  'research/manuscripts/nr4a3-degrader-paper.md',
  'research/manuscripts/nr4a3-degrader-paper-SI.md',
  'research/manuscripts/nr4a3-degrader-outreach-emails.md',
  'research/manuscripts/degrader-grant-draft.md',
];

function pickFiles(argv) {
  const args = argv.slice(2);
  if (args.includes('--all')) return globSync('research/manuscripts/*.md');
  const named = args.filter((a) => !a.startsWith('--'));
  if (named.length) return named;
  return DEFAULT_OUTWARD.filter(existsSync);
}

// Suppress findings on lines that are PROHIBITIONS or RULE STATEMENTS rather than
// claims — a lexical linter must not flag "never claim efficacy" as an efficacy
// claim. Two guards, applied to every rule:
//   META_LINE     — the line is discussing the discipline itself (mapping arrows,
//                   "language discipline", "forbidden", etc.).
//   NEGATION_LINE — the term appears under a negation/prohibition ("never", "not",
//                   "nothing ... claims", "avoid", "delete", quotes-as-forbidden).
// Trade-off: a genuine over-claim co-located with a negation word on the SAME line
// can be masked (rare). The red-team + human sign-off gate remains the real check.
// NOTE: do NOT treat a bare "→" as a meta marker — manuscripts use it as a
// scientific arrow (e.g. "binder→degradation-selectivity"), which would wrongly
// suppress real findings. Only quotes-around-a-mapping ("x" → "y") counts as meta.
const META_LINE = /("[^"]*"\s*→|language discipline|reframe|forbidden|banned|disciplin|over[- ]?claim|litmus|constraint layer|disqualif)/i;
const NEGATION_LINE = /\b(never|not|no|nothing|none|neither|nor|without|don'?t|does ?n'?t|do not|avoid|cannot|can'?t|isn'?t|aren'?t|won'?t|must not|should ?n'?t|refus|forbid|delete|remove|make no|makes no)\b/i;
// Analysis is SENTENCE-based (paragraphs joined, then split on sentence boundaries),
// so a negation/meta marker anywhere in the SAME sentence suppresses the finding —
// but a negation in a DIFFERENT sentence of the same paragraph does not (which would
// wrongly hide a real over-claim). Fenced code blocks are skipped.

// Split a document into paragraph segments (blank-line separated), joining wrapped
// lines, skipping fenced code blocks, and tracking the start line of each segment.
function segment(text) {
  const raw = text.split(/\r?\n/);
  const segs = [];
  let inFence = false, buf = '', start = 0;
  const flush = () => { if (buf.trim()) segs.push({ startLine: start, text: buf }); buf = ''; };
  for (let i = 0; i < raw.length; i++) {
    const ln = raw[i];
    if (/^\s*```/.test(ln)) { flush(); inFence = !inFence; continue; }
    if (inFence) continue;
    if (/^\s*$/.test(ln)) { flush(); continue; }
    if (!buf) start = i + 1;
    buf += (buf ? ' ' : '') + ln.trim();
  }
  flush();
  return segs;
}

// Split a joined paragraph into rough sentences.
function sentences(par) {
  return par.split(/(?<=[.!?;:])\s+(?=[A-Z(“"'*\[])/);
}

function lintFile(path) {
  const findings = [];
  let text;
  try {
    text = readFileSync(path, 'utf8');
  } catch {
    return { path, error: 'unreadable', findings };
  }
  for (const seg of segment(text)) {
    for (const s of sentences(seg.text)) {
      if (META_LINE.test(s)) continue;     // rule-statement sentence, not a claim
      if (NEGATION_LINE.test(s)) continue; // prohibition/negation of the term, not a claim
      for (const rule of RULES) {
        if (rule.re.test(s)) {
          if (rule.guard && rule.guard.test(s)) continue;
          findings.push({ rule, line: seg.startLine, text: s.trim().slice(0, 160) });
        }
      }
    }
  }
  return { path, findings };
}

// ---- Run --------------------------------------------------------------------
const files = pickFiles(process.argv);
if (!files.length) {
  console.log('No files to lint (no default outward-facing artifacts found).');
  process.exit(0);
}

let errors = 0, warns = 0, infos = 0;
const SEV_ORDER = { ERROR: 0, WARN: 1, INFO: 2 };
console.log(`GOVERN/ASSURE over-claim lint — ${files.length} file(s)\n`);

for (const f of files) {
  const { path, error, findings } = lintFile(f);
  if (error) { console.log(`  ?? ${path}: ${error}`); continue; }
  if (!findings.length) { console.log(`  ✔ ${path} — clean`); continue; }
  console.log(`  ✘ ${path} — ${findings.length} finding(s)`);
  findings.sort((a, b) => SEV_ORDER[a.rule.severity] - SEV_ORDER[b.rule.severity] || a.line - b.line);
  for (const { rule, line, text } of findings) {
    if (rule.severity === 'ERROR') errors++;
    else if (rule.severity === 'WARN') warns++;
    else infos++;
    console.log(`      [${rule.severity}] ${path}:${line}  (${rule.id})`);
    console.log(`         "${text}"`);
    console.log(`         → ${rule.why} FIX: ${rule.fix}`);
  }
  console.log('');
}

console.log(`\nSummary: ${errors} ERROR, ${warns} WARN, ${infos} INFO`);
if (errors) {
  console.log('FAIL — resolve ERROR-severity over-claims before this artifact ships.');
  process.exit(1);
}
console.log('PASS (no banned over-claims). WARN/INFO are human judgment calls — review before shipping.');
process.exit(0);
