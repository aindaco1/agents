import { createHash } from 'node:crypto';
import { readFile, realpath, mkdir, writeFile, rename } from 'node:fs/promises';
import { resolve, join, sep } from 'node:path';
import { pathToFileURL } from 'node:url';
import { parseArgs } from 'node:util';

const lockUrl = new URL('../references/platform-lock.json', import.meta.url);
export async function loadPlatform(directory) {
  if (!directory) throw new Error('Set DUSTWAVE_PLATFORM_DIR or --platform-root to the locked Platform checkout');
  const root = await realpath(resolve(directory));
  const lock = JSON.parse(await readFile(lockUrl, 'utf8'));
  for (const [file, expected] of Object.entries(lock.files)) {
    const path = await realpath(join(root, file));
    if (!path.startsWith(root + sep) || hash(await readFile(path)) !== expected) {
      throw new Error('Platform pin mismatch: restore the locked shared dependency');
    }
  }
  return import(pathToFileURL(join(root, 'packages/test-core/src/jev.js')).href);
}

export const POLICY = Object.freeze({ minimumMargin: 0.10, models: ['jev-1.13.0'] });
export const PRICE = Object.freeze({ inputUsdPerMillion: 0.042, date: '2026-09-23', billingVerified: false });
const hash = value => createHash('sha256').update(value).digest('hex');
const object = value => value && typeof value === 'object' && !Array.isArray(value);

export function summarize(report) {
  const summary = { correct: 0, falsePasses: 0, falseFailures: 0, reviews: 0,
    unevaluated: report.questionCount, decisionFlips: 0, inputTokens: 0, outputTokens: 0,
    usageComplete: report.complete, resolvedModels: [], requestLatencyMs: {} };
  const decisions = new Map();
  const times = [];
  for (const row of report.cases) {
    if (row.elapsedMs !== undefined) times.push(row.elapsedMs);
    if (!row.result) continue;
    summary.inputTokens += row.result.usage.input_tokens;
    summary.outputTokens += row.result.usage.output_tokens;
    if (!summary.resolvedModels.includes(row.result.model)) summary.resolvedModels.push(row.result.model);
    for (const [key, value] of Object.entries(row.result.findings)) {
      summary.unevaluated--;
      if (value.decision === 'review') summary.reviews++;
      else if (value.decision === row.expected[key]) summary.correct++;
      else if (value.decision === 'pass') summary.falsePasses++;
      else summary.falseFailures++;
      const id = `${row.caseId}:${key}`;
      if (decisions.has(id) && decisions.get(id) !== value.decision) summary.decisionFlips++;
      decisions.set(id, value.decision);
    }
  }
  times.sort((a, b) => a - b);
  if (times.length) summary.requestLatencyMs = {
    median: times.length % 2 ? times[Math.floor(times.length / 2)] : (times[times.length / 2 - 1] + times[times.length / 2]) / 2,
    p95: times[Math.ceil(times.length * 0.95) - 1], sum: times.reduce((a, b) => a + b, 0),
  };
  summary.estimatedInferenceUsd = summary.inputTokens * PRICE.inputUsdPerMillion / 1e6;
  summary.estimatedWithCreditFeeUsd = summary.estimatedInferenceUsd * 1.05;
  return summary;
}

export async function evaluate(api, plan, { call, onProgress = async () => {} } = {}) {
  const { rows, ...metadata } = plan;
  const report = { schemaVersion: 1, advisory: true, complete: false, releaseAccepted: false,
    networkAttempts: 0, createdAt: new Date().toISOString(), policy: POLICY, ...metadata, cases: [] };
  const save = async () => { report.summary = summarize(report); await onProgress(report); };
  await save();
  for (const { payload, ...metadata } of rows) {
    const row = { ...metadata, request: payload };
    report.cases.push(row);
    if (call) {
      report.networkAttempts++;
      row.status = 'pending';
      // Persist intent before transport; a pending record may or may not be billed.
      await save();
      const started = performance.now();
      try {
        const raw = await call(payload);
        const judged = api.judgeJevResponse(raw, payload.input.questions, POLICY);
        // Drop arbitrary provider/debug metadata from both evidence and results.
        row.result = { model: judged.model, usage: {
          input_tokens: judged.usage.input_tokens, output_tokens: judged.usage.output_tokens,
        }, findings: judged.findings };
        row.response = { model: row.result.model, usage: row.result.usage, answers:
          Object.fromEntries(Object.entries(row.result.findings).map(([key, finding]) => [key, {
            type: 'choice', choice: finding.choice, probabilities: finding.probabilities,
          }])) };
        row.status = 'evaluated';
      } catch {
        row.status = 'unavailable';
        row.error = 'Unavailable: provider request or response validation failed; no retry';
        report.error = row.error;
      } finally {
        row.elapsedMs = Math.round(performance.now() - started);
      }
    }
    await save();
    if (report.error) return report;
  }
  report.complete = typeof call === 'function';
  await save();
  return report;
}

