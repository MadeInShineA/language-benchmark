# language-benchmark

Solving the same LeetCode problems in several languages, to compare the languages.

Solutions are written by hand. The `lc` tool only handles the repetitive parts:
fetching problems, creating stubs and running the tests.

Languages: **Python**, **Rust**, **Go**, **TypeScript (bun)**. C is planned.

## Setup

Toolchains come from the Nix flake (`direnv allow`, or `nix develop`).

## The `lc` tool

`lc` lives in `tools/lc/`. It only uses Python's standard library, so there's nothing to install.
Run it from the repo root:

```sh
python3 tools/lc daily               # fetch today's daily problem, create stubs in every language
python3 tools/lc new two-sum         # fetch any problem by slug or URL
python3 tools/lc test 462            # check every solution against the examples
python3 tools/lc test 462 -l rust go # only some languages
python3 tools/lc list                # problems and which languages have a solution file
python3 tools/lc sync                # create missing stubs, regenerate glue code
```

`test` takes a problem number, slug or id. With none, it uses the most recently fetched problem.

### Typical workflow

1. `python3 tools/lc daily`
2. Read `problems/<id>/README.md` and solve it in each language (files below)
3. `python3 tools/lc test` until everything passes

## Layout

```
problems/<id>/            one folder per problem, e.g. p0462_minimum_moves_to_equal_array_elements_ii
  README.md               problem statement
  problem.json            metadata from LeetCode (signature, snippets)
  cases.json              examples with expected outputs (you can add your own)

python/solutions/<id>.py          ← your solutions
rust/src/problems/<id>.rs         ←
go/problems/<id>/solution.go      ←
js/problems/<id>.ts               ←

python/runner.py, rust/src/main.rs,
go/cmd/runner/, js/runner.ts      runners: load a solution and run it on the cases

tools/lc/                 the lc tool
go/personal/              other experiments, unrelated to the benchmark
```

Files marked *generated, do not edit* (`rust/src/registry.rs`, `rust/src/problems/mod.rs`,
`go/registry/registry_gen.go`, `go/problems/*/adapter_gen.go`) are rewritten on every `lc` run.

New stubs start with a placeholder body (`todo!()`, `panic("TODO")`, ...) so everything
compiles before you've solved the problem.

## How testing works

Each language has a runner that follows the same contract:

```
runner <problem_dir> <cases.json> <iters> <warmup>
→ {"cases": [{"ns": <median ns>, "result": <return value>}, ...]}
```

`lc test` runs every runner once per case and compares `result` with `expected` in `cases.json`.
Rust is built with `--release`.

## Limitations

- Not supported yet: `ListNode`/`TreeNode` problems and "design" problems (classes with
  several methods). `lc` warns when it fetches one.
- No C runner yet: LeetCode's C signatures use raw pointers and output-size arguments.
- Premium-only problems can't be fetched.
