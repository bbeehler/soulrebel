import streamlit as st
from modules import discovery

st.set_page_config(page_title="Soul Rebel StratOS", layout="wide")

def main():
    st.sidebar.title("Soul Rebel StratOS")
    st.sidebar.write("---")
    
    choice = st.sidebar.radio("Navigate Workspace", 
        ["1. The Soul Sprint", "2. Brand Guardian", "3. O2O Analytics"])

    if choice == "1. The Soul Sprint":
        discovery.run()
    elif choice == "2. Brand Guardian":
        st.title("Brand Guardian")
        st.write("Coming next: Upload copy and score it against your Brand Soul.")
    else:
        st.title("O2O Analytics")
        st.write("Coming later: Measure physical impact.")

if __name__ == "__main__":
