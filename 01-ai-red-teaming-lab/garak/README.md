# Garak integration

This adapter sends Garak probe prompts to the Northwind chatbot's `/chat` endpoint and preserves
the target model, session, run, and attack identifiers in each Garak `Message.notes` value.

## Pinned invocation

Install the reviewed scanner version before running it:

```bash
python -m pip install 'garak==0.15.1'
bash garak/run_garak.sh --list-probes
bash garak/run_garak.sh
```

The default bounded run selects `promptinject,encoding`. Override the target, probes, or output
directory explicitly when needed:

```bash
TARGET_URL=http://127.0.0.1:8000 \
GARAK_PROBES=promptinject,encoding \
RESULTS_DIR=results/garak \
bash garak/run_garak.sh
```

The command writes Garak reports and hit logs below `results/garak/`, which are intentionally
ignored because they contain run-specific evidence. Broad probe expansion is opt-in through
`GARAK_PROBES`; CI should keep the default bounded selection.

The exact pinned command and tool version are recorded in `run-manifest.json`.

Reference: [NVIDIA Garak](https://github.com/NVIDIA/garak).
