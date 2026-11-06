import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


api_base_url = "https://192.168.130.6/restconf/data"

basicauth = ("admin", "class")

headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}


def configure_interface(interface_config):
    """Configure via ietf-interfaces (use for GigabitEthernet / Loopback)."""
    interface_name = interface_config["ietf-interfaces:interface"]["name"]

    api_url = (
        f"{api_base_url}/ietf-interfaces:interfaces/"
        f"interface={interface_name.replace('/', '%2F')}"
    )

    print(f"\n--- {interface_name} (ietf-interfaces) ---")
    print(f"PUT {api_url}")

    try:
        resp = requests.put(
            api_url,
            json=interface_config,
            auth=basicauth,
            headers=headers,
            verify=False,
            timeout=10
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
    """Configure a Serial interface via Cisco-IOS-XE-native."""
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
            timeout=10
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
# Serial0/1/0 — JUNK to ISPN (native model, netmask)
# ------------------------------------------------------------------
configure_native_serial(
    serial_number="0/1/0",
    description="JUNK to ISPN",
    ip_address="192.168.129.2",
    netmask="255.255.255.252"
)

# ------------------------------------------------------------------
# GigabitEthernet0/0/0 — JUNK LAN (ietf-interfaces, netmask)
# ------------------------------------------------------------------
lan_config = {
    "ietf-interfaces:interface": {
        "name": "GigabitEthernet0/0/0",
        "description": "JUNK LAN",
        "type": "iana-if-type:ethernetCsmacd",
        "enabled": True,
        "ietf-ip:ipv4": {
            "address": [
                {
                    "ip": "192.168.130.1",
                    "netmask": "255.255.255.0"
                }
            ]
        }
    }
}

configure_interface(lan_config)