export function prepare(api, corpus, { repeats = 1, maxQuestions = 64, maxEstimatedUsd = 0.10, splitQuestions = false } = {}) {
  if (!Number.isSafeInteger(repeats) || repeats < 1 || repeats > 3 ||
      !Number.isSafeInteger(maxQuestions) || maxQuestions < 1 || maxQuestions > 64 ||
      !Number.isFinite(maxEstimatedUsd) || maxEstimatedUsd <= 0 || maxEstimatedUsd > 0.10) {
    throw new Error('Invalid budget: repeats 1–3, questions 1–64, estimate >0 and <=0.10');
  }
  if (corpus?.schemaVersion !== 1 || corpus.classification !== 'public-synthetic' ||
      !Array.isArray(corpus.cases) || !corpus.cases.length) throw new Error('Public synthetic corpus required');
  const ids = new Set();
  let questionCount = 0;
  for (const item of corpus.cases) {
    if (!/^[a-z0-9-]+$/.test(item.id || '') || ids.has(item.id) ||
        typeof item.candidate !== 'string' || !item.candidate.trim() ||
        !object(item.requirements) || !Object.keys(item.requirements).length || !object(item.expected) ||
        Object.keys(item.requirements).sort().join() !== Object.keys(item.expected).sort().join() ||
        !Object.values(item.expected).every(x => ['pass', 'fail'].includes(x))) throw new Error('Invalid labeled case');
    ids.add(item.id);
    questionCount += Object.keys(item.requirements).length * repeats;
  }
  if (questionCount > maxQuestions) throw new Error('Exceeded question budget');
  const reservedEstimateUsd = questionCount * 32000 * PRICE.inputUsdPerMillion / 1e6;
  if (reservedEstimateUsd > maxEstimatedUsd) throw new Error('Exceeded spending budget');
  const rows = [];
  for (let repeat = 1; repeat <= repeats; repeat++) {
    for (const item of corpus.cases) {
      const groups = splitQuestions ? Object.entries(item.requirements).map(([key, value]) => ({ [key]: value })) : [item.requirements];
      for (const requirements of groups) {
        const payload = api.createJevRequest(item.candidate, requirements, { reference: item.reference });
        rows.push({ id: `${item.id}:${repeat}:${Object.keys(requirements).join('+')}`, caseId: item.id, repeat,
          payload, expected: Object.fromEntries(Object.keys(requirements).map(key => [key, item.expected[key]])),
          requestSha256: hash(JSON.stringify(payload)) });
      }
    }
  }
  return { rows, questionCount, requestCount: rows.length, reservedEstimateUsd, repeats, splitQuestions,
    classification: corpus.classification, labelProvenance: corpus.labelProvenance ?? 'Not provided; not a calibration set.',
    corpusSha256: hash(JSON.stringify(corpus)), policySha256: hash(JSON.stringify(POLICY)), price: PRICE };
}

async function main() {
  const { values } = parseArgs({ options: {
    'platform-root': { type: 'string' }, out: { type: 'string' }, live: { type: 'boolean', default: false },
    repeats: { type: 'string', default: '1' }, 'max-questions': { type: 'string', default: '64' },
    'max-estimated-usd': { type: 'string', default: '0.10' }, 'split-questions': { type: 'boolean', default: false },
    help: { type: 'boolean', default: false },
  } });
  if (values.help) {
    console.log('node benchmark.mjs --platform-root PATH --out NEW_DIR [--live] [--repeats 1..3] [--split-questions] [--max-questions 64] [--max-estimated-usd 0.10]\nDefault is a zero-network preview of built-in public synthetic controls. Live requires CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN in process environment.');
    return 0;
  }
  if (!values.out) throw new Error('--out NEW_DIR required');
  const api = await loadPlatform(values['platform-root'] || process.env.DUSTWAVE_PLATFORM_DIR);
  const corpus = JSON.parse(await readFile(new URL('../references/cases.json', import.meta.url), 'utf8'));
  const plan = prepare(api, corpus, { repeats: Number(values.repeats), maxQuestions: Number(values['max-questions']),
    maxEstimatedUsd: Number(values['max-estimated-usd']), splitQuestions: values['split-questions'] });
  plan.runnerSha256 = hash(await readFile(new URL(import.meta.url)));
  plan.dependencyLockSha256 = hash(await readFile(lockUrl));
  let call;
  if (values.live) {
    const accountId = process.env.CLOUDFLARE_ACCOUNT_ID;
    const token = process.env.CLOUDFLARE_API_TOKEN;
    if (!/^[a-fA-F0-9]{32}$/.test(accountId || '') || !token?.trim()) throw new Error('Cloudflare credentials missing or invalid');
    call = payload => api.callCloudflareJev(payload, { accountId, token, timeoutMs: 15000 });
  }
  const out = resolve(values.out);
  await mkdir(resolve(out, '..'), { recursive: true });
  await mkdir(out); // Refuse an existing evidence directory; never overwrite a prior run.
  const onProgress = async report => {
    const temporary = join(out, 'report.json.partial');
    await writeFile(temporary, JSON.stringify(report, null, 2) + '\n', { mode: 0o600 });
    await rename(temporary, join(out, 'report.json'));
  };
  const report = await evaluate(api, plan, { call, onProgress });
  console.log(JSON.stringify({ mode: values.live ? 'live' : 'preview', complete: report.complete,
    releaseAccepted: false, questionCount: report.questionCount, networkAttempts: report.networkAttempts,
    reservedEstimateUsd: report.reservedEstimateUsd, ...report.summary, report: join(out, 'report.json') }, null, 2));
  if (report.error) return 2;
  return values.live && (report.summary.falsePasses || report.summary.falseFailures || report.summary.reviews) ? 1 : 0;
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  try { process.exitCode = await main(); }
  catch {
    console.error('Jev preflight/evidence failed. Check --help, the dependency pin, budgets, credentials, and use a new output directory. No automatic retry; secret details suppressed.');
    process.exitCode = 2;
  }
}
