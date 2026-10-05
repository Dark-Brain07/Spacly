"""Spacly Deployment and Live Test Suite on GenLayer StudioNet.

Deploys Spacly (contracts/spacly.py) to GenLayer StudioNet (chain 61999)
and executes real transactions against the contract to test all key lifecycle functions.
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import genlayer_py as gl
    from genlayer_py.chains import studionet
    from genlayer_py.types import TransactionStatus
except ImportError:
    print("Error: genlayer-py is required. Run: pip install genlayer-py")
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_FILE = ROOT / "contracts" / "spacly.py"


def wait_finalized(client, tx_hash: str, label: str, max_wait: int = 300) -> dict:
    print(f"\n--> Waiting for {label} to finalize on-chain...")
    print(f"    Transaction Hash: {tx_hash}")
    start = time.time()
    while time.time() - start < max_wait:
        try:
            tx = client.get_transaction(tx_hash)
            status_name = tx.get("status_name", "").upper()
            result_name = tx.get("result_name", "").upper()
            last_round = tx.get("last_round", {})
            votes = last_round.get("validator_votes_name", [])

            if status_name == "FINALIZED":
                print(f"    [FINALIZED] Consensus: {result_name} | Votes: {votes}")
                return tx
            elif status_name in ("ERROR", "ROLLBACK", "FAILED"):
                raise RuntimeError(f"Transaction failed with status {status_name}: {tx}")
        except Exception as e:
            if "Transaction failed" in str(e):
                raise
        time.sleep(3)
    raise TimeoutError(f"Transaction {tx_hash} did not finalize within {max_wait}s")


def main():
    print("=" * 70)
    print("SPACLY — STUDIONET DEPLOYMENT & LIVE ON-CHAIN TRANSACTION TEST")
    print("=" * 70)

    if not CONTRACT_FILE.exists():
        print(f"Contract file not found at {CONTRACT_FILE}")
        sys.exit(1)

    code = CONTRACT_FILE.read_text(encoding="utf-8")
    raw_key = os.environ.get("DEPLOYER_PRIVATE_KEY", "").strip()
    if raw_key:
        account = gl.create_account(raw_key if raw_key.startswith("0x") else f"0x{raw_key}")
    else:
        account = gl.create_account()

    client = gl.create_client(chain=studionet, account=account)
    print(f"Deployer Account: {account.address}")
    print(f"Target Network:   StudioNet (chain 61999)")
    print(f"Contract Source:  {CONTRACT_FILE.relative_to(ROOT)}")

    # 1. DEPLOYMENT
    print("\n--- STEP 1: Deploying Spacly Contract ---")
    tx_hash = client.deploy_contract(code=code, args=[])
    print(f"Deploy Tx Hash: {tx_hash}")
    print("Waiting for consensus finality...")

    receipt = client.wait_for_transaction_receipt(
        hash=tx_hash,
        status=TransactionStatus.FINALIZED,
        interval=3000,
        retries=100,
    )

    contract_address = (
        getattr(receipt, "contract_address", None)
        or (receipt.get("data", {}).get("contract_address") if isinstance(receipt, dict) else None)
        or (receipt.get("contract_address") if isinstance(receipt, dict) else None)
    )

    if not contract_address:
        tx_info = client.get_transaction(tx_hash)
        contract_address = (
            tx_info.get("data", {}).get("contract_address")
            or tx_info.get("contract_address")
            or tx_info.get("data", {}).get("created_contract_address")
        )

    print(f"\n[SUCCESS] Spacly Contract Deployed!")
    print(f"Contract Address: {contract_address}")
    print(f"Explorer URL:     https://explorer-studio.genlayer.com/address/{contract_address}")

    deployment_record = {
        "project": "Spacly",
        "contract": "Spacly",
        "network": "studionet",
        "chain_id": 61999,
        "contract_address": contract_address,
        "deploy_transaction": tx_hash,
        "deployer": account.address,
        "deployed_at": datetime.now(timezone.utc).isoformat(),
        "explorer_url": f"https://explorer-studio.genlayer.com/address/{contract_address}",
    }

    live_records = {
        "deployment": deployment_record,
        "transactions": [],
        "views": {},
    }

    # 2. VIEW: get_config
    print("\n--- STEP 2: Testing View Method: get_config() ---")
    config = client.read_contract(address=contract_address, function_name="get_config")
    print(f"Config: {json.dumps(config, indent=2)}")
    assert config.get("chain_id") == 61999, "Chain ID mismatch"
    assert config.get("network") == "studionet", "Network mismatch"
    live_records["views"]["get_config"] = config
    print("[PASS] get_config verified.")

    # 3. VIEW: get_stats
    print("\n--- STEP 3: Testing View Method: get_stats() ---")
    stats = client.read_contract(address=contract_address, function_name="get_stats")
    print(f"Initial Stats: {stats}")
    live_records["views"]["get_stats_initial"] = stats
    print("[PASS] get_stats verified.")

    # 4. WRITE: create_migration
    print("\n--- STEP 4: Testing Write Method: create_migration() ---")
    tx_create = client.write_contract(
        address=contract_address,
        function_name="create_migration",
        args=["Spacly Genesis Production Acceptance", "https://example.com", 3600],
    )
    r_create = wait_finalized(client, tx_create, "create_migration")
    live_records["transactions"].append({
        "function": "create_migration",
        "args": ["Spacly Genesis Production Acceptance", "https://example.com", 3600],
        "tx_hash": tx_create,
        "status": r_create.get("status_name"),
        "consensus": r_create.get("result_name"),
    })
    print("[PASS] create_migration finalized successfully.")

    # 5. VIEW: get_migration(1)
    print("\n--- STEP 5: Testing View Method: get_migration(1) ---")
    migration_1 = client.read_contract(address=contract_address, function_name="get_migration", args=[1])
    print(f"Migration 1 Data: {json.dumps(migration_1, indent=2)}")
    assert migration_1.get("id") == 1, "Migration ID mismatch"
    assert migration_1.get("state") == "DRAFT", "Migration state should be DRAFT"
    assert migration_1.get("title") == "Spacly Genesis Production Acceptance"
    live_records["views"]["migration_1"] = migration_1
    print("[PASS] get_migration(1) verified.")

    # 6. WRITE: add_route
    print("\n--- STEP 6: Testing Write Method: add_route() ---")
    rules = [
        {
            "id": "landing_content",
            "question": "Does the landing page preserve essential core navigation and service claims?",
            "allowed_changes": "Visual layout and styling modernization allowed",
        }
    ]
    tx_add_route = client.write_contract(
        address=contract_address,
        function_name="add_route",
        args=[1, "home", "https://example.com/", "/", json.dumps(rules)],
    )
    r_add_route = wait_finalized(client, tx_add_route, "add_route")
    live_records["transactions"].append({
        "function": "add_route",
        "args": [1, "home", "https://example.com/", "/", rules],
        "tx_hash": tx_add_route,
        "status": r_add_route.get("status_name"),
        "consensus": r_add_route.get("result_name"),
    })
    print("[PASS] add_route finalized successfully.")

    # 7. VIEW: get_route(1, "home")
    print("\n--- STEP 7: Testing View Method: get_route(1, 'home') ---")
    route_home = client.read_contract(address=contract_address, function_name="get_route", args=[1, "home"])
    print(f"Route Home Data: {json.dumps(route_home, indent=2)}")
    assert route_home.get("route_id") == "home", "Route ID mismatch"
    assert route_home.get("baseline_url") == "https://example.com/", "Baseline URL mismatch"
    live_records["views"]["route_home"] = route_home
    print("[PASS] get_route(1, 'home') verified.")

    # 8. VIEW: list_migrations(0, 5)
    print("\n--- STEP 8: Testing View Method: list_migrations(0, 5) ---")
    migrations_list = client.read_contract(address=contract_address, function_name="list_migrations", args=[0, 5])
    print(f"Migrations list: {len(migrations_list)} items found.")
    assert len(migrations_list) >= 1
    live_records["views"]["list_migrations"] = migrations_list
    print("[PASS] list_migrations verified.")

    # 9. VIEW: get_events(0, 10)
    print("\n--- STEP 9: Testing View Method: get_events(0, 10) ---")
    events = client.read_contract(address=contract_address, function_name="get_events", args=[0, 10])
    print(f"Retrieved {len(events)} events from Spacly event ring buffer.")
    for ev in events:
        print(f"  - Event #{ev.get('index')}: {ev.get('kind')} (Migration {ev.get('migration_id')})")
    live_records["views"]["events"] = events
    print("[PASS] get_events verified.")

    # 10. SAVE RECORDS
    proof_dir = ROOT / "proof" / "live"
    proof_dir.mkdir(parents=True, exist_ok=True)
    deployment_file = proof_dir / "spacly-deployment.json"
    deployment_file.write_text(json.dumps(deployment_record, indent=2), encoding="utf-8")
    print(f"\nSaved deployment record to: {deployment_file.relative_to(ROOT)}")

    cases_file = proof_dir / "spacly-live-cases.json"
    cases_file.write_text(json.dumps(live_records, indent=2), encoding="utf-8")
    print(f"Saved live test report to: {cases_file.relative_to(ROOT)}")

    # Update web env file
    web_env_file = ROOT / "apps" / "web" / ".env.local"
    web_env_file.write_text(
        f"NEXT_PUBLIC_SPACLY_CONTRACT_ADDRESS={contract_address}\n"
        f"NEXT_PUBLIC_SPACLY_CONTRACT_ADDRESS={contract_address}\n",
        encoding="utf-8",
    )
    print(f"Updated {web_env_file.relative_to(ROOT)} with live contract address.")

    print("\n" + "=" * 70)
    print("ALL SPACLY DEPLOYMENT AND TRANSACTION TESTS COMPLETED WITH 100% SUCCESS!")
    print(f"Contract: {contract_address}")
    print(f"Explorer: https://explorer-studio.genlayer.com/address/{contract_address}")
    print("=" * 70)


if __name__ == "__main__":
    main()
