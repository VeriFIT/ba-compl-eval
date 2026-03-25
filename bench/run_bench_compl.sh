#!/bin/bash

show_help() {
	echo "Usage:"
	echo "run_bench.sh [options] [BENCHMARK1 BENCHMARK2 ...]"
	echo ""
	echo "Runs the given tool on the specified benchmarks. For omega-automata"
	echo "complementation we treat benchmarks as explicit suites (no grouping)."
	echo "If no benchmark is given, the default suites are:"
	echo "  advanced-automata, s1s-direct-red, from_ltl_red"
	echo ""
	echo "Options:"
	echo "  -h        Show this help message"
	echo "  -t TOOL   Which tool to run (default=kofola)"
	echo "  -j N      How many processes to run in parallel (default=4)"
	echo "  -m N      Memory limit of each process in GB (default=8)"
	echo "  -s N      Timeout for each process in seconds (default=120)"
	echo "  --tela    Run tela evaluation: tools kofola-tela-inductive, kofola-tela-inductive-check,"
	echo "            kofola-tela-inductive-shb, kofola-tela-inductive-shb-check on benchmarks"
	echo "            ltl_tela and ltl_tela_elevator"
	echo "  --tela-bench  Run tela evaluation with tela tools on the given benchmark(s)"
	echo "Note: positional arguments are treated as benchmark names and are not"
	echo "expanded into groups. Provide multiple benchmark names to run them all."
}

# For omega automata complementation we do not use grouped benchmarks.
# Distinguish the three benchmark suites explicitly; do not group benchmarks.
# If no benchmark is given, run the three omega-complementation benchmark sets.

tool="kofola"
j_value="4"
m_value="8"
s_value="120"
tela_mode=false
tela_bench_mode=false

tela_tools=("kofola-tela-inductive" "kofola-tela-inductive-check" "kofola-tela-inductive-shb" "kofola-tela-inductive-shb-check" "kofola-tela-inductive-for" "kofola-tela-inductive-for-check")
tela_default_benchmarks=("ltl_tela" "ltl_tela_elevator")

# Run all tela tools on the given benchmarks (passed as arguments).
run_tela_tools() {
  local benchmarks=("$@")
  local tasks_files=()
  local CUR_DATE
  CUR_DATE=$(date +%Y-%m-%d-%H-%M)
  for tela_tool in "${tela_tools[@]}"; do
    for benchmark in "${benchmarks[@]}"; do
      echo "Running benchmark $benchmark with tool $tela_tool"
      local FILE_PREFIX="$benchmark-to${s_value}-$tela_tool-$CUR_DATE"
      local TASKS_FILE="$FILE_PREFIX.tasks"
      cat "inputs/compl/$benchmark.input" | ./pycobench -c omega-compl.yaml -j $j_value -t $s_value --memout $m_value -m "$tela_tool" -o "$TASKS_FILE"
      tasks_files+=("$TASKS_FILE")
      echo "$TASKS_FILE" >> tasks_names.txt
    done
  done
  for tasks_file in "${tasks_files[@]}"; do
    echo "$tasks_file"
  done
}

# Pre-process long options
args=()
for arg in "$@"; do
  case "$arg" in
    --tela)
      tela_mode=true
      ;;
    --tela-bench)
      tela_bench_mode=true
      ;;
    *)
      args+=("$arg")
      ;;
  esac
done
set -- "${args[@]}"

while getopts "ht:j:m:s:" option; do
    case $option in
        h)
            show_help 
            exit 0
            ;;
        t)
            tool=$OPTARG
            ;;
        j)
            j_value=$OPTARG
            ;;
        m)
            m_value=$OPTARG
            ;;
        s)
            s_value=$OPTARG
            ;;
        *)
            echo "Invalid option: -$OPTARG"
            show_help
            exit 1
            ;;
    esac
done

# Shift the option index so that $1 refers to the first positional argument
shift $((OPTIND - 1))

benchmarks=()

# If --tela is set, run tela tools on the default tela benchmarks
if [ "$tela_mode" = true ]; then
  run_tela_tools "${tela_default_benchmarks[@]}"
  exit 0
fi

# If --tela-bench is set, run tela tools on the benchmark(s) given via positional arguments
if [ "$tela_bench_mode" = true ]; then
  if [ -z "$1" ]; then
    echo "Error: --tela-bench requires at least one benchmark argument."
    show_help
    exit 1
  fi
  run_tela_tools "$@"
  exit 0
fi

# If no benchmark is given, run the three omega automata complementation sets
if [ -z "$1" ]; then
  benchmarks=("advanced_automata_termination" "autohyper" "pecan" "s1s" "state_of_buchi" "seminator" "ldba4ltl")
else
  # treat each positional argument as a benchmark name (no grouping)
  for BENCH_NAME in "$@"; do
    benchmarks+=("$BENCH_NAME")
  done
fi

tasks_files=()

CUR_DATE=$(date +%Y-%m-%d-%H-%M)
for benchmark in "${benchmarks[@]}"; do
	echo "Running benchmark $benchmark"
	FILE_PREFIX="$benchmark-to${s_value}-$tool-$CUR_DATE"
	TASKS_FILE="$FILE_PREFIX.tasks"
	cat "inputs/compl/$benchmark.input" | ./pycobench -c omega-compl.yaml -j $j_value -t $s_value --memout $m_value -m "$tool" -o "$TASKS_FILE"
	tasks_files+=("$TASKS_FILE")
	echo "$TASKS_FILE" >> tasks_names.txt
done

for tasks_file in "${tasks_files[@]}"; do
	echo "$tasks_file"
done