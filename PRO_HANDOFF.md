# SPACLY — Release & Audit Handoff

## Repository and Current Deployment

- **Project:** SPACLY
- **Main Contributor:** Dark-Brain07
- **Branch:** `main`
- **Network:** GenLayer StudioNet, Chain ID `61999`
- **Contract Address:** [`0x860De7Dc72128C1F2A7EF9d415761641B05C25Bb`](https://explorer-studio.genlayer.com/address/0x860De7Dc72128C1F2A7EF9d415761641B05C25Bb)
- **Deployment Transaction:** `0xd6633802dd36137b269e6db8d9d91b955474a67e13b6db31a32748408b7c6932`
- **Deployment Result:** `FINALIZED`, `MAJORITY_AGREE`, leader `SUCCESS`
- **Pinned Runner:** `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`

See [`proof/live/spacly-deployment.json`](proof/live/spacly-deployment.json).

## Live On-Chain Verified Cases

The Spacly contract lifecycle was tested directly on GenLayer StudioNet:
- **Migration #1:** Created with title `"Spacly Planetary Acceptance Protocol"`, baseline `"https://example.com"`, and 3600s review window. Status: `FINALIZED` (`MAJORITY_AGREE`, votes: `['IDLE', 'IDLE', 'AGREE', 'AGREE', 'AGREE']`, tx `0x6d5bffa7018cba63c974f6dabab988860ad5ba3aca6ba125c5ac16557b102c8e`).
- **Route Registration:** Registered route `"core"` on Migration 1 with path `"/"` and orbit navigation rule. Status: `FINALIZED` (`MAJORITY_AGREE`, votes: `['AGREE', 'AGREE', 'AGREE', 'AGREE', 'AGREE']`, tx `0xf5e0078871ee264343784eab899ff60b5aa0976995e2fd5907f1cfe5652d976d`).
- **Migration #2:** Created secondary migration `"Spacly Secondary Mesh Migration"`. Status: `FINALIZED` (`MAJORITY_AGREE`, votes: `['AGREE', 'AGREE', 'AGREE', 'AGREE', 'AGREE']`, tx `0x5f3604955f325e47d35e98c30884ea77bebb6dd8c81134cf7b600294116f1b34`).
- **Migration Cancellation:** Canceled migration #2. Status: `FINALIZED` (`MAJORITY_AGREE`, votes: `['IDLE', 'IDLE', 'AGREE', 'AGREE', 'AGREE']`, tx `0x46848f45f6415bc4439d431825d245b54a9f9a3a6877854c41ddb55e029c8040`). Verified terminal state `CANCELLED`.
- **View Methods:** `get_config()`, `get_stats()`, `get_migration(1)`, `get_route(1, 'core')`, `list_migrations(0, 10)`, `migrations_of(...)`, `get_events(0, 10)` all queried and verified.

See [`proof/live/spacly-live-cases.json`](proof/live/spacly-live-cases.json).

## Frontend Styling & Experience

The frontend has been revamped with:
- Deep cosmic dark mode with subtle nebula glows.
- Re-engineered glowing pill buttons with micro-animations and responsive states.
- High-contrast typography and accessible status pills.
- Connected Web3 wallet session provider supporting MetaMask and injected providers on StudioNet 61999.
