import streamlit as st
from web3 import Web3
import json
from blockchain import get_contract, vote
from database import init_db, register_voter, get_voter, update_voter_status

# Connect to Ethereum network (using Infura for this example)
w3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/YOUR_INFURA_PROJECT_ID'))

# Initialize the database
init_db()

# Streamlit UI
st.title("Blockchain Voting System")

# Sidebar for account info and registration
st.sidebar.header("Account Information")
account = st.sidebar.text_input("Enter your Ethereum address")

if account:
    voter = get_voter(account)
    if voter:
        st.sidebar.write(f"Welcome, {voter['name']}!")
        if voter['voted']:
            st.sidebar.write("You have already voted.")
        else:
            st.sidebar.write("You are registered to vote.")
    else:
        st.sidebar.header("Register to Vote")
        name = st.sidebar.text_input("Enter your name")
        if st.sidebar.button("Register"):
            register_voter(account, name)
            st.sidebar.success("Registration successful!")

# Main content
if account and get_voter(account) and not get_voter(account)['voted']:
    st.header("Cast Your Vote")
    
    contract = get_contract(w3)
    candidate_count = contract.functions.getCandidatesCount().call()
    candidates = [contract.functions.candidates(i).call()[0] for i in range(candidate_count)]
    
    selected_candidate = st.selectbox("Choose your candidate", candidates)
    if st.button("Cast Vote"):
        try:
            tx_hash = vote(w3, contract, account, candidates.index(selected_candidate))
            update_voter_status(account, True)
            st.success(f"Vote cast successfully! Transaction hash: {tx_hash.hex()}")
        except Exception as e:
            st.error(f"Error casting vote: {str(e)}")

# Display results
st.header("Current Results")
if st.button("Refresh Results"):
    contract = get_contract(w3)
    results = {}
    for i in range(candidate_count):
        candidate = contract.functions.candidates(i).call()
        results[candidate[0]] = candidate[1]
    
    st.bar_chart(results)