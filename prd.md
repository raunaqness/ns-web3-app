# Product Requirements Document (PRD)

## Project Overview
A web application to visualize and manage an Ethereum Name Service (ENS) social network. The platform allows users to view ENS profiles, visualize social connections between ENS domains via an interactive graph, and manually edit these network relationships.

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
- **Interactive Visualization**: Create an in-browser graph displaying these nodes and their connections.
- **Profile Navigation**: Every node on the graph must be clickable and dynamically route the user to the corresponding ENS profile page created in Phase 1.

### Phase 3: Editable Graph Relationships
- **Modify Edges**: Browser interface capabilities to add new friend relationships (edges) or delete existing ones directly from the visualization.
- **State Persistence**: Store all edits and friend relationships reliably in a database.

## 2. Technical Specifications

### Technology Stack
- **Frontend**: React (JavaScript)
- **Backend API**: Python (Django)
- **Database**: PostgreSQL (for Step 3 relationships)
- **Blockchain Interaction**: Web3 library (e.g., `ethers.js`, `viem`, or `web3.py`) connected to an RPC provider (like Infura or Alchemy).
- **Graph Visualization**: A Javascript graph library (e.g., `react-force-graph`, `cytoscape.js`, or `vis-network`).
- **Containerization**: Docker and `docker-compose.yml` (slated for later stages).

### Architecture Notes
- The Django backend will serve as an intermediary REST API layer between the React client and the PostgreSQL database.
- It is acceptable to start with a purely React/Web3 approach for Phase 1 to ensure rapid live deployment, then incrementally introduce Django and Postgres for Phases 2/3.

## 3. List of Tasks

### Phase 1 Tasks (Profile Viewer & Deployment)
- [ ] Initialize the React frontend repository.
- [ ] Set up Ethereum RPC connection using a Web3 library.
- [ ] Develop the ENS Search Bar component.
- [ ] Develop the Profile UI component to dynamically render all populated blockchain fields.
- [ ] Configure hosting and deploy the Phase 1 web app to a live URL (e.g., Vercel, Netlify, or Render).

### Phase 2 Tasks (Network Graph)
- [ ] Select and install a suitable JS graph visualization library.
- [ ] Implement an input mechanism to accept ENS name pairs.
- [ ] Develop the interactive graph component to render nodes and edges.
- [ ] Add routing logic to graph nodes to link to Phase 1 profile pages (`/profile/:ensName`).

### Phase 3 Tasks (Persistence and Editing)
- [ ] Initialize the Django backend repository.
- [ ] Configure Django to connect to a PostgreSQL database.
- [ ] Define the Database Schema/Models for ENS identities and their social edges.
- [ ] Create Django REST API endpoints for adding, fetching, and deleting friendship edges.
- [ ] Update frontend graph component state to allow interactive adding/deleting of edges.
- [ ] Integrate frontend API calls with the Django backend.

### DevOps and Infrastructure Tasks (Later)
- [ ] Create a `Dockerfile` for the Django Backend.
- [ ] Create a `Dockerfile` for the React Frontend.
- [ ] Set up a `docker-compose.yml` to spin up Frontend, Backend, and PostgreSQL containers simultaneously.
