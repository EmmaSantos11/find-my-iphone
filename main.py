import os
import socket
from pyicloud_ipd import PyiCloudService
from pyicloud_ipd.exceptions import PyiCloudFailedLoginException
import logging

logging.basicConfig(level=logging.DEBUG)

def test_dns(hostname):
    try:
        ip = socket.gethostbyname(hostname)
        print(f"{hostname} resolved to {ip}")
    except socket.gaierror:
        print(f"DNS resolution failed for {hostname}")

def fetch_iphone_location(icloud_email, icloud_password):
    try:
        api = PyiCloudService(icloud_email, icloud_password)
    except PyiCloudFailedLoginException as e:
        print("Failed to login to iCloud:", e)
        return None
    except Exception as e:
        print("An error occurred:", e)
        return None

    # Handle Two-Factor Authentication
    if api.requires_2fa:
        print("Two-factor authentication is required.")
        code = input("Enter the 2FA code you received on your device: ")
        result = api.validate_2fa_code(code)
        print("Code validation result:", result)
        if not result:
            print("Failed to verify 2FA code.")
            return None
        if not api.is_trusted_session:
            print("Session is not trusted. Requesting trust...")
            api.trust_session()
            print("Session trusted.")
    
    # Access the Find My iPhone service
    devices = api.devices
    iphone = None

    # Find the device you're looking for (by name or model)
    for device in devices:
        if 'iPhone' in device.get('deviceDisplayName', ''):
            iphone = device
            break

    if iphone:
        # Get the location of the iPhone
        location = iphone.location()
        if location:
            latitude = location.get('latitude')
            longitude = location.get('longitude')
            return latitude, longitude
        else:
            print("Location services are turned off or the iPhone is offline.")
            return None
    else:
        print("iPhone not found.")
        return None

# Example usage:
icloud_email = 'your_email@example.com'
icloud_password = 'your_password'
location = fetch_iphone_location(icloud_email, icloud_password)
print(location)
