## Backend Setup with uv

This project uses [uv](https://github.com/astral-sh/uv) for Python environment and dependency management.

### Prerequisites
- Python 3.8+
- [uv](https://github.com/astral-sh/uv) installed globally (see below)

### 1. Install uv
You can install `uv` using pipx or pip:

```bash
# Using pipx (recommended)
pipx install uv

# Or using pip
pip install --user uv
```

### 2. Install Dependencies

```bash
uv sync
```

To add packages
```bash
uv add <package name>
```

### 4. Run the Application

```bash
uv run fastapi dev main.py
```
