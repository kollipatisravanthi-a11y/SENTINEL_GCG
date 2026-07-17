import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


NODES = {
    "NGO": "http://localhost:8001",
    "MEDIA": "http://localhost:8002",
    "OMBUDSMAN": "http://localhost:8003",
    "PUBLIC": "http://localhost:8004",
}

MAIN_SERVER = "http://localhost:8000"


def request_json(url, method="GET"):
    req = Request(url, method=method)
    if method == "POST":
        req.add_header("Content-Type", "application/json")
        req.data = b"{}"
    with urlopen(req, timeout=5) as response:
        body = response.read().decode("utf-8")
    return json.loads(body) if body else {}


def short_hash(value):
    if not value:
        return "-"
    return value[:12] + "..."


def print_complaints(complaints, source):
    if not complaints:
        print("No complaints found from", source)
        return

    print(f"\nComplaints from {source}:")
    print("-" * 78)
    print(f"{'ID':<5} {'TYPE':<18} {'LOCATION':<20} {'STATUS':<16} HASH")
    print("-" * 78)
    for complaint in complaints:
        cid = complaint.get("id", "-")
        ctype = str(complaint.get("complaint_type", "-"))[:18]
        location = str(complaint.get("location", "-"))[:20]
        status = str(complaint.get("status", "-"))[:16]
        rhash = short_hash(complaint.get("record_hash"))
        print(f"{cid:<5} {ctype:<18} {location:<20} {status:<16} {rhash}")


def fetch_complaints(node_url):
    try:
        ledger = request_json(f"{MAIN_SERVER}/ledger")
        complaints = ledger.get("complaints", [])
        if complaints:
            return complaints, "main ledger"
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        pass

    try:
        chain = request_json(f"{node_url}/chain/all")
        return chain.get("complaints", []), "selected node"
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        return [], "backend API"


def select_node():
    names = list(NODES)
    print("\nSelect node to tamper:")
    for index, name in enumerate(names, start=1):
        print(f"{index}. {name} ({NODES[name]})")

    while True:
        choice = input("Node number or name: ").strip().upper()
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(names):
                return names[idx - 1]
        if choice in NODES:
            return choice
        print("Invalid node. Choose 1-4 or one of:", ", ".join(names))


def select_complaint_id(complaints):
    valid_ids = {
        int(c["id"])
        for c in complaints
        if isinstance(c, dict) and str(c.get("id", "")).isdigit()
    }

    while True:
        raw = input("\nComplaint ID to tamper: ").strip()
        if not raw.isdigit():
            print("Enter a numeric complaint ID.")
            continue

        complaint_id = int(raw)
        if valid_ids and complaint_id not in valid_ids:
            print("That ID was not in the displayed list. You can still use it.")
            confirm = input("Continue with this ID? [y/N]: ").strip().lower()
            if confirm != "y":
                continue
        return complaint_id


def confirm_tamper(node_name, complaint_id):
    print(
        f"\nThis will tamper complaint #{complaint_id} on the {node_name} node only."
    )
    print("Type TAMPER to continue.")
    return input("> ").strip() == "TAMPER"


def tamper(node_name, complaint_id):
    node_url = NODES[node_name]
    result = request_json(
        f"{node_url}/simulate/tamper/{complaint_id}",
        method="POST",
    )
    print("\nTamper response:")
    print(json.dumps(result, indent=2))

    try:
        verification = request_json(f"{node_url}/chain/verify")
        print("\nNode chain verification:")
        print(json.dumps(verification, indent=2))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        print("\nTamper call finished, but verification failed:", exc)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Tamper a SENTINEL complaint on a selected node for demo use."
    )
    parser.add_argument(
        "--node",
        choices=list(NODES),
        help="Node to tamper: NGO, MEDIA, OMBUDSMAN, or PUBLIC.",
    )
    parser.add_argument(
        "--complaint",
        type=int,
        help="Complaint ID to tamper.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip the TAMPER confirmation prompt.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    node_name = args.node or select_node()
    node_url = NODES[node_name]

    complaints, source = fetch_complaints(node_url)
    print_complaints(complaints, source)

    complaint_id = args.complaint or select_complaint_id(complaints)

    if not args.yes and not confirm_tamper(node_name, complaint_id):
        print("Cancelled.")
        return 1

    try:
        tamper(node_name, complaint_id)
    except HTTPError as exc:
        message = exc.read().decode("utf-8", errors="replace")
        print(f"\nHTTP {exc.code}: {message}")
        return 1
    except (URLError, TimeoutError) as exc:
        print("\nCould not reach the backend node.")
        print("Make sure the main server and node servers are running.")
        print("Details:", exc)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
