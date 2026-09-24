import { createHash, randomUUID } from 'node:crypto';
import { readFile, writeFile, rename, rm, mkdir, realpath } from 'node:fs/promises';
import { homedir } from 'node:os';
import { join, resolve, dirname } from 'node:path';
import { parseArgs } from 'node:util';
import { prepare, evaluate, loadPlatform } from './benchmark.mjs';

const hash = value => createHash('sha256').update(value).digest('hex');
const pick = (value, keys) => Object.fromEntries(keys.filter(key => value[key] !== undefined).map(key => [key, value[key]]));

// Rebuild every evidence layer from known fields. Never spread provider objects.
function projectEvidence(report) {
  const evidence = pick(report, ['schemaVersion', 'advisory', 'complete', 'releaseAccepted', 'networkAttempts',
    'createdAt', 'questionCount', 'requestCount', 'reservedEstimateUsd', 'repeats', 'splitQuestions',
    'classification', 'corpusSha256', 'sourceControlsSha256', 'policySha256', 'runnerSha256', 'dependencyLockSha256', 'error']);
  evidence.policy = pick(report.policy, ['minimumMargin', 'models']);
  evidence.price = pick(report.price, ['inputUsdPerMillion', 'date', 'billingVerified']);
  evidence.summary = pick(report.summary, ['correct', 'falsePasses', 'falseFailures', 'reviews', 'unevaluated',
    'decisionFlips', 'inputTokens', 'outputTokens', 'usageComplete', 'resolvedModels', 'estimatedInferenceUsd', 'estimatedWithCreditFeeUsd']);
  evidence.summary.requestLatencyMs = pick(report.summary.requestLatencyMs, ['median', 'p95', 'sum']);
  evidence.cases = report.cases.map(row => {
    const result = pick(row, ['id', 'caseId', 'repeat', 'requestSha256', 'status', 'elapsedMs', 'error']);
    result.expected = Object.fromEntries(Object.entries(row.expected));
    if (row.result) {
      scanEvidence(row.result.model);
      // A field-name allowlist is insufficient when a provider puts prose in model.
      if (row.result.model.length > 128 || !/^jev-\d+\.\d+\.\d+(?:-[a-z0-9.-]+)?$/.test(row.result.model)) {
        throw new Error('Invalid Jev model identifier; evidence refused');
      }
      result.result = {
        model: row.result.model,
        usage: pick(row.result.usage, ['input_tokens', 'output_tokens']),
        findings: Object.fromEntries(Object.entries(row.result.findings).map(([key, finding]) => [key, {
          ...pick(finding, ['choice', 'margin', 'decision']),
          probabilities: pick(finding.probabilities, ['pass', 'fail', 'uncertain']),
        }])),
      };
      result.response = { model: result.result.model, usage: result.result.usage,
        answers: Object.fromEntries(Object.entries(result.result.findings).map(([key, finding]) => [key, {
          type: 'choice', choice: finding.choice, probabilities: finding.probabilities,
        }])) };
    }
    return result;
  });
  return evidence;
}

function scanEvidence(value) {
  // A complete 32-hex token is account-shaped; 64-hex provenance hashes are not.
  const forbidden = /cfoat_|cfort_|Bearer |(?<![a-f0-9])[a-f0-9]{32}(?![a-f0-9])/i;
  if (typeof value === 'string' && forbidden.test(value)) throw new Error('Evidence contains credential-shaped data; refused');
  if (Array.isArray(value)) value.forEach(scanEvidence);
  else if (value && typeof value === 'object') {
    for (const [key, item] of Object.entries(value)) { scanEvidence(key); scanEvidence(item); }
  }
}

export async function verifyEvidence(path) {
  const text = await readFile(path, 'utf8');
  const parsed = JSON.parse(text);
  scanEvidence(text);
  scanEvidence(parsed); // Also catch JSON-escaped credentials in keys and values.
  return parsed;
}

async function writeEvidence(out, evidence, first) {
  scanEvidence(evidence);
  const target = first ? out : `${out}.partial-${randomUUID()}`;
  let owned = false;
  try {
    await writeFile(target, JSON.stringify(evidence, null, 2) + '\n', { flag: 'wx', mode: 0o600 });
    owned = true;
    await verifyEvidence(target);
    if (!first) await rename(target, out);
    return await verifyEvidence(out);
  } catch (error) {
    if (owned) await rm(target, { force: true });
    throw error;
  }
}

export async function runProbe({ controls, category, maxUsd, out, accountIdFrom, platformRoot }, {
  env = process.env, home = homedir(), now, fetchTarget = globalThis.fetch,
  progress = message => console.error(message),
} = {}) {
  if (!controls || !out) throw new Error('--controls and --out are required');
  const source = await readFile(controls);
  const api = await loadPlatform(platformRoot || env.DUSTWAVE_PLATFORM_DIR);
  const plan = prepareProbe(api, JSON.parse(source), { category, maxUsd });
  plan.sourceControlsSha256 = hash(source);
  plan.runnerSha256 = hash(await readFile(new URL(import.meta.url)));
  plan.dependencyLockSha256 = hash(await readFile(new URL('../references/platform-lock.json', import.meta.url)));
  const credentials = await discoverCredentials({ env, home, now, accountIdFrom });
  const destination = resolve(out);
  await mkdir(dirname(destination), { recursive: true });
  let first = true;
  let persisted;
  await evaluate(api, plan, {
    onProgress: async report => {
      persisted = await writeEvidence(destination, projectEvidence(report), first);
      first = false;
      progress(`Jev probe: ${report.networkAttempts}/${report.requestCount} attempts; complete=${report.complete}`);
    },
    call: payload => api.callCloudflareJev(payload, { ...credentials, fetchTarget, timeoutMs: 15000 }),
  });
  return persisted;
}

