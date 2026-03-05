# Detailed Implementation Tasks

## Phase 1: ENS Profile Viewer & Deployment

### 1.1 Project Structure & Frontend Initialization
- [ ] **Create Root Repository:** Initialize a single git repository containing two primary directories: `/frontend` and `/backend`. 
- [ ] **Create React App:** Navigate into `/frontend` and initialize a new React application (Next.js or Vite recommended).
- [ ] **Clean Up Boilerplate:** Remove unused CSS, logos, and default test files from the frontend.
- [ ] **Configure Styling:** Set up tailwindcss or standard CSS depending on project preference. Ensure modern, responsive design principles.
- [ ] **Install Core Dependencies:** Add necessary packages like `react-router-dom` (if not Next.js), UI component libraries (e.g., shadcn/ui or MUI) for quick styling, and HTTP clients like `axios`.

### 1.2 Web3 Integration
- [ ] **Install Web3 Library:** Add `viem` or `ethers.js` to the project.
- [ ] **Configure RPC Provider:** 
  - Get a free API key from Infura, Alchemy, or another provider.
  - Set up environment variables (`.env.local`) to store the RPC URL securely.
- [ ] **Create Web3 Service:** Build a utility file (e.g., `src/services/ensService.js`) to encapsulate blockchain calls (fetching profile data, resolving names).

### 1.3 ENS Search Component
- [ ] **Build UI Component:** Create a centered search bar accepting `.eth` names. Include a clear "Search" button.
- [ ] **State Management:** Manage the input value and loading states (e.g., "Searching...", "Found", "Error").
- [ ] **Input Validation:** Implement basic regex/validation to ensure the input format loosely matches ENS standards before making API calls.
- [ ] **Routing:** On successful search or enter key press, redirect the user to `/profile/<ens-input>`.

### 1.4 Profile UI Component
- [ ] **Dynamic Routing:** Set up the route `/profile/:ensName` to capture the domain from the URL.
- [ ] **Data Fetching:** On component mount, use the Web3 service to fetch the ENS data. Ensure graceful error handling if the domain doesn't exist or has no records.
- [ ] **Render Core Details:** Create a header section displaying the `ENS Name` (e.g., vitalik.eth), `Owner Address` (shortened `0x...`), and `Avatar` (fallback to a blockie or default image if missing).
- [ ] **Render Description & URL:** Display the `Description` and `Web URL` prominently if they exist.
- [ ] **Render Social Links:** Create a section (perhaps with icons) for `Twitter`, `GitHub`, and `Discord`. Only render the icons/links for fields that are populated.
- [ ] **Render Crypto Wallets:** Display addresses for `ETH`, `BTC`, `SOL` in a card or list format with a quick "copy-to-clipboard" button.
- [ ] **Render Metadata:** Display technical details like `Resolver address`, `Expiry Date` (formatted human-readable), and `Wrapped state`.

### 1.5 Initial Deployment (Phase 1 Goal)
- [ ] **Prepare for Production:** Run the build script (`npm run build`) to ensure there are no compilation errors or missing dependencies.
- [ ] **Configure Hosting Service:** Connect the GitHub repository to a service like Vercel, Netlify, or Render.
- [ ] **Set Environment Variables:** Ensure the RPC Provider URL/API Keys are added to the hosting platform's environment variables.
- [ ] **Deploy & Verify:** Trigger a deployment, visit the live URL, test the search functionality, and verify the profile renders correctly with data from the blockchain.

---

## Phase 2: Social Network Graph Visualization

### 2.1 Graph Library Selection & Setup
- [ ] **Install Library:** Add a graphing library like `react-force-graph` (recommended for node/edge data structures).
- [ ] **Create Base Component:** Create a new page or component (e.g., `/graph`) that renders a hardcoded, static sample graph to ensure the library works.

### 2.2 Input Mechanism for Connections
- [ ] **Build Input UI:** Design a component to accept a list or CSV of ENS name pairs (e.g., a text area where users type `vitalik.eth, balajis.eth`).
- [ ] **Data Parsing logic:** Write a function to parse the user input string into a structured JSON array of nodes (unique ENS names) and links (source to target).
- [ ] **State Management:** Store the parsed nodes and links in the component's state or a global store.

