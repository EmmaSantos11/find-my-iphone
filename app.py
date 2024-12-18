import streamlit as st
import os
import socket
from pyicloud_ipd import PyiCloudService
from pyicloud_ipd.exceptions import PyiCloudFailedLoginException
import googlemaps
import pandas as pd

# Google Maps API Key (replace with your own)
gmaps_api_key = 'AIzaSyDuCrw1o2Fp44LiIoxM8KLjx8t1SKG0AVU'

# Initialize Google Maps client
gmaps = googlemaps.Client(key=gmaps_api_key)

def fetch_iphone_location(icloud_email, icloud_password):
    try:
        # Log in to iCloud using the provided email and password
        api = PyiCloudService(icloud_email, icloud_password)
        st.info("Successfully logged in to iCloud.")
    except PyiCloudFailedLoginException as e:
        # Handle login failure
        st.error(f"Failed to login to iCloud: {e}")
        return f"Failed to login to iCloud: {e}", None, None, None
    except Exception as e:
        # Catch other errors
        st.error(f"An error occurred: {e}")
        return f"An error occurred: {e}", None, None, None

    # Handle Two-Factor Authentication (2FA)
    if api.requires_2fa:
        st.warning("Two-factor authentication (2FA) is required.")
        code = st.text_input("Enter the 2FA code you received on your device:")
        if st.button("Submit 2FA Code"):
            result = api.validate_2fa_code(code)
            if not result:
                return "Failed to verify 2FA code.", None, None, None
            if not api.is_trusted_session:
                api.trust_session()

    # Access the Find My iPhone service
    devices = api.devices
    iphone = None

    # Loop through the devices to find the iPhone
    for device in devices:
        if 'iPhone' in device.get('deviceDisplayName', ''):
            iphone = device
            break

    if iphone:
        location = iphone.location()
        if location:
            latitude = location.get('latitude')
            longitude = location.get('longitude')
            serial_number = iphone.get('serialNumber', 'N/A')
            imei_number = iphone.get('imei', 'N/A')
            return None, (latitude, longitude), serial_number, imei_number
        else:
            return "Location services are turned off or the iPhone is offline.", None, None, None
    else:
        return "iPhone not found.", None, None, None

def main():
    st.title("iPhone Locator")

    st.sidebar.header("User Input")

    # Input fields for iCloud
    icloud_email = st.sidebar.text_input("iCloud Email")
    icloud_password = st.sidebar.text_input("iCloud Password", type="password")

    if st.sidebar.button("Locate iPhone"):
        if icloud_email and icloud_password:
            error_msg, location, serial_number, imei_number = fetch_iphone_location(icloud_email, icloud_password)

            if error_msg:
                st.error(error_msg)
            else:
                st.write(f"### iPhone Details")
                st.write(f"**Serial Number:** {serial_number}")
                st.write(f"**IMEI Number:** {imei_number}")

                if location:
                    st.write(f"### Location:")
                    st.write(f"**Latitude:** {location[0]}")
                    st.write(f"**Longitude:** {location[1]}")
                    
                    # Create a map to display the location
                    location_df = pd.DataFrame({'lat': [location[0]], 'lon': [location[1]]})
                    st.map(location_df)

                    # Show Google Maps link
                    map_url = f"https://www.google.com/maps?q={location[0]},{location[1]}"
                    st.markdown(f"[View on Google Maps]({map_url})")
                else:
                    st.write("Unable to retrieve location.")
        else:
            st.error("Please enter both iCloud Email and Password.")

if __name__ == "__main__":
    main()
