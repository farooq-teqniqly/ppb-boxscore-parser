# gamebox-parser (table-driven event parser)

Minimal, table-driven baseball event parser.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -U pip pytest
pip install -e .
pytest
```

## Usage
```python
from gamebox import classify_event

ev = classify_event("G6-3")
print(ev.field_path)  # [6, 3]

ev = classify_event("1B+ROE(5)", advances_str="B-1;B-2(E5)")
print(ev.advances)    # [('B','1',None), ('B','2','E5')]
```
