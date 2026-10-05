"""Comprehensive Live Transaction Testing on deployed Spacly Contract."""

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
except ImportError:
    print("Error: genlayer-py is required. Run: pip install genlayer-py")
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_ADDRESS = "0x860De7Dc72128C1F2A7EF9d415761641B05C25Bb"
DEPLOY_TX = "0xd6633802dd36137b269e6db8d9d91b955474a67e13b6db31a32748408b7c6932"


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
    print("=" * 75)
    print("SPACLY — STUDIONET LIVE CONTRACT TRANSACTION TEST SUITE")
    print("=" * 75)
    print(f"Contract Address:  {CONTRACT_ADDRESS}")
    print(f"Explorer URL:      https://explorer-studio.genlayer.com/address/{CONTRACT_ADDRESS}")
    print(f"Deployment Tx:     {DEPLOY_TX}")

    account = gl.create_account()
    client = gl.create_client(chain=studionet, account=account)
    print(f"Operator Address:  {account.address}")
    print("=" * 75)

    test_results = {
        "contract_address": CONTRACT_ADDRESS,
        "deploy_tx": DEPLOY_TX,
        "operator": account.address,
        "network": "studionet",
        "chain_id": 61999,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "transactions": [],
        "views": {},
    }

    # 1. VIEW: get_config
    print("\n1. [VIEW] get_config()")
    config = client.read_contract(address=CONTRACT_ADDRESS, function_name="get_config")
    print(f"   Config: {json.dumps(config, indent=2)}")
    assert config["chain_id"] == 61999
    assert config["network"] == "studionet"
    assert config["snapshot_schema"] == "spacly.baseline.v1"
    assert config["candidate_manifest_schema"] == "spacly.candidate.v1"
    test_results["views"]["get_config"] = config
    print("   -> PASSED")

    # 2. VIEW: get_stats (initial)
    print("\n2. [VIEW] get_stats() [Initial]")
    stats1 = client.read_contract(address=CONTRACT_ADDRESS, function_name="get_stats")
    print(f"   Initial Stats: {stats1}")
    test_results["views"]["initial_stats"] = stats1
    print("   -> PASSED")

    # 3. WRITE: create_migration
    print("\n3. [WRITE] create_migration (Spacly Planetary Acceptance Protocol)...")
    tx_create = client.write_contract(
        address=CONTRACT_ADDRESS,
        function_name="create_migration",
        args=["Spacly Planetary Acceptance Protocol", "https://example.com", 3600],
    )
    r_create = wait_finalized(client, tx_create, "create_migration #1")
    test_results["transactions"].append({
        "label": "create_migration #1",
        "tx_hash": tx_create,
        "function": "create_migration",
        "args": ["Spacly Planetary Acceptance Protocol", "https://example.com", 3600],
        "status": r_create.get("status_name"),
        "consensus": r_create.get("result_name"),
    })
    print("   -> PASSED")

    # 4. VIEW: get_migration(1)
    print("\n4. [VIEW] get_migration(1)")
    m1 = client.read_contract(address=CONTRACT_ADDRESS, function_name="get_migration", args=[1])
    print(f"   Migration 1: {json.dumps(m1, indent=2)}")
    assert m1["id"] == 1
    assert m1["title"] == "Spacly Planetary Acceptance Protocol"
    assert m1["state"] == "DRAFT"
    assert m1["baseline_origin"] == "https://example.com"
    test_results["views"]["migration_1"] = m1
    print("   -> PASSED")

    # 5. WRITE: add_route
    print("\n5. [WRITE] add_route (Route: core on Migration 1)...")
    rules = [
        {
            "id": "orbit_nav",
            "question": "Are core orbital navigation links and services preserved?",
            "allowed_changes": "Modernized styling permitted",
        }
    ]
    tx_route = client.write_contract(
        address=CONTRACT_ADDRESS,
        function_name="add_route",
        args=[1, "core", "https://example.com/", "/", json.dumps(rules)],
    )
    r_route = wait_finalized(client, tx_route, "add_route")
    test_results["transactions"].append({
        "label": "add_route",
        "tx_hash": tx_route,
        "function": "add_route",
        "args": [1, "core", "https://example.com/", "/", rules],
        "status": r_route.get("status_name"),
        "consensus": r_route.get("result_name"),
    })
    print("   -> PASSED")

    # 6. VIEW: get_route(1, "core")
    print("\n6. [VIEW] get_route(1, 'core')")
    r1 = client.read_contract(address=CONTRACT_ADDRESS, function_name="get_route", args=[1, "core"])
    print(f"   Route: {json.dumps(r1, indent=2)}")
    assert r1["route_id"] == "core"
    assert r1["baseline_url"] == "https://example.com/"
    assert r1["candidate_path"] == "/"
    assert len(r1["rules"]) == 1
    test_results["views"]["route_1_core"] = r1
    print("   -> PASSED")

    # 7. WRITE: create_migration #2
    print("\n7. [WRITE] create_migration (Secondary Mesh Migration)...")
    tx_create2 = client.write_contract(
        address=CONTRACT_ADDRESS,
        function_name="create_migration",
        args=["Spacly Secondary Mesh Migration", "https://example.com", 1800],
    )
    r_create2 = wait_finalized(client, tx_create2, "create_migration #2")
    test_results["transactions"].append({
        "label": "create_migration #2",
        "tx_hash": tx_create2,
        "function": "create_migration",
        "args": ["Spacly Secondary Mesh Migration", "https://example.com", 1800],
        "status": r_create2.get("status_name"),
        "consensus": r_create2.get("result_name"),
    })
    print("   -> PASSED")

    # 8. WRITE: cancel_migration #2
    print("\n8. [WRITE] cancel_migration(2)...")
    tx_cancel = client.write_contract(
        address=CONTRACT_ADDRESS,
        function_name="cancel_migration",
        args=[2],
    )
    r_cancel = wait_finalized(client, tx_cancel, "cancel_migration #2")
    test_results["transactions"].append({
        "label": "cancel_migration #2",
        "tx_hash": tx_cancel,
        "function": "cancel_migration",
        "args": [2],
        "status": r_cancel.get("status_name"),
        "consensus": r_cancel.get("result_name"),
    })
    print("   -> PASSED")

    # 9. VIEW: get_migration(2)
    print("\n9. [VIEW] get_migration(2) [Post Cancel]")
    m2 = client.read_contract(address=CONTRACT_ADDRESS, function_name="get_migration", args=[2])
    print(f"   Migration 2: state={m2.get('state')}, cancelled={m2.get('cancelled')}")
    assert m2["state"] == "CANCELLED"
    assert m2["cancelled"] is True
    test_results["views"]["migration_2"] = m2
    print("   -> PASSED")

    # 10. VIEW: list_migrations(0, 10)
    print("\n10. [VIEW] list_migrations(0, 10)")
    all_m = client.read_contract(address=CONTRACT_ADDRESS, function_name="list_migrations", args=[0, 10])
    print(f"    Found {len(all_m)} migrations:")
    for item in all_m:
        print(f"    - ID {item['id']}: '{item['title']}' | State: {item['state']}")
    assert len(all_m) >= 2
    test_results["views"]["list_migrations"] = all_m
    print("    -> PASSED")

    # 11. VIEW: migrations_of(account.address, 0, 10)
    print(f"\n11. [VIEW] migrations_of({account.address})")
    my_m = client.read_contract(address=CONTRACT_ADDRESS, function_name="migrations_of", args=[account.address, 0, 10])
    print(f"    Operator migrations: {my_m}")
    assert len(my_m) >= 2
    test_results["views"]["operator_migrations"] = my_m
    print("    -> PASSED")

    # 12. VIEW: get_events(0, 10)
    print("\n12. [VIEW] get_events(0, 10)")
    events = client.read_contract(address=CONTRACT_ADDRESS, function_name="get_events", args=[0, 10])
    print(f"    Retrieved {len(events)} events:")
    for ev in events:
        print(f"    - Event #{ev['index']}: {ev['kind']} (Migration ID: {ev['migration_id']})")
    assert len(events) >= 4
    test_results["views"]["events"] = events
    print("    -> PASSED")

    # 13. VIEW: get_stats (final)
    print("\n13. [VIEW] get_stats() [Final]")
    stats_final = client.read_contract(address=CONTRACT_ADDRESS, function_name="get_stats")
    print(f"    Final Stats: {stats_final}")
    assert stats_final["migrations"] >= 2
    assert stats_final["events_total"] >= 4
    test_results["views"]["final_stats"] = stats_final
    print("    -> PASSED")

    # Save live proof
    proof_dir = ROOT / "proof" / "live"
    proof_dir.mkdir(parents=True, exist_ok=True)
    report_file = proof_dir / "spacly-live-cases.json"
    report_file.write_text(json.dumps(test_results, indent=2), encoding="utf-8")
    print(f"\nDetailed live proof report saved to: {report_file.relative_to(ROOT)}")

    deployment_record = {
        "project": "Spacly",
        "contract": "Spacly",
        "network": "studionet",
        "chain_id": 61999,
        "contract_address": CONTRACT_ADDRESS,
        "deploy_transaction": DEPLOY_TX,
        "operator": account.address,
        "deployed_at": datetime.now(timezone.utc).isoformat(),
        "explorer_url": f"https://explorer-studio.genlayer.com/address/{CONTRACT_ADDRESS}",
    }
    deployment_file = proof_dir / "spacly-deployment.json"
    deployment_file.write_text(json.dumps(deployment_record, indent=2), encoding="utf-8")
    print(f"Deployment record saved to: {deployment_file.relative_to(ROOT)}")

    # Update web env file
    web_env_file = ROOT / "apps" / "web" / ".env.local"
    web_env_file.write_text(
        f"NEXT_PUBLIC_SPACLY_CONTRACT_ADDRESS={CONTRACT_ADDRESS}\n"
        f"NEXT_PUBLIC_CUTOVER_CONTRACT_ADDRESS={CONTRACT_ADDRESS}\n",
        encoding="utf-8",
    )
    print(f"Frontend .env.local configured with contract address: {CONTRACT_ADDRESS}")

    print("\n" + "=" * 75)
    print("SUCCESS: ALL TRANSACTIONS & VIEW METHODS VERIFIED ON STUDIONET!")
    print(f"Contract: {CONTRACT_ADDRESS}")
    print(f"Explorer: https://explorer-studio.genlayer.com/address/{CONTRACT_ADDRESS}")
    print("=" * 75)


if __name__ == "__main__":
    main()
