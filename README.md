Country Currency & Exchange API
This project provides a backend service that fetches country and currency data from public APIs, computes estimated GDPs using an adjustable random multiplier, caches results in a database, and exposes CRUD & utility endpoints.

Why I built this
Short paragraph about the learning goals: external API integration, DB caching, image generation, robust error handling and building production-ready endpoints.


Create and activate a virtualenv
python -m venv venv && .\venv\Scripts\activate (Windows)

Install deps
pip install -r requirements.txt

Create .env (see sample lines)

Run server
uvicorn main:app --reload

Visit http://127.0.0.1:8000/docs to explore Swagger UI.

Endpoints

Describe /countries/refresh, /countries, /countries/{name}, /status, /countries/image with sample responses (short).

Deployment (Railway)

Add DATABASE_URL (MySQL) in Railway environment variables.

Add COUNTRIES_API_URL, EXCHANGE_API_URL, RANDOM_MIN, RANDOM_MAX, SUMMARY_IMAGE_PATH.

Push and deploy; Railway will use Procfile.

Testing

Include how to run tests/test_hng.ps1 or bash tests.sh.

Notes & Limitations

Estimates are rough; random multiplier used for demonstration.

If external APIs fail, endpoint returns 503 Service Unavailable and does not change DB.

License / Author
11) Deployment checklist (Railway)

Ensure requirements.txt and Procfile present.

Add repository to Railway (New Project → Deploy from GitHub).

Add env vars on Railway (DATABASE_URL, COUNTRIES_API_URL, EXCHANGE_API_URL, RANDOM_MIN, RANDOM_MAX, SUMMARY_IMAGE_PATH).

Railway uses port $PORT; Procfile uses $PORT automatically for uvicorn.

Deploy — check logs. If 503 after hitting /countries/refresh, inspect logs for network error.

12) Quick troubleshooting & gotchas

.env loading: load_dotenv() must be executed before modules that call os.getenv(). Doing it at the top of main.py is safest.

Different restcountries versions: v2 returns currencies as list-of-objects; v3 returns dicts — code above tries to handle both shapes.

Database URI: Use sqlite:///./countries.db for local dev; in Railway, supply MySQL URI mysql+pymysql://user:pass@host:3306/db.

Timeouts: Use reasonable timeouts for external calls; fail gracefully with 503 and do not modify DB on failure.

Image fonts: Windows might not have 'arial.ttf' path accessible; fallback to default font is included.

Testing remote deployment: Test from multiple networks if Railway cannot reach external APIs due to private networking rules.

Unique constraint: Country name is unique — use case-insensitive matching .ilike() when updating.