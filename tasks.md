# Detailed Implementation Tasks

## Phase 1: ENS Profile Viewer & Deployment

### 1.1 Project Structure & Django Initialization
- [ ] **Create Root Repository:** Initialize a single git repository with a `/backend` directory (no separate `/frontend` — Django serves everything).
- [ ] **Create Python Environment:** Set up a virtual environment inside `/backend` (`python -m venv venv`).
- [ ] **Install Core Dependencies:** `pip install django web3 psycopg2-binary gunicorn django-environ`.
- [ ] **Start Django Project:** Run `django-admin startproject core .` inside `/backend` and `python manage.py startapp ens`.
- [ ] **Configure Settings:** Use `django-environ` to load secrets from a `.env` file. Set `ALLOWED_HOSTS`, `STATIC_ROOT`, and database settings.
- [ ] **Create `requirements.txt`:** `pip freeze > requirements.txt`.

### 1.2 Web3 / ENS Integration (Server-Side)
- [ ] **Get RPC API Key:** Obtain a free key from Infura, Alchemy, or another provider.
- [ ] **Store Credentials Securely:** Add the RPC URL to `.env` and load it in `settings.py` via `django-environ`.
- [ ] **Create ENS Service Module:** Build a utility file (e.g., `ens/services.py`) that uses `web3.py` to:
  - Resolve an ENS name to an address.
  - Fetch all text records (avatar, description, url, twitter, github, discord).
  - Fetch coin addresses (ETH, BTC, SOL via EIP-2304 coin-type lookups).
  - Fetch metadata (resolver address, expiry/registration date, wrapped state).
- [ ] **Graceful Error Handling:** Return structured error responses for non-existent or empty records.

### 1.3 ENS Search Page (Home)
- [ ] **URL Route:** Map `/` to a view in `ens/views.py`.
- [ ] **View:** Render a simple home page template with the search form. On GET, display the empty form.
- [ ] **Template (`templates/ens/home.html`):** A centered search bar accepting `.eth` names with a Search button. Include basic client-side validation (e.g., must end in `.eth`).
- [ ] **Form Submission:** On submit, redirect the user to `/profile/<ens_name>/`.

### 1.4 ENS Profile Page
- [ ] **URL Route:** Map `/profile/<str:ens_name>/` to a profile view in `ens/views.py`.
- [ ] **View:** Call the ENS service module to fetch all data for `ens_name`. Pass the result dict as context to the profile template.
- [ ] **Template (`templates/ens/profile.html`):** Render:
  - **Header:** ENS Name, Owner Address (shortened `0x…`), Avatar (with fallback placeholder).
  - **Description & URL:** Display prominently if populated.
  - **Social Links:** Twitter, GitHub, Discord — render only if populated.
  - **Crypto Wallets:** ETH, BTC, SOL addresses in a card/list with a copy-to-clipboard button.
  - **Metadata:** Resolver address, Expiry Date (human-readable), Wrapped state.
- [ ] **Styling:** Include a base CSS file (`static/css/base.css`) for clean, responsive design. Use Google Fonts for typography.

### 1.5 Static Files & Templates Setup
- [ ] **Configure `TEMPLATES`:** Set `DIRS` to include a top-level `templates/` folder.
- [ ] **Configure `STATICFILES_DIRS`:** Point to a top-level `static/` directory for CSS/JS assets.
- [ ] **Run `collectstatic`:** Verify static files are collected correctly before deployment.

### 1.6 Initial Deployment (Phase 1 Goal)
- [ ] **Prepare for Production:** Set `DEBUG=False`, configure `ALLOWED_HOSTS`, run `collectstatic`.
- [ ] **Choose Hosting:** Deploy to Railway, Render, or Fly.io (all support Django natively without containers at this stage).
- [ ] **Set Environment Variables:** Add `.env` values (RPC URL, `SECRET_KEY`, `DEBUG=False`) to the hosting platform.
- [ ] **Deploy & Verify:** Trigger a deployment, visit the live URL, test the search, and verify the profile renders blockchain data correctly.

---

## Phase 2: Social Network Graph Visualization