const AUTH_HELP = 'Wrangler OAuth missing, invalid, or expires within 15 minutes. Run wrangler login manually, then use a new --out path; or set CLOUDFLARE_API_TOKEN. No automatic refresh.';

export async function discoverCredentials({ env = process.env, home = homedir(), now, accountIdFrom } = {}) {
  let accountId = env.CLOUDFLARE_ACCOUNT_ID;
  if (!accountId && accountIdFrom) {
    try { accountId = JSON.parse(await readFile(accountIdFrom, 'utf8')).cloudflare_account_id; }
    catch { throw new Error('Cannot read account JSON with cloudflare_account_id'); }
  }
  if (typeof accountId !== 'string' || !/^[a-fA-F0-9]{32}$/.test(accountId)) {
    throw new Error('Cloudflare account ID missing or invalid');
  }
  if (env.CLOUDFLARE_API_TOKEN?.trim()) return { accountId, token: env.CLOUDFLARE_API_TOKEN };
  let cache;
  try { cache = await readFile(join(home, 'Library/Preferences/.wrangler/config/default.toml'), 'utf8'); }
  catch { throw new Error(AUTH_HELP); }
  // Deliberately accept only Wrangler's top-level quoted scalar format, fail closed otherwise.
  const scalar = key => {
    const top = cache.split(/^\s*\[/m)[0];
    const matches = [...top.matchAll(new RegExp(`^\\s*${key}\\s*=\\s*["']([^"'\\r\\n]*)["']\\s*(?:#.*)?$`, 'gm'))];
    return matches.length === 1 ? matches[0][1] : undefined;
  };
  const token = scalar('oauth_token');
  const expiration = Date.parse(scalar('expiration_time'));
  // Read the live clock after I/O; an earlier snapshot can cross the safety window.
  if (!token?.trim() || !Number.isFinite(expiration) || expiration - (now ?? Date.now()) <= 15 * 60 * 1000) {
    throw new Error(AUTH_HELP);
  }
  return { accountId, token };
}

export function prepareProbe(api, controls, { category, maxUsd } = {}) {
  if (!Number.isFinite(maxUsd) || maxUsd <= 0 || maxUsd > 0.10) {
    throw new Error('Required spending budget --max-usd must be >0 and <=0.10');
  }
  let selected = controls;
  if (category !== undefined) {
    if (!category || !Array.isArray(controls?.cases)) throw new Error('Invalid controls category');
    selected = { ...controls, cases: controls.cases.filter(item => item.category === category) };
    if (!selected.cases.length) throw new Error('No controls match category');
  }
  return prepare(api, selected, { maxEstimatedUsd: maxUsd });
}

async function main() {
  const { values } = parseArgs({ options: {
    controls: { type: 'string' }, category: { type: 'string' }, 'max-usd': { type: 'string' },
    out: { type: 'string' }, 'account-id-from': { type: 'string' }, 'platform-root': { type: 'string' },
    help: { type: 'boolean', default: false },
  } });
  if (values.help) {
    console.log(JSON.stringify({
      usage: 'node live-probe.mjs --controls PUBLIC_CONTROLS.json [--category NAME] --max-usd AMOUNT --out NEW_FILE.json [--account-id-from ACCOUNT.json] [--platform-root PATH]',
      mode: 'Explicit live inference, no retries. Uses the hash-locked shared adapter.',
      limits: '64 questions, 32000 tokens/question at $0.042/1M; cap >0 and <=0.10 USD. Not a provider billing cap.',
      credentials: 'CLOUDFLARE_ACCOUNT_ID then --account-id-from (cloudflare_account_id); CLOUDFLARE_API_TOKEN then macOS Wrangler OAuth cache with >15 minutes remaining.',
    }, null, 2));
    return 0;
  }
  const report = await runProbe({ controls: values.controls, category: values.category,
    maxUsd: Number(values['max-usd']), out: values.out, accountIdFrom: values['account-id-from'],
    platformRoot: values['platform-root'] });
  console.log(JSON.stringify(report, null, 2));
  if (!report.complete) return 2;
  return report.summary.falsePasses || report.summary.falseFailures || report.summary.reviews ? 1 : 0;
}

const entrypoint = process.argv[1] ? await realpath(process.argv[1]).catch(() => null) : null;
if (entrypoint && entrypoint === await realpath(new URL(import.meta.url))) {
  try { process.exitCode = await main(); }
  catch (error) {
    // Never print paths, provider bodies, parser exceptions or raw credential values.
    const message = error?.message === AUTH_HELP ? AUTH_HELP
      : 'Jev probe refused: check --help, public controls, dependency pin, required budget, credentials, and a new --out path. No automatic retry; details suppressed.';
    console.error(message);
    console.log(JSON.stringify({ complete: false, releaseAccepted: false, error: message }));
    process.exitCode = 2;
  }
}
