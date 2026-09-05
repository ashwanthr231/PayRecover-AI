# PayRecover AI

PayRecover AI is a FastAPI + ML payment-failure diagnosis and recovery simulation dashboard.

## Fixed in this version

- Fixed the **Analyze Payment** frontend failure: `frontend/script.js` contained an accidental leading `javascript` token, which stopped the entire JavaScript file before the form submit handler could be registered.
- Made the frontend API endpoint configurable with `window.PAYRECOVER_API_URL`.
- Added complete failure-code options in the UI so they match the trained ML models.
- Added backend input validation for amount, attempt number, payment method, failure code, and IDs.
- Added a clear `409 Conflict` response when a duplicate Payment ID is submitted instead of returning an opaque server error.
- Made SQLite database location independent of the terminal's current working directory.
- Made the recovery simulator explicitly handle deferred recovery, customer action, method change, escalation, and manual review.
- Normalized `requirements.txt` to UTF-8 so it can be consumed reliably by pip.
- Existing ML models, training data, dashboard, and database are retained.

## Project structure

```text
PayRecover-AI/
├── backend/
│   ├── agents/
│   │   ├── diagnosis_agent.py
│   │   └── recovery_agent.py
│   ├── engine/
│   │   ├── policy_engine.py
│   │   └── safety_gate.py
│   ├── ml/
│   │   ├── diagnosis_model.pkl
│   │   ├── recovery_model.pkl
│   │   ├── train_model.py
│   │   └── train_recovery_model.py
│   ├── simulator/
│   │   └── recovery_simulator.py
│   ├── database.py
│   ├── main.py
│   └── models.py
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
├── payrecover.db
├── requirements.txt
└── README.md
```

## Run

From the project root:

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the backend:

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Then serve the `frontend` directory with a local HTTP server, for example in a second terminal:

```bash
cd frontend
python -m http.server 5500
```

Open:

```text
http://127.0.0.1:5500
```

## Analyze Payment flow

The dashboard sends a payment to `POST /payments`.

The backend executes:

1. ML failure diagnosis
2. Recovery-probability prediction
3. Policy evaluation
4. Safety-gate verification
5. Recovery-strategy selection
6. Recovery simulation
7. Database persistence
8. Full result returned to the dashboard

The project is a **simulation**; it does not connect to a real bank, UPI, card network, or payment gateway.

## Important

The bundled `.pkl` models were trained with the scikit-learn version specified in `requirements.txt`. Install the project requirements before running the application.
