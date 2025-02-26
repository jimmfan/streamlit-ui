# uv run streamlit run src/streamlit/horizontal_dev.py
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

preselect_js = JsCode("""
function onFirstDataRendered(params) {
    params.api.forEachNode(node => node.setSelected(true));
}
""")

# Example tables for demonstration
tables = [
    {"source": "team pikachu", "process": "process name 0", "owner": "Ash"},
    {"source": "team pikachu", "process": "process name 1", "owner": "Misty"},
    {"source": "team pikachu", "process": "process name 2", "owner": "Brock"},
    {"source": "team pikachu", "process": "process name 3", "owner": "Ash"},
    {"source": "team pikachu", "process": "process name 4", "owner": "Misty"},
    {"source": "team pikachu", "process": "process name 5", "owner": "Brock"},
    {"source": "team pikachu", "process": "process name 6", "owner": "Ash"},
    {"source": "team rocket", "process": "process name 7", "owner": "James"},
    {"source": "team rocket", "process": "process name 8", "owner": "Meowth"},
    {"source": "team rocket", "process": "process name 9", "owner": "Jesse"},
    {"source": "team rocket", "process": "process name 10", "owner": "James"},
    {"source": "team rocket", "process": "process name 11", "owner": "Meowth"},
    {"source": "team rocket", "process": "process name 12", "owner": "Jesse"},
    {"source": "team rocket", "process": "process name 13", "owner": "James"},
]

st.set_page_config(page_title="Streamlit Aggrid", layout="wide")
st.title("Streamlit Aggrid")

# Initialize session state DataFrames
if "selected_df" not in st.session_state:
    st.session_state.selected_df = pd.DataFrame(tables)

if "final_df" not in st.session_state:
    st.session_state.final_df = pd.DataFrame()

# Filters
col1, col2, col3 = st.columns(3)

with col1:
    selected_sources = st.multiselect(
        "Filter by Source",
        st.session_state.selected_df["source"].unique(),
    )

with col2:
    selected_processes = st.multiselect(
        "Filter by Process",
        st.session_state.selected_df["process"].unique(),
    )

with col3:
    selected_owners = st.multiselect(
        "Filter by Owner",
        st.session_state.selected_df["owner"].unique(),
    )

# Apply filters
df_filtered = st.session_state.selected_df.copy()
if selected_sources:
    df_filtered = df_filtered[df_filtered["source"].isin(selected_sources)]
if selected_processes:
    df_filtered = df_filtered[df_filtered["process"].isin(selected_processes)]
if selected_owners:
    df_filtered = df_filtered[df_filtered["owner"].isin(selected_owners)]

# Update session state
st.session_state.selected_df = df_filtered

# Display table with AgGrid
if not df_filtered.empty:
    gb = GridOptionsBuilder.from_dataframe(df_filtered)

    gb.configure_selection(
        selection_mode="multiple", use_checkbox=True, header_checkbox=True
    )

    gb.configure_grid_options(
        domLayout="autoHeight",
        animateRows=True,
        enableSorting=True,
        enableFilter=True,
        pagination=True,
        paginationPageSize=50,
        onFirstDataRendered=preselect_js,  # Preselect checkboxes
    )

    gridOptions = gb.build()

    grid_response = AgGrid(
        df_filtered,
        gridOptions=gridOptions,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        allow_unsafe_jscode=True,
    )

    selected_rows = grid_response["selected_rows"]

    if any(selected_rows):
        st.write("Selected Rows:", selected_rows)

# Button to copy selected rows
if st.button("Copy to Final DataFrame") and any(selected_rows):
    selected_rows_df = pd.DataFrame(selected_rows)
    st.session_state.final_df = (
        pd.concat([st.session_state.final_df, selected_rows_df])
        .drop_duplicates()
        .reset_index(drop=True)
    )
    st.success("Selected rows copied successfully!")

# Display Final DataFrame
if not st.session_state.final_df.empty:
    st.subheader("Final DataFrame")

    gb_final = GridOptionsBuilder.from_dataframe(st.session_state.final_df)
    gb_final.configure_selection("multiple", use_checkbox=True, header_checkbox=True)
    gb_final.configure_grid_options(
        domLayout="autoHeight",
        animateRows=True,
        enableSorting=True,
        enableFilter=True,
        pagination=True,
        paginationPageSize=50,
        onFirstDataRendered=preselect_js,  # Preselect checkboxes for final table
    )

    grid_options_final = gb_final.build()

    grid_response_final = AgGrid(
        st.session_state.final_df,
        gridOptions=grid_options_final,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        allow_unsafe_jscode=True,
    )

    selected_rows_final = grid_response_final["selected_rows"]

    if any(selected_rows_final):
        st.write("Controls to push to API:", selected_rows_final)

        # Download button
        csv = pd.DataFrame(selected_rows_final).to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download CSV", data=csv, file_name="final_data.csv", mime="text/csv"
        )
