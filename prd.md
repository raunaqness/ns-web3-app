# Product Requirements Document (PRD)

## Project Overview
A web application to visualize and manage an Ethereum Name Service (ENS) social network. The platform allows users to view ENS profiles, visualize social connections between ENS domains via an interactive graph, and manually edit these network relationships. The entire application — both frontend (HTML/CSS/JS templates) and backend — is served by a single Django application.

## 1. Features

### Phase 1: ENS Profile Viewer (Primary Goal)
- **Search Functionality**: A search bar to input any ENS name (e.g., `vitalik.eth`).
- **Blockchain Data Retrieval**: Read and display all populated fields and text records associated with the ENS name from the Ethereum blockchain. Based on the provided API response schema, the profile should include the following fields if they exist:
  - **Core details**: ENS Name, Owner address, Avatar, Description, Web URL.
  - **Social Links**: Twitter, GitHub, Discord.
  - **Crypto Wallets**: ETH, BTC, SOL.
  - **Metadata**: Resolver address, Expiry Date, and Wrapped state.
- **Public URL**: A live, deployed version of this step must be immediately accessible.

### Phase 2: Social Network Graph Visualization
- **Input Collection**: Ability to take a list of ENS name pairs (representing connections, e.g., `vitalik.eth, balajis.eth`).
- **Interactive Visualization**: Create an in-browser graph displaying these nodes and their connections using a JavaScript graph library embedded in a Django template.
- **Profile Navigation**: Every node on the graph must be clickable and dynamically route the user to the corresponding ENS profile page created in Phase 1.

### Phase 3: Editable Graph Relationships
- **Modify Edges**: Browser interface capabilities to add new friend relationships (edges) or delete existing ones directly from the visualization.
- **State Persistence**: Store all edits and friend relationships reliably in a PostgreSQL database via Django models.

## 2. Technical Specifications

### Technology Stack
- **Full-Stack Framework**: Python (Django) — serves HTML templates, handles routing, business logic, and REST API endpoints.
- **Frontend**: Django Templates (HTML/CSS/Vanilla JS) — no separate frontend framework or build step.
- **Database**: PostgreSQL (for Phase 3 relationships).
- **Blockchain Interaction**: `web3.py` connected to an RPC provider (like Infura or Alchemy) — all ENS resolution happens server-side in Django views.
- **Graph Visualization**: A JavaScript graph library (e.g., `cytoscape.js` or `vis-network`) loaded via CDN in Django templates.
- **Containerization**: Docker and `docker-compose.yml` (slated for later stages).

### Architecture Notes
- Django serves all pages as rendered HTML templates — no separate frontend server.
- ENS data is fetched server-side in Django views using `web3.py` and passed to templates via context.
- The Django REST framework (or plain Django views returning JSON) will power the AJAX calls for graph edge management in Phase 3.
- A single `docker-compose.yml` will orchestrate the Django app and PostgreSQL containers.

## 3. List of Tasks

### Phase 1 Tasks (Profile Viewer & Deployment)
- [ ] Initialize the Django project and app structure.
- [ ] Install and configure `web3.py` as the Ethereum RPC client.
- [ ] Create a Django view and template for the ENS search bar (home page).
- [ ] Create a Django view that resolves an ENS name via `web3.py` and renders the profile template with all populated blockchain fields.
- [ ] Configure hosting and deploy the Phase 1 app to a live URL (e.g., Railway, Render, or Fly.io).

### Phase 2 Tasks (Network Graph)
- [ ] Select and load a suitable JS graph visualization library via CDN in a Django template.
- [ ] Create a Django view and template for the graph page with an input area for ENS name pairs.
- [ ] Render graph nodes and edges using the JS library, driven by data passed from the Django view.
- [ ] Add click handlers on graph nodes to link to Phase 1 profile pages (`/profile/<ens_name>/`).

### Phase 3 Tasks (Persistence and Editing)
- [ ] Configure Django to connect to a PostgreSQL database.
- [ ] Define the Database Schema/Models for ENS social edges.
- [ ] Create Django REST API endpoints (JSON views) for adding, fetching, and deleting friendship edges.
- [ ] Update the graph template with AJAX calls to add/delete edges via the Django API.

### DevOps and Infrastructure Tasks (Later)
- [ ] Create a `Dockerfile` for the Django app.
- [ ] Set up a `docker-compose.yml` to spin up the Django app and PostgreSQL containers simultaneously.
