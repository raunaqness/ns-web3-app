# ENS Social Network App

A web application to visualize and manage an Ethereum Name Service (ENS) social network. The platform allows users to view ENS profiles, fetch on-chain data including social connections, metadata, and financial activity, and visualize/edit connections between ENS domains.

## Features

- **ENS Profile Lookups**: Search for any valid `.eth` name (e.g., `vitalik.eth`).
- **Blockchain Data Integration**:
  - Pull text records directly from the ENS registry via `web3.py`.
  - Display social records (Twitter, GitHub, Discord, website URLs).
  - Retrieve bound wallet addresses for cross-chain activity (ETH, BTC, SOL).
  - Show ENS Metadata like resolver addresses, expiry date, and wrapper status.
- **Etherscan Financials Dashboard**:
  - Seamlessly pulls current ETH balance for associated addresses.
  - Generates transaction pipelines visualizing recent normal & internal transactions directly linking users to the active blockchain ledger.
- **Social Graph Interlink**:
  - Extendable capability to visualize interpersonal relations between multiple ENS addresses as an in-browser graph using JavaScript graph libraries dynamically rendered by Django backend APIs.

## Tech Stack Overview

- **Backend**: Python, Django (with `web3.py` for Web3 integrations).
- **Frontend Engine**: Django Standard Templates (`HTML`/`CSS`/Vanilla `JS`).
- **External Web3 APIs**: 
  - Mainnet Ethereum RPCs (e.g. Infura / Alchemy).
  - Etherscan API.
- **Database**: PostgreSQL (for persistent Graph Network edge/node relationships) / SQLite (Development).

## Local Development Setup

### 1. Requirements
Ensure you have Python 3.9+ installed and optionally access to Docker.

### 2. Environment Variables
To get the application interacting with the blockchain, specific external API keys are needed.
1. Duplicate the example bindings: 
   ```bash
   cp backend/.env.example backend/.env
   ```
2. Populate the `.env` configuration file with your endpoints:
   - `WEB3_PROVIDER_URL` (Your Infura/Alchemy Mainnet URL)
   - `ETHERSCAN_API_KEY` (Your developer token for Etherscan integration)

### 3. Installation & Bootstrapping

Move to the Django source code directory, mount a virtual environment, and install all dependencies:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Deploy local migrations (this sets up SQLite unless `DATABASE_URL` is pointing to Postgres):
```bash
python manage.py migrate
```

Start the Django Development Server:
```bash
python manage.py runserver
```

> **Usage:** Open your browser and navigate to `http://localhost:8000`. Enter a valid namespace (e.g., `vitalik.eth`) to search and interact with the application.

## Project Structure

- `backend/core` - Contains the Django settings configuring the templates, database bindings, and global configurations.
- `backend/profiles` - Contains Django views and routing. `services.py` holds integration logic communicating with ABIs to hit the Etherscan and Infura RPC.
- `backend/templates` - Holds styling schemas, template macros, and base configurations.

## Further Integration Phases 

This repository has a product roadmap divided via three main phases outlined further in [`prd.md`](prd.md):
- [x] Phase 1 - Advanced profile analytics mapped from `.eth` names.
- [ ] Phase 2 - Social Network connections displayed as Interactive DAGs.
- [ ] Phase 3 - Relational edges persisted leveraging a database adapter.
