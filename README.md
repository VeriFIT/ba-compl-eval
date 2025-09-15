# Büchi Automata Complementation & Inclusion Evaluation Environment

This repository provides an environment to benchmark and analyse tools for:
1. Omega-automata (Büchi) complementation
2. Omega-automata language inclusion (A ⊆ B)

Both workflows share infrastructure (wrappers, `pycobench`, result post‑processing) but differ in:
- Bench scripts (`run_bench_compl.sh` vs `run_bench_incl.sh`)
- YAML tool configs (`omega-compl.yaml` vs `omega-incl.yaml`)
- Result columns (`<tool>-states` for complementation, `<tool>-result` for inclusion)
- Input lists (`inputs/compl/*.input` vs `inputs/incl/*.input`)

---
## 1. Python Dependencies
```
pip3 install -r requirements.txt
```

---
## 2. External Tools (Optional / As Needed)
Comment out entries in the relevant YAML (`bench/omega-compl.yaml` or `bench/omega-incl.yaml`) to disable a tool variant.

Assume the repository lives at `${HOME}/ba-compl-eval`.

### 2.1 GOAL

Download [GOAL](http://goal.im.ntu.edu.tw/wiki/doku.php#download) and move the file into the `bin/` directory.  Then

```
cd bin/
unzip GOAL-xxxxxxxx.zip
mv GOAL-xxxxxxxx/ goal/
```

macOS (App bundle installation):
After installing GOAL, copy the GOAL directory:
```
cp -r /Applications/GOAL.app/Contents/Resources/Java bin/goal
```

#### Fribourg Construction Plugin

A GOAL plugin implementing the Fribourg construction needs to be downloaded separetely.

```
cd bin/
wget 'https://frico.s3.amazonaws.com/goal_plugins/ch.unifr.goal.complement.zip'
unzip ch.unifr.goal.complement.zip
cd ch.unifr.goal.complement
zip -r ch.unifr.goal.complement.zip classes plugin.xml
cp ch.unifr.goal.complement.zip <GOAL_LOCATION>/plugins
```

### 2.2 Spot

We compile Spot and copy the file `autfilt` and the required libraries into the `bin/` directory

```
cd bin/
wget http://www.lrde.epita.fr/dload/spot/spot-2.9.3.tar.gz
tar xzf spot-2.9.3.tar.gz
cd spot-2.9.3/
./configure
make
cp bin/.libs/autfilt ../
cp spot/.libs/libspot.so.0 ../
cp buddy/src/.libs/libbddx.so.0 ../
export LD_LIBRARY_PATH=$HOME/ba-compl-eval/bin        # or the correct path
```

macOS note: you may need a Homebrew Bison (`brew install bison`) and set `$BISON`.

### 2.3 Seminator 2 (depends on Spot)

```
cd bin/
wget https://github.com/mklokocka/seminator/releases/download/v2.0/seminator-2.0.tar.gz
tar xzvf seminator-2.0.tar.gz
cd seminator-2.0/

SPOT="${HOME}/ba-compl-eval/bin/spot-2.9.3"   # or the path to sources of Spot
./configure CXXFLAGS="-I${SPOT} -I${SPOT}/buddy/src" LDFLAGS="-L${SPOT}/spot/.libs -L${SPOT}/buddy/src/.libs"
make
cp .libs/seminator ../
cp src/.libs/libseminator.so.0 ../
```

### 2.4 ROLL

```
wget 'https://github.com/ISCAS-PMC/roll-library/archive/dev.tar.gz' -O roll.tar.gz
tar xzvf roll.tar.gz
cd roll-library-dev/
./build.sh
cp ROLL.jar ../
```

### 2.5 Ranker (Inclusion related)

```
wget 'https://github.com/vhavlena/ba-inclusion/archive/master.tar.gz' -O ranker.tar.gz
tar xzvf ranker.tar.gz
cd ba-inclusion-master/src/
make
cp ranker ranker-tight ranker-composition ../../
```

---
## 3. Environment Variables
```
export LD_LIBRARY_PATH=$HOME/ba-compl-eval/bin   # adjust to your path
export GOALEXE=$HOME/ba-compl-eval/bin/goal/gc   # if GOAL used
```

---
## 4. Benchmarks & Inputs
Input lists (one HOA path per line):
- Complementation: `inputs/compl/*.input`
- Inclusion:       `inputs/incl/*.input` (pairs consumed internally by wrappers / pycobench)

Bench script default benchmark sets:
- Complementation (`bench/run_bench_compl.sh`): `advanced_automata_termination autohyper pecan s1s state_of_buchi seminator ldba4ltl`
- Inclusion (`bench/run_bench_incl.sh`): `autohyper rabit termination`

You can pass explicit benchmark names as positional arguments. No grouping/expansion is performed.

---
## 5. Running Benchmarks (Server Side)

### 5.1 Complementation
Script: `bench/run_bench_compl.sh`
```
./bench/run_bench_compl.sh -t kofola -s 120 -j 4 -m 8 advanced_automata_termination
```
Options:
- `-t TOOL` (matches key in `omega-compl.yaml`, default `kofola`)
- `-j N` parallel processes (default 4)
- `-m GB` memory limit per process (default 8)
- `-s SEC` timeout per task (default 120)

### 5.2 Inclusion
Script: `bench/run_bench_incl.sh`
```
./bench/run_bench_incl.sh -t kofola_fast_early autohyper rabit
```
Options identical; default tool is `kofola_fast`.

### 5.3 Output Files
For each benchmark a `.tasks` file is created in `bench/`:
```
<benchmark>-to<timeout>-<tool>-YYYY-MM-DD-hh-mm.tasks
```
All names are appended to `bench/tasks_names.txt`.

Column semantics inside `.tasks` differ:
- Complementation: per automaton states of produced complement (-> `<tool>-states` later)
- Inclusion: result status (`true|false|TO|ERR`) for pair A,B (-> `<tool>-result` later)

---
## 6. Tool Configuration YAML
Edit or comment entries:
- `bench/omega-compl.yaml` – complementation tool variants (e.g. `kofola-subs-tup`, `spot-red`, `kofola-tacas23`).
- `bench/omega-incl.yaml`  – inclusion tool variants (e.g. `kofola_fast_early_plus`, `spot`).

Keys become the `-t` TOOL argument (hyphens vs underscores must match exactly what you use later in analysis; keep consistent).

---
## 7. Retrieving & Normalising Results (Client Side)

From `eval/` use the helper scripts (edit HOST/PORT/PATH first):

### 7.1 Complementation
```
cd eval
./get_task_compl.sh <benchmark-toTIMEOUT-TOOL-DATE.tasks>
```
Processing steps:
1. Secure copy from server into `eval/compl/<benchmark>/`.
2. Detect tool version from first `;version-states` line (if present) and rename file to inject `-<version>` after tool name.
3. Commit the file (`git add` + commit message `<tool>[-<version>] on <benchmark>`).

### 7.2 Inclusion
```
cd eval
./get_task_incl.sh <benchmark-toTIMEOUT-TOOL-DATE.tasks>
```
Similar, but extracts version from a `;version-result` line and writes into `eval/incl/<benchmark>/`.

Result naming after version normalisation (example):
```
autohyper-to120-kofola_fast-1.2.3-2025-09-15-12-30.tasks
```

---
## 8. Analysis (Jupyter Notebooks)

### 8.1 Complementation Notebook
`eval/eval_compl.ipynb` uses:
```
from eval_functions import load_benches
df = load_benches(benches, tools, timeout=120)
```
DataFrame columns: `benchmark`, `name`, and per tool: `<tool>-states`, `<tool>-runtime` (+ optional `<tool>-check`). Timeouts have state `TO` and runtime coerced to timeout value.

### 8.2 Inclusion Notebook
`eval/eval_incl.ipynb` uses:
```
from eval_functions import load_benches_incl
df = load_benches_incl(benches, tools, timeout=120)
```
Columns: `benchmark`, `name`, per tool `<tool>-result` (values `true|false|TO|ERR|MISSING`) and `<tool>-runtime` (float seconds). Missing result columns are auto‑filled with `TO`.

### 8.3 Plot / Utility Functions
Found in `eval/eval_functions.py`:
- `scatter_plot` (runtime vs runtime)
- `scatter_plot_states` (states vs states; complementation only)
- `cactus_plot`, `get_solved`, `get_timeouts`, `get_errors`, etc.

### 8.4 Classification Metadata
Place classification CSVs in `eval/classifications/` named:
```
<benchmark>-classification.csv
```
Use helpers: `parse_classification`, `join_with_classification` to merge property info.

---
## 9. Quick End‑to‑End Example (Complementation)
Server:
```
./bench/run_bench_compl.sh -t kofola advanced_automata_termination
```
Client:
```
cd eval
./get_task_compl.sh advanced_automata_termination-to120-kofola-<DATE>.tasks
python3 -c "from eval_functions import load_benches;print(load_benches(['advanced_automata_termination'], ['kofola']))"
```

## 10. Quick End‑to‑End Example (Inclusion)
Server:
```
./bench/run_bench_incl.sh -t kofola_fast autohyper
```
Client:
```
cd eval
./get_task_incl.sh autohyper-to120-kofola_fast-<DATE>.tasks
python3 -c "from eval_functions import load_benches_incl;print(load_benches_incl(['autohyper'], ['kofola_fast']))"
```

---
## 11. Troubleshooting
| Symptom | Cause | Fix |
|---------|-------|-----|
| Missing `<tool>-states` or `<tool>-result` column | Tool produced only timeouts | Column auto-filled; verify tool wrapper path |
| `ImportError: libspot.so.0` | LD_LIBRARY_PATH not set | Export path to `bin/` before running notebooks |
| No version injected into filename | No `;version-states` / `;version-result` line | Accept plain tool name or update wrapper to emit version |
| Long runtimes show as exactly timeout | Non-numeric replaced | Expected behaviour for TO / ERR |

---
## 12. Conventions Summary
- Tasks filename: `<benchmark>-to<timeout>-<tool>-<timestamp>.tasks`
- Complementation result columns: `<tool>-states`, `<tool>-runtime`
- Inclusion result columns: `<tool>-result`, `<tool>-runtime`
- Timeout handling: runtime coerced to timeout, non-numeric marker retained in states/result column.

---
## 13. License / Citation
If you use this infrastructure in academic work, please cite the corresponding tool / benchmark sources (add your project-specific citation info here).
