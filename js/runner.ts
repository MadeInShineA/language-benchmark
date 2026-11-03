// TypeScript runner (bun). Usage: bun run runner.ts <problem_dir> <cases.json> <iters> <warmup>
// See tools/lc/langs.py for the contract. Prints {"cases": [{"ns", "result"}]}.
//
// Your solutions live in problems/<id>.ts and export the LeetCode function by name.

// @ts-nocheck: uses bun/node globals without pulling in their type packages
import { readFileSync } from "node:fs";
import { basename, join } from "node:path";

const [problemDir, casesFile, itersArg, warmupArg] = process.argv.slice(2);
const iters = Number(itersArg);
const warmup = Number(warmupArg);
const id = basename(problemDir);

const meta = JSON.parse(readFileSync(join(problemDir, "problem.json"), "utf8")).meta;
const names: string[] = meta.params.map((p: { name: string }) => p.name);
const voidIndex = meta.return.type === "void" ? (meta.output?.paramindex ?? 0) : null;

const mod = await import(join(import.meta.dir, "problems", `${id}.ts`));
const fn = mod[meta.name];
if (typeof fn !== "function") {
  console.error(`problems/${id}.ts must export ${meta.name}`);
  process.exit(1);
}

const cases = JSON.parse(readFileSync(casesFile, "utf8"));
const out = [];
for (const c of cases) {
  const args0 = names.map((n) => c.input[n]);
  const times: number[] = [];
  let result: unknown;
  let args: unknown[] = [];
  for (let i = 0; i < warmup + iters; i++) {
    args = structuredClone(args0); // fresh copy, not timed
    const t0 = Bun.nanoseconds();
    result = fn(...args);
    const dt = Bun.nanoseconds() - t0;
    if (i >= warmup) times.push(dt);
  }
  if (voidIndex !== null) result = args[voidIndex];
  times.sort((a, b) => a - b);
  out.push({ ns: times[times.length >> 1], result });
}
console.log(JSON.stringify({ cases: out }));
