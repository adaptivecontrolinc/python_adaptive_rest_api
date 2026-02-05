# Adaptive API Python Client

A Python client library for interacting with Adaptive Live and PE APIs.

## Features

- **Live API**: Monitor machines, fetch tag values, control machine operations
- **PE API**: Access job history, program groups, schedules and production data
- **Type Safety**: Full dataclass models with type hints
- **Easy Integration**: Simple, intuitive API design

## Installation

```bash
pip install adaptive-api-python
```

## Quick Start

```python
from adaptive_api import ApiLive, ApiPe

# Initialize clients
live_client = ApiLive("http://your-server", "your-api-token")
pe_client = ApiPe("http://your-server", "your-api-token")

# Get machine list
machines = live_client.machines()
for machine in machines:
    print(f"Machine: {machine.machine}, Type: {machine.type}")

# Get job history
history = pe_client.history("job-id", tags=["01.TargetTemp", "01.State"])
```

## API Reference

### Live API

- `machines()` - Get list of available machines
- `tag_values(machine, tags)` - Fetch tag values for a machine
- `dashboard_entries()` - Get dashboard entries
- `run(machine)` - Start/run a machine
- `pause(machine)` - Pause a machine

### PE API

- `history(job_id, tags)` - Get job execution history
- `jobs_and_stoppages(after, before)` - Get jobs and stoppages in time range
- `program_group_names()` - Get available program groups
- `search(query, limit)` - Search for items

### Setup

```bash
git clone <repo-url>
cd adaptive-api-python
pip install -e ".[dev]"
```

## License

See LICENSE file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.