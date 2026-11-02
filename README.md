# jobtrack

A small, dependency-free command-line tool to keep track of your job
applications — the company, the role, where it stands, and your notes —
all stored locally in a SQLite database.

Built as a personal project. No frameworks, just Python's standard library.

## Install

```bash
git clone <your-repo-url>
cd jobtrack
pip install -e .
```

Or run it without installing:

```bash
python -m jobtrack --help
```

## Usage

```bash
# Add an application (status defaults to "applied", date defaults to today)
jobtrack add "Ingenics Digital" "C++ / Qt Developer" --location "Gräfelfing" --salary "72000"

# List everything, newest first
jobtrack list

# Only show the ones where you're interviewing
jobtrack list --status interview

# See one application in full
jobtrack show 3

# Move an application along its lifecycle
jobtrack status 3 interview

# Remove one
jobtrack delete 3
```

Statuses: `applied`, `interview`, `offer`, `rejected`, `withdrawn`.

By default the database lives at `~/.jobtrack/jobtrack.db`. Point it elsewhere
with `--db /path/to/file.db`.

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Roadmap

These are intentionally not built yet — they are the next things to work on:

- [ ] `stats` command: counts per status, response rate, applications per week
- [ ] `export` command: write all applications to CSV and JSON
- [ ] `search` / free-text filter across company, position and notes
- [ ] `edit` command: update any field, not just status
- [ ] Follow-up reminders: flag applications with no update after N days
- [ ] Colored terminal output and nicer table formatting
- [ ] `import` from a CSV file
- [ ] Config file for defaults (default location, currency, date format)

## License

MIT — see [LICENSE](LICENSE).
