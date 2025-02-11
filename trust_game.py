import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ------------------------- GOOGLE SHEETS SETUP ------------------------- #
# Load credentials and authenticate
GOOGLE_CREDENTIALS_FILE = "google_credentials.json"  # Ensure this file is in your Streamlit workspace
SHEET_NAME = "Trustgame123"  # Change this to your Google Sheet name

try:
    # Authenticate with Google Sheets
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet
    sheet = client.open(SHEET_NAME).sheet1

    # Ensure headers exist and are correct
    headers = [
        "SONA ID", "Amount Sent (A → B)", "Amount Received (B)", "Amount Returned (B → A)",
        "Amount Sent (B → A)", "Amount Received (A)", "Final Earnings (A)", "Final Earnings (B)"
    ]
    
    existing_data = sheet.get_all_values()  # Fetch all rows

    if len(existing_data) == 0:  # If sheet is empty, add headers
        sheet.append_row(headers)
    else:
        # Check if first row is correct headers; if not, update them
        if existing_data[0] != headers:
            sheet.insert_row(headers, index=1)

except Exception as e:
    st.error(f"⚠️ Google Sheets connection failed: {e}")
    st.stop()

# ------------------------- STREAMLIT APP ------------------------- #
st.title("Two-Round Trust Game with Google Sheets Storage")

# Ask for SONA ID (Unique Identifier)
sona_id = st.text_input("Enter SONA ID:", "")

if sona_id:
    # Check if SONA ID already exists in Google Sheets
    existing_ids = sheet.col_values(1)  # Fetch all SONA IDs
    if sona_id in existing_ids:
        st.error("❌ This SONA ID has already participated. Please use a different ID.")
        st.stop()

    # ------------------------- ROUND 1: Player A as Trustor ------------------------- #
    initial_amount_A = 1000  # Player A always starts with $1000
    st.write(f"### Round 1: Player A (Trustor) Starts with ${initial_amount_A}")

    # Player A automatically sends the full $1000
    amount_sent_by_A = initial_amount_A

    # Tripled amount received by Player B
    amount_received_by_B = amount_sent_by_A * 3
    st.write(f"Player B receives **${amount_received_by_B}** (tripled).")

    # Player B decides how much to return to Player A (USING SLIDER)
    amount_returned_by_B = st.slider("Player B: How much do you want to return to Player A?", 
                                     min_value=0, max_value=max(amount_received_by_B, 1), step=1)

    # Compute earnings after Round 1
    player_A_earnings = initial_amount_A - amount_sent_by_A + amount_returned_by_B
    player_B_earnings = amount_received_by_B - amount_returned_by_B

    st.write("---")  # Separator for clarity

    # ------------------------- ROUND 2: Player B as Trustor ------------------------- #
    st.write(f"### Round 2: Player B Now Becomes the Trustor")

    # Player B starts with what they kept from Round 1
    new_initial_amount_B = player_B_earnings
    st.write(f"Player B starts this round with **${new_initial_amount_B}**.")

    # Player B uses a slider to decide how much to send to Player A
    amount_sent_by_B = st.slider("Player B: How much do you want to send to Player A?", 
                                min_value=0, max_value=max(new_initial_amount_B, 1), step=1)

    # Tripled amount received by Player A
    amount_received_by_A = amount_sent_by_B * 3
    st.write(f"Player A receives **${amount_received_by_A}** (tripled).")

    # Compute final earnings after Round 2
    final_A_earnings = player_A_earnings + amount_received_by_A  # Player A receives the tripled amount
    final_B_earnings = new_initial_amount_B - amount_sent_by_B  # Player B keeps what's left

    # ------------------------- STORE DATA IN GOOGLE SHEETS ------------------------- #
    participant_data = [
        sona_id,
        amount_sent_by_A,
        amount_received_by_B,
        amount_returned_by_B,
        amount_sent_by_B,
        amount_received_by_A,
        final_A_earnings,
        final_B_earnings
    ]

    try:
        # Append the new row to Google Sheets
        sheet.append_row(participant_data)
        st.success("✅ Your responses have been recorded and saved in Google Sheets!")
    except Exception as e:
        st.error(f"⚠️ Failed to save data to Google Sheets: {e}")

    # ------------------------- SHOW FINAL RESULTS ------------------------- #
    st.write("### Final Earnings After Both Rounds")
    st.write(f"**Player A's Final Earnings:** ${final_A_earnings}")
    st.write(f"**Player B's Final Earnings:** ${final_B_earnings}")

    st.write("🎉 Thank you for participating in this two-round trust game!")
