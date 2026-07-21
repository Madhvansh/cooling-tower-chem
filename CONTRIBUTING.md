# Contributing to cooling-tower-chem

Thanks for your interest! This is a small, focused library and contributions are
welcome — especially additional well-referenced indices and worked examples.

## Development setup

```bash
git clone https://github.com/Madhvansh/cooling-tower-chem
cd cooling-tower-chem
python -m pip install -e ".[dev]"
pytest
ruff check .
```

The package uses a `src/` layout; install it in editable mode (as above) so
`import cooling_tower_chem` resolves during testing.

## Guidelines

- **Keep it dependency-free.** The core library uses only the Python standard
  library. Please don't add runtime dependencies without discussion.
- **Cite your formula.** New indices should include a reference (paper, standard,
  or textbook) in the docstring, and at least one test that pins a value derived
  from that source.
- **Validate inputs.** Reject non-physical inputs (e.g. non-positive hardness)
  with a clear `ValueError` rather than returning a silent fallback.
- **Type hints + docstrings** on every public function, with units stated
  explicitly.
- Run `ruff check .` and `pytest` before opening a PR.

## Test policy

Major new functionality must ship with tests. Any new index, formula, or
public function should include unit tests that pin expected values (ideally
against a cited source), and bug fixes should add a regression test. Please run
both `pytest` and `ruff check .` locally and make sure they pass before opening
a pull request — CI runs the same checks, and PRs are expected to be green.

## Good first issues

- Contribute additional worked examples from the literature to strengthen the
  test suite (see `tests/test_literature.py` for the pattern).
- Further unit-conversion helpers (e.g. more ion equivalents, pressure units).

By contributing you agree that your contributions are licensed under the MIT
License of this project.
