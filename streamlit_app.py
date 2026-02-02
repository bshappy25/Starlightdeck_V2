# streamlit_app.py

import os
import streamlit as st

from utils.economy import deposit, spend, recent_txs, add_history
from utils.admin import check_admin

# -------------------------
# CONFIGURATION
# -------------------------
st.set_page_config(page_title="Starlight Deck", layout="centered")
st.title("🌌 Starlight Deck - Economy + Admin Demo")

HERE = os.path.dirname(os.path.abspath(__file__))
BANK_PATH = os.path.join(HERE, "careon_bank_v2.json")
LEDGER_PATH = os.path.join(HERE, "codes_ledger.json")

# -------------------------
# SESSION DEFAULTS
# -------------------------
st.session_state.setdefault("username", "")
st.session_state.setdefault("admin_ok", False)

# -------------------------
# USERNAME INPUT
# -------------------------
name = st.text_input("Your username", value=st.session_state["username"])
st.session_state["username"] = name.strip()

# -------------------------
# BALANCE DISPLAY
# -------------------------
bank_data = deposit(0, "Init check", BANK_PATH)  # This ensures file exists
bank = bank_data if isinstance(bank_data, dict) else {}

st.markdown(f"""
**Balance**: {bank.get("balance", 0)} Ȼ  
**Network Fund**: {bank.get("sld_network_fund", 0)} Ȼ
""")

# -------------------------
# ACTIONS
# -------------------------
st.divider()
st.subheader("💸 Deposit Careons")

amount = st.number_input("Amount to deposit", min_value=1, step=1)
note = st.text_input("Note", value="User deposit")

if st.button("Deposit"):
    if deposit(amount, note, BANK_PATH):
        st.success(f"Deposited {amount} Ȼ")
        st.rerun()
    else:
        st.error("Invalid deposit amount")

# -------------------------
# SPENDING
# -------------------------
st.subheader("🧾 Spend Careons")

spend_amount = st.number_input("Spend amount", min_value=1, step=1, key="spend_input")
spend_note = st.text_input("Reason", key="spend_note")

if st.button("Spend"):
    if spend(spend_amount, spend_note, BANK_PATH):
        st.success(f"Spent {spend_amount} Ȼ")
        st.rerun()
    else:
        st.error("Not enough funds or invalid amount.")

# -------------------------
# ADMIN PANEL
# -------------------------
st.divider()
st.subheader("🔐 Admin Access")

admin_user = st.text_input("Admin username", key="admin_user_input")
admin_pass = st.text_input("Admin password", type="password", key="admin_pw_input")

if st.button("Unlock Admin", key="admin_btn"):
    if check_admin(admin_user, admin_pass):
        st.session_state["admin_ok"] = True
        st.success("✅ Admin access granted")
        st.rerun()
    else:
        st.error("❌ Invalid credentials")

# -------------------------
# ADMIN TOOLS
# -------------------------
if st.session_state.get("admin_ok"):
    st.markdown("### 🛠️ Admin Tools")

    with st.expander("Add Manual History Entry"):
        tx_type = st.selectbox("Type", ["note", "admin", "phrase", "earn", "spend"])
        tx_note = st.text_input("Note", key="admin_tx_note")
        tx_amt = st.number_input("Amount", key="admin_tx_amt", step=1, value=0)
        if st.button("Add History Entry"):
            tx = {
                "ts": deposit.__globals__["now_z"](),  # using the shared utility
                "type": tx_type,
                "amount": tx_amt,
                "note": tx_note
            }
            add_history(tx, BANK_PATH)
            st.success("Transaction added.")
            st.rerun()

# -------------------------
# RECENT TRANSACTIONS
# -------------------------
st.divider()
st.subheader("📜 Recent Activity")
txs = recent_txs(BANK_PATH)

if not txs:
    st.info("No recent transactions.")
else:
    for tx in reversed(txs):
        ts = tx.get("ts", "???")
        typ = tx.get("type", "").upper()
        amt = tx.get("amount", 0)
        note = tx.get("note", "")
        st.markdown(f"**{ts}** — `{typ}` {amt} Ȼ — _{note}_")

# Footer
st.divider()
st.caption("Built with ❤️ and Python • v0.1 economy+security demo")