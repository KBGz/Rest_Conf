import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

basicauth = ("admin", "class")
headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}

JUNK_HOST = "192.168.130.6"
ACL_NAME = "BLOCK_WEB"
INTF = "GigabitEthernet=0%2F0%2F0"

BASE = f"https://{JUNK_HOST}/restconf/data/Cisco-IOS-XE-native:native"


def get(url):
    return requests.get(url, auth=basicauth, headers=headers,
                        verify=False, timeout=15)


def put(url, payload):
    return requests.put(url, json=payload, auth=basicauth, headers=headers,
                        verify=False, timeout=15)


def main():
    intf_url = f"{BASE}/interface/{INTF}"

    print(f"GET {intf_url}")
    r = get(intf_url)
    if r.status_code != 200:
        print(f"GET failed: {r.status_code}\n{r.text[:600]}")
        return

    data = r.json()
    gi = data.get("Cisco-IOS-XE-native:GigabitEthernet", {})
    ip = gi.setdefault("ip", {})

    # Inject access-group with the exact structure the device returned
    ip["access-group"] = {
        "in": {
            "acl": {
                "acl-name": ACL_NAME,
                "in": [None]
            }
        }
    }

    # If negotiation is missing (device had it), keep whatever GET returned.
    # We're PUTting the whole object back exactly as read, plus our change.

    print(f"\nPUT {intf_url}")
    r = put(intf_url, data)
    print(f"Status: {r.status_code}")
    if r.status_code >= 300:
        print(r.text[:800])
        return

    # Confirm
    print(f"\nGET (verify) {intf_url}")
    r = get(intf_url)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        ip_after = r.json().get("Cisco-IOS-XE-native:GigabitEthernet", {}).get("ip", {})
        ag = ip_after.get("access-group", {}).get("in", {}).get("acl", {})
        print(f"  acl-name: {ag.get('acl-name')}")
        print(f"  acl in:   {ag.get('in')}")


if __name__ == "__main__":
    main()