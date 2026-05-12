import streamlit as st
# Import the run function from discovery.py inside the modules folder
from modules import discovery

st.set_page_config(page_title="Soul Rebel StratOS", layout="wide")

# This will tell us if main.py is actually loading
st.sidebar.success("✅ Dashboard Engine Active")

def main():
    st.sidebar.title("Soul Rebel StratOS")
    st.sidebar.write("---")
    
    choice = st.sidebar.radio("Navigate Workspace", 
        ["1. The Soul Sprint", "2. Brand Guardian", "3. O2O Analytics"])

    if choice == "1. The Soul Sprint":
        discovery.run()
    elif choice == "2. Brand Guardian":
        st.title("Brand Guardian")
        st.write("Coming next...")
    else:
        st.title("O2O Analytics")
        st.write("Coming later...")

if __name__ == "__main__":
    main()