### 2.3 Interactive Graph Rendering
- [ ] **Bind Data to Graph:** Pass the parsed nodes and links state into the graph visualization library.
- [ ] **Style Nodes:** Customize node appearance (e.g., sizing, colors, labels showing the `.eth` name).
- [ ] **Style Edges:** Customize connection lines (e.g., arrows for direction, thickness, color).
- [ ] **Hover Interactions:** Add tooltips or highlights when hovering over nodes or edges.

### 2.4 Profile Navigation from Graph
- [ ] **Implement Click Handler:** Add an `onNodeClick` event listener to the graph nodes.
- [ ] **Routing:** When a node is clicked, capture its `id` (the ENS name) and use the router to navigate dynamically to the profile page built in Phase 1 (`/profile/:ensName`).

---

## Phase 3: Editable Graph Relationships & Persistence

### 3.1 Django Backend Initialization
- [ ] **Navigate to Backend Directory:** Move into the `/backend` folder.
- [ ] **Create Python Environment:** Set up a virtual environment (e.g., `python -m venv venv`).
- [ ] **Install Django:** `pip install django djangorestframework psycopg2-binary django-cors-headers`.
- [ ] **Start Project:** Run `django-admin startproject core .` (using the dot to initialize in the current `/backend` folder) and `python manage.py startapp api`.
- [ ] **Configure Settings:** Add the new app, `rest_framework`, and `corsheaders` to `INSTALLED_APPS`. Configure CORS to allow requests from the React frontend port.

### 3.2 PostgreSQL Database Integration
- [ ] **Provision Database:** Set up a local PostgreSQL instance or a cloud database (Supabase, Neon).
- [ ] **Configure Django DB Settings:** Update the `DATABASES` dictionary in `settings.py` with the Postgres credentials.
- [ ] **Apply Initial Migrations:** Run `python manage.py migrate` to set up Django's default tables.

### 3.3 Define Database Schema (Models)
- [ ] **Create Edge Model:** In `api/models.py`, define an `Edge` or `Friendship` model with:
  - `source` (CharField, max_length=255) - The origin ENS name.
  - `target` (CharField, max_length=255) - The destination ENS name.
  - `created_at` (DateTimeField auto_now_add).
- [ ] **Add Constraints:** Add a `unique_together` constraint on `('source', 'target')` to prevent duplicate friendships.
- [ ] **Make Migrations:** Run `python manage.py makemigrations api` and `python manage.py migrate`.

### 3.4 Create REST API Endpoints
- [ ] **Create Serializers:** In `api/serializers.py`, create an `EdgeSerializer`.
- [ ] **Create Views:** In `api/views.py`, set up an API view or ViewSet to handle GET (list all edges), POST (add an edge), and DELETE (remove an edge).
- [ ] **Define URLs:** In `api/urls.py`, route the views to endpoints (e.g., `/api/edges/`).
- [ ] **Test API:** Use Postman or curl to verify records can be added, viewed, and deleted.

### 3.5 Frontend Integration (Read & Write)
- [ ] **Fetch Initial State:** Modify the Phase 2 graph component to perform a `GET` request to the Django API on mount, populating the initial graph data instead of relying solely on manual text input.
- [ ] **Add Edge UI/Logic:** Provide a UI (button or contextual menu) on the graph to add a connection. On submit, make a `POST` request to the backend and update the local graph state on success.
- [ ] **Delete Edge UI/Logic:** Allow users to click an existing edge to trigger a removal option. On confirm, make a `DELETE` request to the backend and remove the edge from the local graph state.

---

## Phase 4: DevOps & Infrastructure

### 4.1 Backend Dockerization
- [ ] **Create Backend Dockerfile:** Write a `Dockerfile` for the Django app (use a python base image, install requirements.txt, run migrations, and start gunicorn/runserver).
- [ ] **Create requirements.txt:** `pip freeze > requirements.txt`.

### 4.2 Frontend Dockerization 
- [ ] **Create Frontend Dockerfile:** Write a `Dockerfile` for the React app (use a Node base image, install dependencies, run the build command, and serve via Nginx or a lightweight server).

### 4.3 Orchestration
- [ ] **Create docker-compose.yml:** Define three services:
  - `db`: The PostgreSQL image (with environment variables for user/password/db).
  - `backend`: The Django Dockerfile (depends on `db`).
  - `frontend`: The React Dockerfile (depends on `backend`).
- [ ] **Test Full Stack Spin-up:** Run `docker-compose up --build` and ensure all three containers communicate correctly and the app is accessible on `localhost`.
