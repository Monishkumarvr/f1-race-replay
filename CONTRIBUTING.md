# Contributing to F1 Race Replay

Thank you for your interest in contributing to F1 Race Replay! This document provides guidelines and instructions for contributing.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/f1-race-replay.git
   cd f1-race-replay
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e ".[dev]"  # Install dev dependencies
   ```

4. **Install pre-commit hooks** (recommended)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

### Running the Application

```bash
# Launch GUI (default)
python main.py

# Launch CLI
python main.py --cli

# View a specific race
python main.py --viewer --year 2024 --round 5

# List available rounds
python main.py --list-rounds --year 2024

# See all options
python main.py --help
```

## Development Workflow

### Before Making Changes

1. Create a new branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make sure all tests pass:
   ```bash
   python -m pytest tests/ -v
   ```

### Making Changes

1. Write your code following the existing style
2. Add tests for new functionality
3. Update documentation if needed
4. Run the linter:
   ```bash
   ruff check src/ tests/
   ```

### Submitting Changes

1. **Run all tests**:
   ```bash
   python -m pytest tests/ -v
   ```

2. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Brief description of changes"
   ```

3. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a Pull Request** on GitHub

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Use type hints where appropriate
- Keep functions focused and small

### Logging

Use the `logging` module instead of `print()` for debug output:

```python
import logging
logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.debug("Detailed debug info")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
```

## Testing

- Tests are located in the `tests/` directory
- Use pytest for running tests
- Name test files `test_*.py`
- Name test functions `test_*`

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_time.py -v

# Run with coverage
python -m pytest tests/ --cov=src
```

## Project Structure

```
f1-race-replay/
├── main.py              # Application entry point
├── src/
│   ├── f1_data.py       # Data loading and processing
│   ├── arcade_replay.py # Race visualization
│   ├── lib/             # Utility modules
│   │   ├── time.py      # Time formatting utilities
│   │   └── tyres.py     # Tyre compound utilities
│   ├── cli/             # CLI interface
│   ├── gui/             # GUI interface
│   └── interfaces/      # Session interfaces
├── tests/               # Test suite
├── .github/             # GitHub templates and workflows
└── pyproject.toml       # Project configuration
```

## Areas for Contribution

### Good First Issues
- Adding unit tests for existing functions
- Improving documentation
- Fixing typos or small bugs

### Feature Ideas
- Additional telemetry visualizations
- New session types (practice sessions)
- UI/UX improvements
- Performance optimizations

## Questions?

Feel free to open an issue if you have questions or need help getting started!
