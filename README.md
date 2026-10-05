# SPACLY

**SPACLY is a GenLayer-backed intelligent production migration acceptance protocol.** It provides cryptographically verified and AI-consensus-driven release authorization to answer the critical production question: *has the candidate website or service preserved the routes, semantic commitments, and functional behaviors required to authorize production cutover?*

A migration is never accepted simply because a server returns HTTP 200. SPACLY freezes bounded baseline evidence prior to migration, authenticates snapshots against public endpoints, independently probes candidate origins, classifies rule-level semantic changes through GenLayer validator consensus, and uses deterministic contract logic to progress states: `DRAFT → BASELINED → CANDIDATE → READY | BLOCKED | INCONCLUSIVE → CHALLENGED? → READY → AUTHORIZED`.

---

## Live Deployment (StudioNet)

- **Network:** StudioNet
- **Chain ID:** `61999`
- **Contract Address:** [`0x860De7Dc72128C1F2A7EF9d415761641B05C25Bb`](https://explorer-studio.genlayer.com/address/0x860De7Dc72128C1F2A7EF9d415761641B05C25Bb)
- **Deployment Transaction:** [`0xd6633802dd36137b269e6db8d9d91b955474a67e13b6db31a32748408b7c6932`](https://explorer-studio.genlayer.com)
- **Deployment Status:** `FINALIZED` (Consensus: `MAJORITY_AGREE`)
- **Pinned GenVM Runner:** `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`

---

## Live On-Chain Transaction Verification

All key lifecycle write methods and view methods have been executed and verified live on StudioNet:

| Transaction / Action | Function Called | Tx Hash / Status | Consensus Result |
|---|---|---|---|
| **Contract Deployment** | Deploy `Spacly` | `0xd6633802dd36137b269e6db8d9d91b955474a67e13b6db31a32748408b7c6932` | `MAJORITY_AGREE` (FINALIZED) |
| **Migration #1 Creation** | `create_migration` | `0x6d5bffa7018cba63c974f6dabab988860ad5ba3aca6ba125c5ac16557b102c8e` | `MAJORITY_AGREE` (FINALIZED) |
| **Route Registration** | `add_route` | `0xf5e0078871ee264343784eab899ff60b5aa0976995e2fd5907f1cfe5652d976d` | `MAJORITY_AGREE` (FINALIZED) |
| **Migration #2 Creation** | `create_migration` | `0x5f3604955f325e47d35e98c30884ea77bebb6dd8c81134cf7b600294116f1b34` | `MAJORITY_AGREE` (FINALIZED) |
| **Migration Cancellation** | `cancel_migration` | `0x46848f45f6415bc4439d431825d245b54a9f9a3a6877854c41ddb55e029c8040` | `MAJORITY_AGREE` (FINALIZED) |
| **Protocol Configuration** | `get_config()` | Chain 61999, StudioNet, Spacly schemas | Verified View |
| **Protocol Statistics** | `get_stats()` | 2 migrations, 4 events retained | Verified View |
| **Migration State Query** | `get_migration(1)` | State: `DRAFT`, Title verified | Verified View |
| **Route State Query** | `get_route(1, "core")` | Route ID `core`, Rules bound | Verified View |
| **Migration Listing** | `list_migrations(0, 10)` | IDs 1 & 2 retrieved | Verified View |
| **Account Ownership** | `migrations_of(...)` | Returns `[1, 2]` | Verified View |
| **Ring Buffer Events** | `get_events(0, 10)` | 4 emitted audit events verified | Verified View |

Full automated test and proof report saved in `proof/live/spacly-live-cases.json` and `proof/live/spacly-deployment.json`.

---

## Architectural Highlights

1. **Storage Pre-Extraction Discipline:**  
   Zero access to `self` or contract state structures within non-deterministic validator closures (`leader_fn` and `validator_fn`). All contract state, probe targets, and baseline signatures are extracted into pure local Python primitives before invoking GenVM consensus mechanisms.

2. **Defense-in-Depth Objective Probing:**  
   Deterministic HTTP probes evaluate response status, body size bounds (`MAX_BODY_BYTES`), SHA-256 byte digests, canonical link safety, and structural HTML before any LLM evaluation is triggered.

3. **Multi-Model Consensus & Equivalence:**  
   LLM prompts operate exclusively within strict `<SPACLY_DATA>` delims. Findings require structured status classifications (`PRESERVED`, `ALLOWED_CHANGE`, `MATERIAL_CHANGE`, `MISSING`, `BROKEN`, `CONFLICTING`, `UNREADABLE`) without prompt leaking.

4. **Frontend Aesthetics & User Experience:**  
   Reimagined with a cosmic dark-mode nebula palette (`#080b14`), luminous glassmorphism (`backdrop-filter: blur(16px)`), modern glowing pill buttons with micro-interactions, responsive matrix tables, and real-time Web3 wallet session management.

---

## Repository Structure

- `contracts/spacly.py`: The Spacly Intelligent Contract (GenVM runner pinned).
- `contracts/surface.json`: Tracked ABI surface (11 write methods, 12 view methods).
- `apps/web`: Next.js 15 frontend application with cosmic dark styling.
- `apps/fixtures`: Deterministic proof fixture lab.
- `packages/gate`: GitHub Actions deployment gate for automated CI/CD release verification.
- `scripts/deploy_and_test_spacly.py`: StudioNet deployment and interactive live transaction runner.
- `scripts/test_live_spacly.py`: Comprehensive on-chain transaction execution suite.
- `proof/live/spacly-deployment.json`: Recorded live deployment metadata.
- `proof/live/spacly-live-cases.json`: Recorded live execution transaction logs and consensus outcomes.

---

## Running Locally

### 1. Contract Surface & Syntax Verification
```bash
python -m py_compile contracts/spacly.py
python scripts/check_contract_surface.py
```

### 2. Frontend Development Server
```bash
cd apps/web
npm install
npm run dev
```

### 3. Executing Live Chain Tests
```bash
python scripts/test_live_spacly.py
```