### 2.1 Graph Library Setup
- [ ] **Choose Library:** Use `cytoscape.js` or `vis-network`, loaded via CDN in the template — no npm/build step needed.
- [ ] **Create Graph App:** Add a new Django app (`python manage.py startapp graph`) or extend the `ens` app with a graph view.
- [ ] **Base Graph Template (`templates/graph/graph.html`):** Renders a hardcoded static sample graph to confirm the library loads correctly.

### 2.2 Input Mechanism for Connections
- [ ] **URL Route:** Map `/graph/` to the graph view.
- [ ] **View:** Accept a `POST` form with a textarea of ENS name pairs. Parse the input into a list of unique nodes and edges; pass as JSON-serialized context to the template.
- [ ] **Template Input UI:** A textarea where users type pairs like `vitalik.eth, balajis.eth` (one pair per line or comma-separated), plus a "Visualize" button.

### 2.3 Interactive Graph Rendering
- [ ] **Bind Data to Graph:** Use an inline `<script>` block in the template to read the context-provided nodes/edges JSON and initialize the graph library.
- [ ] **Style Nodes:** Customize node appearance (color, label showing the `.eth` name, sizing).
- [ ] **Style Edges:** Customize connection lines (arrows, thickness, color).
- [ ] **Hover Interactions:** Add tooltips or highlights on node/edge hover using the library's event API.

### 2.4 Profile Navigation from Graph
- [ ] **Click Handler:** Register a node-click event via JS. When clicked, capture the node's `id` (ENS name) and `window.location.href` to `/profile/<ens_name>/`.

---

## Phase 3: Editable Graph Relationships & Persistence

### 3.1 PostgreSQL Database Integration
- [ ] **Provision Database:** Set up a local PostgreSQL instance or a cloud DB (Supabase, Neon).
- [ ] **Configure Django DB Settings:** Update `DATABASES` in `settings.py` using the `.env` credentials.
- [ ] **Apply Initial Migrations:** Run `python manage.py migrate`.

### 3.2 Define Database Schema (Models)
- [ ] **Create Edge Model:** In `graph/models.py` (or `ens/models.py`), define a `Friendship` model:
  - `source` (CharField, max_length=255) — origin ENS name.
  - `target` (CharField, max_length=255) — destination ENS name.
  - `created_at` (DateTimeField, auto_now_add=True).
  - `unique_together = ('source', 'target')` to prevent duplicates.
- [ ] **Make & Apply Migrations:** `python manage.py makemigrations` and `python manage.py migrate`.

### 3.3 Create JSON API Endpoints (Django Views)
- [ ] **Install DRF (optional):** `pip install djangorestframework` or use plain `JsonResponse` views.
- [ ] **Edges List/Create View:** `GET /api/edges/` returns all edges as JSON; `POST /api/edges/` creates a new edge.
- [ ] **Edge Delete View:** `DELETE /api/edges/<id>/` removes an edge.
- [ ] **URL Config:** Add `api/` routes to `core/urls.py`.
- [ ] **Test API:** Use `curl` or a REST client to verify CRUD operations.

### 3.4 Graph Template Integration (AJAX)
- [ ] **Fetch Initial State:** On page load, the graph template JavaScript calls `GET /api/edges/` to populate the graph instead of relying solely on the input form.
- [ ] **Add Edge UI/Logic:** Provide a UI (button or context menu) to add a connection. On submit, call `POST /api/edges/` via `fetch()` and update the graph on success.
- [ ] **Delete Edge UI/Logic:** On edge click, show a remove option. On confirm, call `DELETE /api/edges/<id>/` via `fetch()` and remove the edge from the graph.
- [ ] **CSRF Handling:** Include Django's CSRF token in AJAX headers using the `getCookie('csrftoken')` helper.

---

## Phase 4: DevOps & Infrastructure

### 4.1 Django App Dockerization
- [ ] **Create `Dockerfile`:** Use a Python base image. Install `requirements.txt`, collect static files, and start with `gunicorn`.
- [ ] **Create `.dockerignore`:** Exclude `venv/`, `__pycache__/`, `.env`, etc.

### 4.2 Orchestration
- [ ] **Create `docker-compose.yml`:** Define two services:
  - `db`: The official PostgreSQL image (with `POSTGRES_*` environment variables).
  - `web`: The Django Dockerfile (depends on `db`; mounts a volume for static files).
- [ ] **Test Full Stack Spin-up:** Run `docker-compose up --build` and verify the app is accessible on `localhost`.
