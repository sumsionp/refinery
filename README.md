# Refinery

A local-first troubleshooting intelligence tool designed to transform noisy support logs into refined, searchable knowledge.

## Quick Start

### 1. Initialize Workspace
Run the initialization script to set up the directory structure and security protections:
```bash
python3 refinery_init.py
```

### 2. Gather: Import a Support Archive
Import a raw archive (e.g., `.tar.gz`, `.zip`) and associate it with a Case ID. This will unpack the files into `data/raw/` and register them in the database.
```bash
export PYTHONPATH=$PYTHONPATH:.
python3 src/main.py gather CASE-12345 path/to/logs.tar.gz
```

### 3. Review: Scrub and Filter
Open a file in the TUI to review content, scrub PII, and mark proprietary terms.
```bash
python3 src/main.py review CASE-12345 messages.txt
```
**TUI Controls:**
- `h/j/k/l`: Navigate (vi-style)
- `v`: Toggle visual selection mode
- `y`: Yank selection (add to case proprietary terms)
- `a`: Manually add a proprietary term
- `q`: Quit

### 4. Manage Cases & Tiered Storage
List case statuses and manage raw data retention.
```bash
# Show status of all cases
python3 src/main.py cases --status

# Set active cases (others will be marked for 30-day deletion)
python3 src/main.py cases --active CASE-12345 CASE-67890

# Cleanup expired data
python3 src/main.py cases --cleanup

# Cleanup all inactive cases immediately
python3 src/main.py cases --cleanup --immediate
```

## Funnel Stages
1. **Gather**: Import raw supportconfigs/logs.
2. **Review**: Identify clues and scrub PII/proprietary data via the Manual Gate.
3. **Sort**: Filter clues into actionable evidence (In Development).
4. **Refine**: Create technical internal resolutions (In Development).
5. **Publish**: Generate public-ready Markdown KBs (In Development).

## Development & Testing
To run the test suite:
```bash
export PYTHONPATH=$PYTHONPATH:.
python3 -m unittest discover tests
```

## Security
Refinery is built with privacy first. Raw data in `data/raw/` is strictly ignored by Git. Processed data is stored with salted hashes to ensure PII remains anonymous while maintaining technical consistency for pattern matching.
