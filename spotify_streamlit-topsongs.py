import streamlit as st
import requests
import json
import time

# gets the access token needed for spotify api calss
def getAccessToken():
    headers = {
    "Content-Type" : "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type":"client_credentials",
        "client_id": st.secrets["client_id"],
        "client_secret": st.secrets["client_secret"]
    }

    response = requests.post("https://accounts.spotify.com/api/token",headers=headers, data=data)

    if response.status_code in [200,201]:
        print("success")
        print(json.dumps(response.json(),indent=4))
        print(response.json()["access_token"])
        return response.json()["access_token"]
    else:
        print(f"error {response.status_code} with error: {response.text}")
        return None

# columns
col1, col2, col3 = st.columns([1,3,1])

col2.markdown("# Spotify top songs")

artistName = col2.text_input("Find top songs by artist")

# session state - for keeping variables in memory
if "access_token" not in st.session_state:
    st.session_state["access_token"] = getAccessToken()

if col2.button("GO"):
    if artistName == "":
        col2.error("Enter artist name first!")
    else:
       with col2.status("Contacting Spotify API..."):
            progressBar = col2.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progressBar.progress(i + 1)
            headers = {
            "Authorization": f"Bearer {st.session_state['access_token']}"
            }
            response = requests.get(f'https://api.spotify.com/v1/search?q={artistName}&type=artist&limit=1',headers=headers)
            if response.status_code in [200,201]:  
                artistId = response.json()["artists"]["items"][0]["id"]

                # get top songs
                response = requests.get(f"https://api.spotify.com/v1/artists/{artistId}/top-tracks",headers=headers)

                if response.status_code in [200,201]:
                    print("success")
                    print(json.dumps(response.json(),indent=4))
                    col2.success("sucessfully got top tracks!")
                    with col2.expander("click to see all tracks"):
                        for track in response.json()["tracks"]:
                            st.link_button(url=f"{track['external_urls']['spotify']}", label=f"{track['name']}")
                else:
                    print(f"error {response.status_code} with error: {response.text}")

            elif response.status_code == 401:
                st.error("your access token is expired this time, try again!")
                del st.session_state["access_token"]
            else:
                print(f"error {response.status_code} with error: {response.text}")
                st.error(f"error {response.status_code} with error: {response.text}")
