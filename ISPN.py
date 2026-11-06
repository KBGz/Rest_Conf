import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

api_base_url = "https://192.168.130.5/restconf/data"
basicauth = ("admin", "class")

headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}


def configure_interface(interface_config):
    """Configure an interface using the ietf-interfaces model (Loopback works here)."""
    interface_name = interface_config["ietf-interfaces:interface"]["name"]

    # URL encoding for interface name (e.g., Serial0/1/0)
    encoded_name = interface_name.replace("/", "%2F")

    api_url = f"{api_base_url}/ietf-interfaces:interfaces/interface={encoded_name}"

    print(f"\n--- {interface_name} ---")
    print(f"PUT {api_url}")

    try:
        resp = requests.put(
            api_url,
            json=interface_config,
            auth=basicauth,
            headers=headers,
            verify=False,
            timeout=15
        )

        print(f"Status: {resp.status_code}")

        if 200 <= resp.status_code < 300:
            print(f"{interface_name}: OK")
        else:
            print(f"{interface_name}: FAILED")
            print(resp.text[:800])

    except requests.RequestException as error:
        print(f"Request failed: {error}")


def configure_native_serial(serial_number, description, ip_address, netmask):
    """Configure a Serial interface via Cisco-IOS-XE-native (ietf-interfaces rejects Serial type)."""
    api_url = (
        f"{api_base_url}/Cisco-IOS-XE-native:native/interface/"
        f"Serial={serial_number.replace('/', '%2F')}"
    )

    payload = {
        "Cisco-IOS-XE-native:Serial": {
            "name": serial_number,
            "description": description,
            "ip": {
                "address": {
                    "primary": {
                        "address": ip_address,
                        "mask": netmask
                    }
                }
            }
        }
    }

    print(f"\n--- Serial{serial_number} (native) ---")
    print(f"PUT {api_url}")

    try:
        resp = requests.put(
            api_url,
            json=payload,
            auth=basicauth,
            headers=headers,
            verify=False,
            timeout=15
        )

        print(f"Status: {resp.status_code}")

        if 200 <= resp.status_code < 300:
            print(f"Serial{serial_number}: OK")
        else:
            print(f"Serial{serial_number}: FAILED")
            print(resp.text[:800])

    except requests.RequestException as error:
        print(f"Request failed: {error}")


# ------------------------------------------------------------------
# Loopback0 — via ietf-interfaces (works, returns 204)
# ------------------------------------------------------------------
loopback_config = {
    "ietf-interfaces:interface": {
        "name": "Loopback0",
        "description": "Internet",
        "type": "iana-if-type:softwareLoopback",
        "enabled": True,
        "ietf-ip:ipv4": {
            "address": [
                {
                    "ip": "192.168.128.129",
                    "netmask": "255.255.255.128"
                }
            ]
        }
    }
}

configure_interface(loopback_config)

# ------------------------------------------------------------------
# Serial0/1/0 — via Cisco-IOS-XE-native (ietf-interfaces can't do Serial)
# ------------------------------------------------------------------
configure_native_serial(
    serial_number="0/1/0",
    description="ISPN to JUNK",
    ip_address="192.168.129.1",
    netmask="255.255.255.252"
)