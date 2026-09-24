import test from 'node:test';
import { createHash } from 'node:crypto';
import assert from 'node:assert/strict';
import { existsSync, mkdtempSync, mkdirSync, readFileSync, writeFileSync, rmSync, symlinkSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { tmpdir } from 'node:os';
import { spawnSync } from 'node:child_process';

const moduleUrl = new URL('../skills/software-development/jev-evaluation/scripts/benchmark.mjs', import.meta.url);
const probeUrl = new URL('../skills/software-development/jev-evaluation/scripts/live-probe.mjs', import.meta.url);

const probeControls = { ...corpusForProbe() };
function corpusForProbe() {
  return { schemaVersion: 1, classification: 'public-synthetic', labelProvenance: 'Engineering controls, not calibration.', cases: [
    { id: 'saved', category: 'save-vs-execute', candidate: 'The draft is saved; it has not been sent.',
      requirements: { saved: 'States that the draft is saved.', unsent: 'States that the draft has not been sent.' },
      expected: { saved: 'pass', unsent: 'pass' } },
    { id: 'other', category: 'handoff', candidate: 'QA owns review.',
      requirements: { owner: 'Names QA as owner.' }, expected: { owner: 'pass' } },
  ] };
}

test('live probe preflights the filtered question count and required spending cap before requests', async () => {
  assert.ok(existsSync(probeUrl), 'portable bounded live probe must exist');
  const { prepareProbe } = await import(probeUrl);
  let touched = 0;
  const api = { createJevRequest(candidate, requirements) {
    touched++;
    return { input: { state: { candidate }, questions: requirements } };
  } };
  const cap = 2 * 32000 * 0.042 / 1e6;
  for (const maxUsd of [undefined, NaN, Infinity, 0, -1, 0.11, cap - 0.000001]) {
    assert.throws(() => prepareProbe(api, probeControls, { category: 'save-vs-execute', maxUsd }), /budget/);
  }
  assert.throws(() => prepareProbe(api, probeControls, { category: 'missing', maxUsd: 0.1 }), /category/);
  assert.equal(touched, 0);
  const plan = prepareProbe(api, probeControls, { category: 'save-vs-execute', maxUsd: cap });
  assert.equal(plan.questionCount, 2);
  assert.equal(plan.requestCount, 1);
  assert.equal(plan.reservedEstimateUsd, cap);
  assert.equal(plan.rows[0].payload.input.state.expected, undefined);
  assert.equal(prepareProbe(api, probeControls, { maxUsd: 0.1 }).questionCount, 3);
});

const corpus = { schemaVersion: 1, classification: 'public-synthetic', labelProvenance: 'Engineering test controls.', cases: [{
  id: 'handoff', candidate: 'Ask QA to verify the local test artifact; the release remains unverified.',
  requirements: { owner: 'Names QA as the next owner.', honesty: 'States release verification is not complete.' },
  expected: { owner: 'pass', honesty: 'pass' },
}] };

test('live probe discovers credentials without refreshing short-lived Wrangler OAuth', async () => {
  const mod = await import(probeUrl);
  assert.equal(typeof mod.discoverCredentials, 'function', 'credential preflight must exist');
  const dir = mkdtempSync(join(tmpdir(), 'jev-auth-'));
  const accountId = 'a'.repeat(32);
  const env = { CLOUDFLARE_ACCOUNT_ID: accountId, CLOUDFLARE_API_TOKEN: 'env-test-token' };
  const now = Date.parse('2026-01-01T00:00:00Z');
  const cache = join(dir, 'Library/Preferences/.wrangler/config/default.toml');
  const accountFile = join(dir, 'account.json');
  try {
    assert.deepEqual(await mod.discoverCredentials({ env, home: dir, now, accountIdFrom: '/does-not-exist' }),
      { accountId, token: 'env-test-token' });
    writeFileSync(accountFile, JSON.stringify({ cloudflare_account_id: accountId, ignored: 'not-evidence' }));
    mkdirSync(resolve(cache, '..'), { recursive: true });
    const put = expiration => writeFileSync(cache, `oauth_token = "cfoat_OFFLINE_TEST"\nexpiration_time = "${expiration}"\nrefresh_token = "cfort_OFFLINE_TEST"\n`);
    for (const expiration of ['2025-12-31T23:59:00Z', '2026-01-01T00:14:59Z', '2026-01-01T00:15:00Z', '', 'invalid']) {
      put(expiration);
      await assert.rejects(mod.discoverCredentials({ env: {}, home: dir, now, accountIdFrom: accountFile }), /wrangler login/);
    }
    put('2026-01-01T00:15:01Z');
    assert.deepEqual(await mod.discoverCredentials({ env: {}, home: dir, now, accountIdFrom: accountFile }),
      { accountId, token: 'cfoat_OFFLINE_TEST' });
    // A malformed env account is not silently replaced or normalized.
    await assert.rejects(mod.discoverCredentials({ env: { ...env, CLOUDFLARE_ACCOUNT_ID: ` ${accountId}` },
      home: dir, now, accountIdFrom: accountFile }), /account/i);
    // An env token takes precedence even when the OAuth cache has expired.
    put('2025-12-31T00:00:00Z');
    assert.deepEqual(await mod.discoverCredentials({ env: { CLOUDFLARE_API_TOKEN: 'env-test-token' },
      home: dir, now, accountIdFrom: accountFile }), { accountId, token: 'env-test-token' });
    writeFileSync(cache, 'oauth_token = "cfoat_OFFLINE_TEST"\n');
    await assert.rejects(mod.discoverCredentials({ env: { CLOUDFLARE_ACCOUNT_ID: accountId }, home: dir, now }), /wrangler login/);
  } finally { rmSync(dir, { recursive: true }); }
});

test('live probe persists candidate-free allowlisted evidence before every billable request', async () => {
  const mod = await import(probeUrl);
  assert.equal(typeof mod.runProbe, 'function', 'live probe orchestration must exist');
  const dir = mkdtempSync(join(tmpdir(), 'jev-probe-'));
  const controls = join(dir, 'controls.json');
  const out = join(dir, 'evidence.json');
  writeFileSync(controls, JSON.stringify(probeControls));
  const marker = 'SECRET_PROVIDER_METADATA';
  const env = { DUSTWAVE_PLATFORM_DIR: process.env.DUSTWAVE_PLATFORM_DIR,
    CLOUDFLARE_ACCOUNT_ID: 'a'.repeat(32), CLOUDFLARE_API_TOKEN: 'cfoat_OFFLINE_TEST' };
  const snapshots = [];
  const progress = [];
  let calls = 0;
  try {
    const report = await mod.runProbe({ controls, category: 'save-vs-execute', maxUsd: 0.01, out }, {
      env, progress: message => progress.push(message), fetchTarget: async (url, options) => {
        calls++;
        const pending = JSON.parse(readFileSync(out));
        snapshots.push(JSON.stringify(pending));
        assert.equal(pending.cases[0].status, 'pending');
        assert.equal(pending.networkAttempts, 1);
        assert.equal(pending.summary.usageComplete, false);
        assert.equal(pending.cases[0].request, undefined);
        assert.match(url, /api.cloudflare.com/);
        const payload = JSON.parse(options.body);
        assert.equal(payload.input.state.candidate, probeControls.cases[0].candidate);
        assert.equal(payload.input.state.expected, undefined);
        return new Response(JSON.stringify({ success: true, messages: [marker], result: {
          state: 'Completed', debug: marker, result: { model: 'jev-1.13.0',
            usage: { input_tokens: 100, output_tokens: 10, debug: marker },
            answers: Object.fromEntries(Object.keys(payload.input.questions).map(key => [key, {
              type: 'choice', choice: 'pass', probabilities: { pass: 0.99, fail: 0.01, uncertain: 0 }, debug: marker,
            }])) },
        } }));
      },
    });
    assert.equal(calls, 1);
    assert.equal(report.complete, true);
    assert.equal(report.releaseAccepted, false);
    assert.equal(report.summary.correct, 2);
    assert.ok(progress.length > 0);
    assert.deepEqual(JSON.parse(readFileSync(out)), report);
    snapshots.push(JSON.stringify(report));
    for (const snapshot of snapshots) {
      for (const forbidden of [marker, ...probeControls.cases.map(row => row.candidate), 'cfoat_', 'cfort_', 'Bearer ', env.CLOUDFLARE_ACCOUNT_ID]) {
        assert.equal(snapshot.includes(forbidden), false);
      }
    }
    assert.deepEqual(report.cases[0].response.usage, { input_tokens: 100, output_tokens: 10 });
    assert.deepEqual(report.cases[0].response.answers.saved.probabilities, { pass: 0.99, fail: 0.01, uncertain: 0 });
    assert.match(report.sourceControlsSha256, /^[a-f0-9]{64}$/);
    // Caller paths and source text are recoverable from fixtures, never duplicated in evidence.
    assert.equal(JSON.stringify(report).includes(controls), false);
    const before = readFileSync(out, 'utf8');
    await assert.rejects(mod.runProbe({ controls, maxUsd: 0.01, out }, { env, progress() {},
      fetchTarget: async () => { calls++; throw new Error('Must not call'); } }));
    assert.equal(calls, 1);
    assert.equal(readFileSync(out, 'utf8'), before);
  } finally { rmSync(dir, { recursive: true }); }
});

test('live probe re-parses written JSON and refuses credential-shaped strings without rejecting SHA-256', async () => {
  const mod = await import(probeUrl);
  assert.equal(typeof mod.verifyEvidence, 'function', 'post-write evidence verification must exist');
  const dir = mkdtempSync(join(tmpdir(), 'jev-scan-'));
  const out = join(dir, 'evidence.json');
  const controls = join(dir, 'controls.json');
  const env = { DUSTWAVE_PLATFORM_DIR: process.env.DUSTWAVE_PLATFORM_DIR,
    CLOUDFLARE_ACCOUNT_ID: 'a'.repeat(32), CLOUDFLARE_API_TOKEN: 'offline-test' };
  try {
    for (const marker of ['cfoat_TEST', 'cfort_TEST', 'Bearer test', 'a'.repeat(32), 'ABCDEF01'.repeat(4)]) {
      for (const value of [{ nested: [marker] }, { [marker]: 'key' }]) {
        writeFileSync(out, JSON.stringify(value));
        await assert.rejects(mod.verifyEvidence(out), /credential/i);
      }
    }
    writeFileSync(out, '{"model":"\\u0063foat_TEST"}');
    await assert.rejects(mod.verifyEvidence(out), /credential/i, 'scan decoded strings too');
    writeFileSync(out, 'progress\n{}');
    await assert.rejects(mod.verifyEvidence(out), /JSON/);
    const safe = { sha256: 'a'.repeat(64), model: 'jev-1.13.0' };
    writeFileSync(out, JSON.stringify(safe));
    assert.deepEqual(await mod.verifyEvidence(out), safe);
    rmSync(out);
    writeFileSync(controls, JSON.stringify(probeControls));
    let calls = 0;
    await assert.rejects(mod.runProbe({ controls, maxUsd: 0.01, out }, { env, progress() {},
      fetchTarget: async (_url, options) => {
        calls++;
        return new Response(JSON.stringify({ model: 'cfoat_TEST', usage: { input_tokens: 1, output_tokens: 0 },
          answers: Object.fromEntries(Object.keys(JSON.parse(options.body).input.questions).map(key => [key, {
            type: 'choice', choice: 'pass', probabilities: { pass: 1, fail: 0, uncertain: 0 },
          }])) }));
      } }), /credential/i);
    assert.equal(calls, 1, 'unsafe response stops the batch, never retries');
    const pending = await mod.verifyEvidence(out);
    assert.equal(pending.cases[0].status, 'pending', 'last safe checkpoint survives unsafe response');
    assert.equal(pending.complete, false);
  } finally { rmSync(dir, { recursive: true }); }
});

test('live probe CLI keeps stdout JSON-only on success, mismatch, expiry and refusal', () => {
  const dir = mkdtempSync(join(tmpdir(), 'jev-probe-cli-'));
  const controls = join(dir, 'controls.json');
  const out = join(dir, 'evidence.json');
  const transport = join(dir, 'offline-transport.mjs');
  const cache = join(dir, 'Library/Preferences/.wrangler/config/default.toml');
  writeFileSync(controls, JSON.stringify(probeControls));
  // Replace only external transport; exercise the real CLI, locked parser and filesystem.
  writeFileSync(transport, `globalThis.fetch = async (_url, options) => {
    if (process.env.TEST_JEV_MODE === 'error') throw new Error('cfoat_MUST_NOT_LEAK');
    const choice = process.env.TEST_JEV_MODE === 'fail' ? 'fail' : 'pass';
    return new Response(JSON.stringify({ model: 'jev-1.13.0', usage: { input_tokens: 1, output_tokens: 0 },
      answers: Object.fromEntries(Object.keys(JSON.parse(options.body).input.questions).map(key => [key, {
        type: 'choice', choice, probabilities: { pass: choice === 'pass' ? 1 : 0, fail: choice === 'fail' ? 1 : 0, uncertain: 0 },
      }])) }));
  };`);
  const env = { ...process.env, HOME: dir, CLOUDFLARE_ACCOUNT_ID: 'a'.repeat(32), CLOUDFLARE_API_TOKEN: 'offline-only' };
  const command = (args, overrides = {}) => spawnSync(process.execPath,
    ['--import', transport, decodeURIComponent(probeUrl.pathname), ...args],
    { env: { ...env, ...overrides }, encoding: 'utf8' });
  const args = ['--controls', controls, '--category', 'save-vs-execute', '--max-usd', '0.01', '--out', out];
  try {
    const result = command(args);
    assert.equal(result.status, 0, result.stderr);
    assert.ok(result.stdout.trim().startsWith('{'), 'stdout must contain JSON, not silence or progress');
    assert.deepEqual(JSON.parse(result.stdout), JSON.parse(readFileSync(out)));
    assert.equal(JSON.parse(result.stdout).summary.correct, 2);
    assert.match(result.stderr, /Jev probe:/);
    const before = readFileSync(out, 'utf8');
    for (const args of [[], ['--unknown'], ['--controls', controls, '--out', out],
      ['--controls', controls, '--out', out, '--max-usd', '0.00001'],
      ['--controls', controls, '--out', out, '--max-usd', 'NaN']]) {
      const refused = command(args);
      assert.equal(refused.status, 2);
      assert.equal(JSON.parse(refused.stdout).complete, false);
    }
    assert.equal(command(args).status, 2, 'refuse overwrite');
    assert.equal(readFileSync(out, 'utf8'), before);
    rmSync(out);
    const mismatch = command(args, { TEST_JEV_MODE: 'fail' });
    assert.equal(mismatch.status, 1);
    assert.equal(JSON.parse(mismatch.stdout).summary.falseFailures, 2);
    rmSync(out);
    const unavailable = command(args, { TEST_JEV_MODE: 'error' });
    assert.equal(unavailable.status, 2);
    assert.equal(JSON.parse(unavailable.stdout).networkAttempts, 1);
    assert.equal((unavailable.stdout + unavailable.stderr).includes('cfoat_'), false);
    rmSync(out);
    mkdirSync(resolve(cache, '..'), { recursive: true });
    writeFileSync(cache, 'oauth_token = "cfoat_TEST"\nexpiration_time = "2000-01-01T00:00:00Z"\n');
    const expired = command(args, { CLOUDFLARE_API_TOKEN: '' });
    assert.equal(expired.status, 2);
    assert.equal(JSON.parse(expired.stdout).complete, false);
    assert.match(expired.stderr, /wrangler login/);
    assert.equal(existsSync(out), false, 'expiry refuses before evidence or transport');
    assert.ok(JSON.parse(command(['--help']).stdout).usage);
  } finally { rmSync(dir, { recursive: true }); }
});

test('live probe refuses oversized controls before credentials and blocks transport on checkpoint failure', async () => {
  const { runProbe } = await import(probeUrl);
  const dir = mkdtempSync(join(tmpdir(), 'jev-probe-stop-'));
  const controls = join(dir, 'controls.json');
  const out = join(dir, 'evidence.json');
  const env = { DUSTWAVE_PLATFORM_DIR: process.env.DUSTWAVE_PLATFORM_DIR,
    CLOUDFLARE_ACCOUNT_ID: 'a'.repeat(32), CLOUDFLARE_API_TOKEN: 'offline-only' };
  let calls = 0;
  let credentialReads = 0;
  try {
    const oversized = structuredClone(probeControls);
    oversized.cases[1].candidate = 'x'.repeat(32000);
    writeFileSync(controls, JSON.stringify(oversized));
    await assert.rejects(runProbe({ controls, maxUsd: 0.01, out }, {
      env: new Proxy(env, { get(target, key) {
        if (String(key).startsWith('CLOUDFLARE_')) credentialReads++;
        return target[key];
      } }), progress() {}, fetchTarget: async () => { calls++; },
    }), /32000 bytes/);
    assert.equal(credentialReads, 0);
    assert.equal(calls, 0);
    assert.equal(existsSync(out), false);
    writeFileSync(controls, JSON.stringify(probeControls));
    let checkpoints = 0;
    await assert.rejects(runProbe({ controls, maxUsd: 0.01, out }, { env,
      progress() {
        if (++checkpoints === 1) { rmSync(out); mkdirSync(out); }
      }, fetchTarget: async () => { calls++; },
    }));
    assert.equal(calls, 0, 'a failed pending checkpoint must prevent billable transport');
  } finally { rmSync(dir, { recursive: true }); }
});

test('offline lesson demonstrates the predicted naïve false passes, not fabricated model evidence', () => {
  const reference = new URL('../skills/software-development/jev-evaluation/references/offline-controls.md', import.meta.url);
  assert.ok(existsSync(reference), 'controlled offline probe reference must exist');
  const source = readFileSync(reference, 'utf8').match(/```js\n([\s\S]*?)\n```/)[1];
  const run = code => spawnSync(process.execPath, ['--input-type=module', '--eval', code], { encoding: 'utf8' });
  const demonstration = run(source);
  assert.equal(demonstration.status, 0, demonstration.stderr);
  assert.deepEqual(JSON.parse(demonstration.stdout), {
    kind: 'simulated-controls-not-live-inference',
    faithful: { correct: 4, falsePasses: 0, falseFailures: 0 },
    naive: { correct: 2, falsePasses: 2, falseFailures: 0 },
  });
  assert.equal(run(source.replace('predictedFalsePasses = 2', 'predictedFalsePasses = 1')).status, 1,
    'a wrong predeclared false-pass prediction must fail, never be silently accepted');
});

test('live probe CLI runs through a symlink instead of silently exiting', () => {
  const dir = mkdtempSync(join(tmpdir(), 'jev-probe-link-'));
  try {
    const entry = join(dir, 'probe.mjs');
    symlinkSync(decodeURIComponent(probeUrl.pathname), entry);
    const result = spawnSync(process.execPath, [entry, '--help'], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    assert.ok(result.stdout.trim().startsWith('{'), 'symlink invocation must emit a JSON document');
    assert.ok(JSON.parse(result.stdout).usage.includes('--controls'));
    assert.equal(result.stderr, '');
  } finally { rmSync(dir, { recursive: true }); }
});

test('live probe checks OAuth against the clock at credential validation, not batch start', async t => {
  const { runProbe } = await import(probeUrl);
  const dir = mkdtempSync(join(tmpdir(), 'jev-probe-clock-'));
  const controls = join(dir, 'controls.json');
  const out = join(dir, 'evidence.json');
  const cache = join(dir, 'Library/Preferences/.wrangler/config/default.toml');
  let now = Date.parse('2026-01-01T00:00:00Z');
  let calls = 0;
  t.mock.method(Date, 'now', () => now);
  try {
    writeFileSync(controls, JSON.stringify(probeControls));
    mkdirSync(resolve(cache, '..'), { recursive: true });
    writeFileSync(cache, 'oauth_token = "cfoat_OFFLINE"\nexpiration_time = "2026-01-01T00:15:01Z"\n');
    const env = new Proxy({ DUSTWAVE_PLATFORM_DIR: process.env.DUSTWAVE_PLATFORM_DIR,
      CLOUDFLARE_ACCOUNT_ID: 'a'.repeat(32) }, { get(target, key) {
      if (key === 'DUSTWAVE_PLATFORM_DIR') now += 10000; // Slow controls/dependency preflight.
      return target[key];
    } });
    await assert.rejects(runProbe({ controls, maxUsd: 0.01, out }, { env, home: dir, progress() {},
      fetchTarget: async () => { calls++; throw new Error('Must not reach transport'); },
    }), /wrangler login/);
    assert.equal(calls, 0);
    assert.equal(existsSync(out), false);
  } finally { rmSync(dir, { recursive: true }); }
});

test('live probe rejects free-form model text while retaining review for unknown Jev versions', async () => {
  const { runProbe, verifyEvidence } = await import(probeUrl);
  const dir = mkdtempSync(join(tmpdir(), 'jev-probe-model-'));
  const controls = join(dir, 'controls.json');
  const env = { DUSTWAVE_PLATFORM_DIR: process.env.DUSTWAVE_PLATFORM_DIR,
    CLOUDFLARE_ACCOUNT_ID: 'a'.repeat(32), CLOUDFLARE_API_TOKEN: 'offline-only' };
  try {
    writeFileSync(controls, JSON.stringify(probeControls));
    const probe = (model, out) => runProbe({ controls, category: 'save-vs-execute', maxUsd: 0.01, out }, {
      env, progress() {}, fetchTarget: async (_url, options) => new Response(JSON.stringify({ model,
        usage: { input_tokens: 10, output_tokens: 1 },
        answers: Object.fromEntries(Object.keys(JSON.parse(options.body).input.questions).map(key => [key, {
          type: 'choice', choice: 'pass', probabilities: { pass: 1, fail: 0, uncertain: 0 },
        }])),
      })),
    });
    for (const [index, model] of [probeControls.cases[0].candidate, 'debug blob\nwith text', 'hello', 'x'.repeat(129)].entries()) {
      const out = join(dir, `refused-${index}.json`);
      await assert.rejects(probe(model, out), /model identifier/);
      const pending = await verifyEvidence(out);
      assert.equal(pending.cases[0].status, 'pending');
      assert.equal(JSON.stringify(pending).includes(model), false);
    }
    const report = await probe('jev-99.0.0', join(dir, 'unknown-version.json'));
    assert.equal(report.complete, true);
    assert.equal(report.summary.reviews, 2);
    assert.equal(report.summary.correct, 0);
    assert.equal(report.cases[0].response.model, 'jev-99.0.0');
  } finally { rmSync(dir, { recursive: true }); }
});

test('live probe module can be imported from a stdin runner', () => {
  const result = spawnSync(process.execPath, ['--input-type=module', '-'], {
    input: `const probe = await import(${JSON.stringify(probeUrl.href)}); console.log(typeof probe.runProbe);`,
    encoding: 'utf8',
  });
  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stdout.trim(), 'function');
});

test('preflight refuses a batch beyond its question or spending budget before using an adapter', async () => {
  assert.ok(existsSync(moduleUrl), 'portable Jev benchmark module must exist');
  const { prepare } = await import(moduleUrl);
  const corpus = { schemaVersion: 1, classification: 'public-synthetic', cases: [{
    id: 'one', candidate: 'A bounded synthetic handoff.',
    requirements: { owner: 'Names the next owner.' }, expected: { owner: 'fail' },
  }] };
  let touched = 0;
  const api = { createJevRequest() { touched++; } };
  assert.throws(() => prepare(api, corpus, { repeats: 3, maxQuestions: 2 }), /question budget/);
  assert.throws(() => prepare(api, corpus, { maxEstimatedUsd: 0.00001 }), /spending budget/);
  assert.equal(touched, 0);
});

test('dry run groups questions sharing state, with no provider call or acceptance', async () => {
  const mod = await import(moduleUrl);
  assert.equal(typeof mod.evaluate, 'function', 'offline evaluation must exist');
  const api = { createJevRequest(candidate, requirements) {
    return { input: { state: { candidate }, questions: requirements } };
  } };
  const plan = mod.prepare(api, corpus);
  const split = mod.prepare(api, corpus, { splitQuestions: true });
  assert.equal(plan.requestCount, 1);
  assert.equal(split.requestCount, 2);
  assert.equal(plan.questionCount, split.questionCount);
  const report = await mod.evaluate(api, plan);
  assert.equal(report.networkAttempts, 0);
  assert.equal(report.complete, false);
  assert.equal(report.releaseAccepted, false);
  assert.equal(report.summary.unevaluated, 2);
  assert.equal(report.summary.correct, 0);
  assert.equal(report.classification, 'public-synthetic');
  assert.equal(report.labelProvenance, 'Engineering test controls.');
  assert.equal(report.cases[0].request.input.state.expected, undefined);
});

test('evaluation accounts for reviews, errors, repeat flips and token usage without retries', async () => {
  const { prepare, evaluate } = await import(moduleUrl);
  // Contract doubles exercise orchestration; real shared parser is tested separately.
  const api = {
    createJevRequest(candidate, requirements) { return { input: { state: { candidate }, questions: requirements } }; },
    judgeJevResponse(raw) { return raw; },
  };
  let calls = 0;
  const report = await evaluate(api, prepare(api, corpus, { repeats: 3 }), { call: async () => {
    calls++;
    if (calls === 3) throw new Error('SECRET must not be persisted');
    return { model: 'jev-1.13.0', usage: { input_tokens: 100, output_tokens: 10 }, findings: {
      owner: { decision: calls === 1 ? 'pass' : 'fail' }, honesty: { decision: 'review' },
    } };
  } });
  assert.equal(calls, 3);
  assert.equal(report.complete, false);
  assert.equal(report.networkAttempts, 3);
  assert.equal(report.summary.correct, 1);
  assert.equal(report.summary.falseFailures, 1);
  assert.equal(report.summary.reviews, 2);
  assert.equal(report.summary.unevaluated, 2);
  assert.equal(report.summary.decisionFlips, 1);
  assert.equal(report.summary.inputTokens, 200);
  assert.equal(report.summary.usageComplete, false);
  assert.ok(report.cases[2].elapsedMs >= 0);
  assert.equal(JSON.stringify(report).includes('SECRET'), false);
});

test('shared adapter loads only hash-locked files and exercises real response validation', async () => {
  const mod = await import(moduleUrl);
  assert.equal(typeof mod.loadPlatform, 'function', 'hash-verified shared adapter loader required');
  assert.ok(process.env.DUSTWAVE_PLATFORM_DIR, 'Set DUSTWAVE_PLATFORM_DIR for offline integration tests');
  const api = await mod.loadPlatform(process.env.DUSTWAVE_PLATFORM_DIR);
  const request = api.createJevRequest('QA owns review.', { owner: 'Names QA.' });
  const raw = { model: 'jev-1.13.0', usage: { input_tokens: 10, output_tokens: 2 }, answers: {
    owner: { type: 'choice', choice: 'pass', probabilities: { pass: 0.99, fail: 0.01, uncertain: 0 } },
  } };
  assert.equal(api.judgeJevResponse(raw, request.input.questions, mod.POLICY).findings.owner.decision, 'pass');
  assert.equal(api.judgeJevResponse({ ...raw, model: 'unknown-model' }, request.input.questions, mod.POLICY).findings.owner.decision, 'review');
  assert.throws(() => api.judgeJevResponse({ ...raw, answers: {} }, request.input.questions, mod.POLICY));
  const dir = mkdtempSync(join(tmpdir(), 'jev-tamper-'));
  try {
    mkdirSync(join(dir, 'packages/test-core'), { recursive: true });
    writeFileSync(join(dir, 'packages/test-core/package.json'), '{}');
    await assert.rejects(mod.loadPlatform(dir), /pin mismatch/);
  } finally { rmSync(dir, { recursive: true }); }
});

test('pending attempt is durable before transport and persistence failure prevents the call', async () => {
  const { loadPlatform, prepare, evaluate } = await import(moduleUrl);
  const api = await loadPlatform(process.env.DUSTWAVE_PLATFORM_DIR);
  const plan = prepare(api, corpus);
  let persisted;
  let inFlight;
  let calls = 0;
  const report = await evaluate(api, plan, {
    onProgress: async value => { persisted = JSON.parse(JSON.stringify(value)); },
    call: async () => {
      calls++;
      inFlight = persisted;
      throw new Error('Simulated provider failure');
    },
  });
  assert.equal(calls, 1);
  assert.equal(inFlight.networkAttempts, 1);
  assert.equal(inFlight.cases[0].status, 'pending');
  assert.equal(inFlight.cases[0].requestSha256, plan.rows[0].requestSha256);
  assert.equal(inFlight.summary.usageComplete, false);
  assert.equal(report.cases[0].status, 'unavailable');
  assert.ok(persisted.cases[0].elapsedMs >= 0);
  assert.equal(report.summary.unevaluated, 2);
  // Failure to persist intent must abort before invoking billable transport.
  calls = 0;
  await assert.rejects(evaluate(api, plan, {
    onProgress: async value => {
      if (value.networkAttempts) throw new Error('Disk unavailable');
    },
    call: async () => { calls++; throw new Error('Must not be called'); },
  }), /Disk unavailable/);
  assert.equal(calls, 0);
});

test('successful response evidence excludes provider envelope and debug metadata', async () => {
  const { loadPlatform, prepare, evaluate } = await import(moduleUrl);
  const api = await loadPlatform(process.env.DUSTWAVE_PLATFORM_DIR);
  const marker = 'SECRET_PROVIDER_METADATA';
  const answers = Object.fromEntries(Object.keys(corpus.cases[0].requirements).map(key => [key, {
    type: 'choice', choice: 'pass', probabilities: { pass: 0.99, fail: 0.01, uncertain: 0 }, debug: marker,
  }]));
  const snapshots = [];
  const report = await evaluate(api, prepare(api, corpus), {
    call: async () => ({ success: true, messages: [marker], result: {
      state: 'Completed', debug: marker, result: {
        model: 'jev-1.13.0', usage: { input_tokens: 100, output_tokens: 10, debug: marker }, answers,
      },
    } }),
    onProgress: async value => snapshots.push(JSON.stringify(value)),
  });
  assert.equal(report.complete, true);
  assert.equal(snapshots.join().includes(marker), false);
  assert.equal(report.cases[0].raw, undefined);
  assert.deepEqual(report.cases[0].result.usage, { input_tokens: 100, output_tokens: 10 });
  assert.equal(api.judgeJevResponse(report.cases[0].response, report.cases[0].request.input.questions,
    report.policy).findings.owner.decision, 'pass', 'sanitized evidence retains replayable full distributions');
});

test('locked dependency refuses a symlink outside its selected checkout', async () => {
  const { loadPlatform } = await import(moduleUrl);
  const dir = mkdtempSync(join(tmpdir(), 'jev-symlink-'));
  try {
    mkdirSync(join(dir, 'packages/test-core'), { recursive: true });
    symlinkSync(resolve(process.env.DUSTWAVE_PLATFORM_DIR, 'packages/test-core/package.json'),
      join(dir, 'packages/test-core/package.json'));
    await assert.rejects(loadPlatform(dir), /pin mismatch/);
  } finally { rmSync(dir, { recursive: true }); }
});

test('shared transport emits an abort deadline and never retries', async () => {
  const { loadPlatform } = await import(moduleUrl);
  const api = await loadPlatform(process.env.DUSTWAVE_PLATFORM_DIR);
  let aborted = false;
  let attempts = 0;
  await assert.rejects(api.callCloudflareJev(api.createJevRequest('QA owns review.', { owner: 'Names QA.' }), {
    accountId: '0'.repeat(32), token: 'offline-test-only', timeoutMs: 5,
    fetchTarget: async (_url, { signal }) => {
      attempts++;
      return new Promise((_resolve, reject) => {
        const guard = setTimeout(() => reject(new Error('Deadline not emitted')), 1000);
        signal.addEventListener('abort', () => {
          aborted = true;
          clearTimeout(guard);
          reject(signal.reason);
        }, { once: true });
      });
    },
  }), /Jev request failed/);
  assert.equal(aborted, true);
  assert.equal(attempts, 1);
});

test('published pilot observations replay against frozen cases and recompute all summary metrics', async () => {
  const { loadPlatform, prepare, summarize } = await import(moduleUrl);
  const api = await loadPlatform(process.env.DUSTWAVE_PLATFORM_DIR);
  const builtIn = JSON.parse(readFileSync(new URL('../skills/software-development/jev-evaluation/references/cases.json', import.meta.url)));
  const observations = JSON.parse(readFileSync(new URL('../docs/jev/2026-09-23-observations.json', import.meta.url)));
  const archive = JSON.parse(readFileSync(new URL('../docs/jev/2026-09-23-pilot-runner.json', import.meta.url))).source;
  assert.equal(observations.labelProvenance, builtIn.labelProvenance);
  for (const run of Object.values(observations.runs)) {
    const plan = prepare(api, builtIn, { repeats: run.repeats, splitQuestions: run.splitQuestions });
    assert.equal(createHash('sha256').update(archive).digest('hex'), run.runnerSha256);
    assert.equal(plan.corpusSha256, run.corpusSha256);
    assert.equal(plan.policySha256, run.policySha256);
    assert.equal(plan.requestCount, run.cases.length);
    const cases = run.cases.map((row, index) => {
      const planned = plan.rows[index];
      assert.equal(row.id, planned.id);
      assert.equal(row.requestSha256, planned.requestSha256);
      assert.deepEqual(row.expected, planned.expected);
      const result = api.judgeJevResponse(row.response, planned.payload.input.questions, run.policy);
      return { ...row, result };
    });
    assert.deepEqual(summarize({ ...run, cases }), run.summary);
  }
});

test('CLI defaults to no network, refuses overwrite and budget excess, and never reads credentials in preview', () => {
  const dir = mkdtempSync(join(tmpdir(), 'jev-cli-'));
  const out = join(dir, 'preview');
  const env = { ...process.env, CLOUDFLARE_ACCOUNT_ID: '', CLOUDFLARE_API_TOKEN: '' };
  // URL pathname must be decoded for the iCloud path containing spaces.
  const command = extra => spawnSync(process.execPath, [decodeURIComponent(moduleUrl.pathname), '--out', out, ...extra], { env, encoding: 'utf8' });
  try {
    const preview = command([]);
    assert.equal(preview.status, 0, preview.stderr);
    assert.ok(existsSync(join(out, 'report.json')), 'CLI must write the real preview artifact');
    const report = JSON.parse(readFileSync(join(out, 'report.json')));
    assert.equal(report.networkAttempts, 0);
    assert.equal(report.complete, false);
    assert.equal(report.questionCount, 16);
    assert.equal(report.requestCount, 8);
    assert.equal(command([]).status, 2, 'existing output must not be overwritten');
    const before = readFileSync(join(out, 'report.json'), 'utf8');
    assert.equal(command(['--max-questions', '1']).status, 2);
    assert.equal(readFileSync(join(out, 'report.json'), 'utf8'), before);
    assert.equal(command(['--live']).status, 2);
    assert.equal(command(['--unknown']).status, 2);
  } finally { rmSync(dir, { recursive: true }); }
});
