import pandas as pd
import streamlit as st
import time
from fuzzywuzzy import fuzz  # <-- fuzzy matching

# --- Configuración inicial ---
st.set_page_config(page_title="AI Judge", layout="wide")
st.title("🤖 AI Judge: Is This Action Already Covered?")

# --- Sidebar para personalizar la acción ---
with st.sidebar:
    st.header("🔧 Customize Action")
    name = st.text_input("Action Name", value="Replace Hydraulic Filter")
    freq = st.selectbox("Frequency", ["3 months", "6 months", "12 months"], index=1)
    type_ = st.selectbox("Type", ["PDM", "CM", "PVM", "FF"], index=0)
    use_fuzzy = st.checkbox("Use fuzzy match for description?", value=False)

# --- Acción definida por el usuario ---
action = {
    "ID": "A-103",
    "Name": name,
    "Frequency": freq,
    "Type": type_
}

# --- PMs de ejemplo ---
mnt_plans = [
    {"ID": "PM-1001", "Description": "Replace Filter", "Frequency": "12 months", "Type": "PDM"},
    {"ID": "PM-2002", "Description": "Clean Hydraulic System", "Frequency": "6 months", "Type": "CM"},
    {"ID": "PM-3003", "Description": "Replace Hydraulic Filter", "Frequency": "6 months", "Type": "PDM"},
]

# --- Evaluación IA ---
def evaluate_match(pm, action, use_fuzzy=False):
    # Descripción
    if use_fuzzy:
        ratio = fuzz.token_set_ratio(pm["Description"].lower(), action["Name"].lower())
        if ratio >= 90:
            description_match = "✅"
        elif ratio >= 60:
            description_match = "⚠️"
        else:
            description_match = "❌"
    else:
        description_match = "✅" if pm["Description"].lower() == action["Name"].lower() else "⚠️" if action["Name"].lower() in pm["Description"].lower() else "❌"

    # Frecuencia
    frequency_match = "✅" if pm["Frequency"] == action["Frequency"] else "❌"

    # Tipo
    type_match = "✅" if pm["Type"] == action["Type"] else "❌"

    # Resultado final
    score = sum(x == "✅" for x in [description_match, frequency_match, type_match])
    if score == 3:
        result = "Perfect ✅"
    elif score == 2:
        result = "Likely ⚠️"
    else:
        result = "Mismatch ❌"

    return {
        "PM ID": pm["ID"],
        "Description Match": description_match,
        "Frequency Match": frequency_match,
        "Type Match": type_match,
        "Result": result
    }

# --- Spinner y evaluación simulada ---
with st.spinner("🤖 Thinking... evaluating possible matches..."):
    time.sleep(2)
    results = [evaluate_match(pm, action, use_fuzzy=use_fuzzy) for pm in mnt_plans]

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["🛠 Action", "📘 Maintenance Plans", "📊 AI Evaluation"])

with tab1:
    st.subheader("Proposed Action")
    st.table(pd.DataFrame([action]))

with tab2:
    st.subheader("Existing Maintenance Plans")
    st.table(pd.DataFrame(mnt_plans))

with tab3:
    st.subheader("AI Evaluation Results")

    df_results = pd.DataFrame(results)
    st.dataframe(
        df_results.style.applymap(
            lambda v: 'color: green' if '✅' in v else ('color: orange' if '⚠️' in v else 'color: red'),
            subset=["Description Match", "Frequency Match", "Type Match", "Result"]
        )
    )

    chosen = next((r for r in results if r["Result"].startswith("Perfect")), None)

    with st.chat_message("assistant"):
        if chosen:
            st.markdown(f"🎯 I believe **PM {chosen['PM ID']}** already covers this action. It's a **Perfect Match**.")
        else:
            st.markdown("⚠️ None of the plans perfectly match the action. Consider creating a new Maintenance Plan.")

# --- Explicación IA ---
with st.expander("ℹ️ How does the AI Judge work?"):
    st.markdown("""
    The AI evaluates each Maintenance Plan based on three criteria:

    - **Description**: 
      - Exact match (✅), partial match (⚠️), or no match (❌).
      - If *fuzzy matching* is enabled, it uses similarity ratio (e.g. >=90% = ✅).
    - **Frequency**: Recurrence of the action.
    - **Type**: Nature of the maintenance (PDM, CM, etc.).

    The final result:
    - ✅ **Perfect**: All 3 match
    - ⚠️ **Likely**: 2 match
    - ❌ **Mismatch**: 1 or none match
    """)
