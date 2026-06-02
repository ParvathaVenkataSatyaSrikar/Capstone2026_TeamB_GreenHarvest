# GreenHarvest tests

Run from the project root:

```powershell
python tests/test_llm_providers.py
python tests/test_rag.py
python tests/test_vision.py
python scripts/test_apis.py
```

## Fixtures

- `fixtures/queries.txt` — sample farmer questions
- `fixtures/images/` — place crop photos here (`sample_leaf.jpg` auto-generated)

Generate sample image:

```powershell
python tests/fixtures/generate_sample_image.py
```
