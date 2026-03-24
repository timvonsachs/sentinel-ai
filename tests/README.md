# Sentinel AI Tests

## Run all tests
```bash
cd /Users/elpatron/Sentinel/sentinel-ai
python3 -m pytest tests/ -v
```

## Run by category
```bash
python3 -m pytest tests/unit/ -v
python3 -m pytest tests/integration/ -v
python3 -m pytest tests/scenarios/ -v
```

## Run specific test
```bash
python3 -m pytest tests/scenarios/test_silent_drift.py -v
```

## Run with coverage
```bash
python3 -m pip install pytest-cov
python3 -m pytest tests/ --cov=sentinel --cov-report=term-missing
```

## The Most Important Test

`tests/scenarios/test_silent_drift.py::TestSilentDrift::test_detects_drift_before_traditional_threshold`

This is THE test. If Sentinel detects silent drift BEFORE traditional threshold monitoring,
the product thesis is validated.
