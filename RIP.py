import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

basicauth = ("admin", "class")
headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}

# Networks advertised by RIP on each router
ROUTERS = {
    "ISPN": {
        "host": "192.168.130.5",
        "networks": [
            "192.168.128.0",   # Loopback0 segment (/25)
            "192.168.129.0"    # Serial link to JUNK (/30)
        ]
    },
    "JUNK": {
        "host": "192.168.130.6",
        "networks": [
            "192.168.129.0",   # Serial link to ISPN (/30)
            "192.168.130.0"    # LAN segment
        ]
    },
    "MGM": {
        "host": "192.168.130.1",
        "networks": [
            "192.168.130.0"    # Segment toward JUNK LAN
        ]
    }
}

RIP_URL_TEMPLATE = (
    "https://{host}/restconf/data/"
    "Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-rip:rip"
)


def _patch(host, payload, label):
    """PATCH a partial RIP payload (merge, not replace)."""
    url = RIP_URL_TEMPLATE.format(host=host)
    try:
        resp = requests.patch(
            url,
            json=payload,
            auth=basicauth,
            headers=headers,
            verify=False,
            timeout=15
        )
        print(f"  {label}: {resp.status_code}")
        if resp.status_code >= 300:
            print(f"    {resp.text[:400]}")
        return resp.status_code
    except requests.RequestException as e:
        print(f"  {label} failed: {e}")
        return None


def configure_rip(router_name, host, networks):
    """Configure RIPv2 — version first, then each network individually."""
    print(f"\n--- {router_name} ({host}) ---")
    print(f"Networks: {networks}")

    # Step 1: ensure version 2
    _patch(host, {"Cisco-IOS-XE-rip:rip": {"version": 2}}, "version 2")

    # Step 2: add each network separately so none get dropped
    for net in networks:
        payload = {"Cisco-IOS-XE-rip:rip": {"network": [{"ip": net}]}}
        _patch(host, payload, f"network {net}")


def verify_rip(router_name, host):
    """GET the RIP config back and show which networks landed."""
    url = RIP_URL_TEMPLATE.format(host=host)
    print(f"\n--- {router_name} verification ---")
    try:
        resp = requests.get(
            url,
            auth=basicauth,
            headers=headers,
            verify=False,
            timeout=15
        )
        print(f"  Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json().get("Cisco-IOS-XE-rip:rip", {})
            nets = [n.get("ip") for n in data.get("network", [])]
            print(f"  version: {data.get('version', '?')}")
            print(f"  networks on device: {nets}")
        else:
            print(f"  {resp.text[:400]}")
    except requests.RequestException as e:
        print(f"  Request failed: {e}")


# Configure RIP on all routers
for name, info in ROUTERS.items():
    configure_rip(name, info["host"], info["networks"])

# Read back what actually got applied
for name, info in ROUTERS.items():
    verify_rip(name, info["host"])