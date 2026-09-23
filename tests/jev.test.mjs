import test from 'node:test';
import { createHash } from 'node:crypto';
import assert from 'node:assert/strict';
import { existsSync, mkdtempSync, mkdirSync, readFileSync, writeFileSync, rmSync, symlinkSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { tmpdir } from 'node:os';
import { spawnSync } from 'node:child_process';

const moduleUrl = new URL('../skills/software-development/jev-evaluation/scripts/benchmark.mjs', import.meta.url);

const corpus = { schemaVersion: 1, classification: 'public-synthetic', labelProvenance: 'Engineering test controls.', cases: [{
  id: 'handoff', candidate: 'Ask QA to verify the local test artifact; the release remains unverified.',
  requirements: { owner: 'Names QA as the next owner.', honesty: 'States release verification is not complete.' },
  expected: { owner: 'pass', honesty: 'pass' },
}] };

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
