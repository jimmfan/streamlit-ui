# uv run streamlit run src/streamlit/horizontal_layout.py

import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode


delete_button_js = JsCode("""
    class DeleteButtonRenderer {
        init(params) {
            this.params = params;
            this.eGui = document.createElement('div');
            this.eGui.innerHTML = '<button style="color: red; cursor: pointer;">❌</button>';
            this.eGui.querySelector('button').addEventListener('click', () => {
                const deletedID = params.data.ID;  // Capture deleted row ID
                params.api.applyTransaction({ remove: [params.data] });  // Remove from UI

                // Send deletion info to Streamlit backend
                fetch("/_stcore/_st_query_params?delete_event=" + deletedID, {method: "POST"});
            });
        }
        getGui() {
            return this.eGui;
        }
    }
""")

# JavaScript code for row drag and drop
onRowDragEnd = JsCode("""
function onRowDragEnd(e) {
    console.log('Row dragged', e);
}
""")

getRowNodeId = JsCode("""
function getRowNodeId(data) {
    return data.id;
}
""")

onGridReady = JsCode("""
function onGridReady() {
    gridOptions.api.forEachNode(function(node, index) {
        node.data.id = index;
    });
    gridOptions.api.setRowData(gridOptions.rowData);
}
""")

# onGridReady = JsCode("""
# function onGridReady() {
#     immutableStore.forEach(function(data, index) {
#         data.id = index;
#     });
#     gridOptions.api.setRowData(immuatableStore);
# }
# """)


onRowDragMove = JsCode("""
function onRowDragMove(event) {
    var movingNode = event.node;
    var overNode = event.overNode;
    var rowNeedsToMove = movingNode !== overNode;

    if (rowNeedsToMove) {
        var movingData = movingNode.data;
        var overData = overNode.data;
        var fromIndex = gridOptions.rowData.indexOf(movingData);
        var toIndex = gridOptions.rowData.indexOf(overData);

        gridOptions.rowData.splice(fromIndex, 1);
        gridOptions.rowData.splice(toIndex, 0, movingData);

        gridOptions.api.setRowData(gridOptions.rowData);
        gridOptions.api.clearFocusedCell();
    }
}
""")

# Example tables for demonstration
tables = {
    "table1": {
        "id": {i: i + 1 for i in range(0, 5)},
        "process": {i: f"process name {i + 1}" for i in range(0, 5)},
        "owner": {i: f"owner name {i + 1}" for i in range(0, 5)},
    },
    "table2": {
        "id": {i: i + 1 for i in range(0, 5)},
        "process": {i: f"process name {i + 1}" for i in range(0, 5)},
        "owner": {i: f"owner name {i + 1}" for i in range(0, 5)},
    },
}

st.set_page_config(page_title="Streamlit Aggrid", layout="wide")
st.title("Streamlit Aggrid")

# Initialize session state DataFrames if they do not exist
if "selected_df" not in st.session_state:
    st.session_state.selected_df = pd.DataFrame()

if "final_df" not in st.session_state:
    st.session_state.final_df = pd.DataFrame()

# Create three columns for the table selection and filters
col1, col2, col3 = st.columns(3)

with col1:
    selected_table = st.selectbox("Select a Table", list(tables.keys()))
    if selected_table:
        # Load selected table into session state
        st.session_state.selected_df = pd.DataFrame(tables[selected_table])

with col2:
    # Only show filter options if a table has been loaded
    if not st.session_state.selected_df.empty:
        selected_column = st.selectbox(
            "Select a Column to Filter", st.session_state.selected_df.columns
        )

with col3:
    if not st.session_state.selected_df.empty and "selected_column" in locals():
        selected_values = st.multiselect(
            "Select Values to Filter",
            st.session_state.selected_df[selected_column].unique(),
        )

# Apply the filter if selections were made
if (
    not st.session_state.selected_df.empty
    and "selected_column" in locals()
    and selected_values
):
    st.session_state.selected_df = st.session_state.selected_df[
        st.session_state.selected_df[selected_column].isin(selected_values)
    ]

st.write("Filtered DataFrame:")
st.dataframe(st.session_state.selected_df)

if selected_column and selected_values:
    st.session_state.selected_df = st.session_state.selected_df[
        st.session_state.selected_df[selected_column].isin(selected_values)
    ]

    # Configure grid options
    gb = GridOptionsBuilder.from_dataframe(st.session_state.selected_df)

    editable_columns = st.session_state.selected_df.columns
    gb.configure_columns(editable_columns, editable=True)
    gb.configure_column(" ", cellRenderer=delete_button_js, width=5, pinned="left")

    gb.configure_columns(
        st.session_state.selected_df.columns[0], rowDrag=True, width=60
    )

    # gb.configure_default_column(rowDrag=True, rowDragManaged=True)
    gb.configure_grid_options(
        rowDragManaged=True,
        onRowDragEnd=onRowDragEnd,
        deltaRowDataMode=True,
        getRowNodeId=getRowNodeId,
        onGridReady=onGridReady,
        onRowDragMove=onRowDragMove,
        animateRows=True,
    )
    gridOptions = gb.build()

    # Display the grid
    grid_response = AgGrid(
        st.session_state.selected_df,
        gridOptions=gridOptions,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        allow_unsafe_jscode=True,
    )

    # # Updated DataFrame after reordering
    # updated_df = grid_response['data']
    # st.write(updated_df)

# Button to copy selected rows to final dataframe
if st.button("Copy to Final DataFrame"):
    if not st.session_state.selected_df.empty:
        st.session_state.final_df = (
            pd.concat([st.session_state.final_df, st.session_state.selected_df])
            .drop_duplicates()
            .reset_index(drop=True)
        )
        st.success("Rows copied successfully!")
    else:
        st.warning("No rows selected!")

    # Display the second AgGrid (Final Table)
    st.subheader("Final DataFrame")
    gb_final = GridOptionsBuilder.from_dataframe(st.session_state.final_df)
    gb_final.configure_selection(
        "multiple", use_checkbox=True
    )  # Allow selection if needed

    editable_columns_final = st.session_state.final_df.columns
    gb_final.configure_columns(editable_columns_final, editable=True)
    gb_final.configure_column(
        " ", cellRenderer=delete_button_js, width=5, pinned="left"
    )

    gb_final.configure_columns(
        st.session_state.final_df.columns[0], rowDrag=True, width=60
    )

    # gb.configure_default_column(rowDrag=True, rowDragManaged=True)
    gb_final.configure_grid_options(
        rowDragManaged=True,
        onRowDragEnd=onRowDragEnd,
        deltaRowDataMode=True,
        getRowNodeId=getRowNodeId,
        onGridReady=onGridReady,
        onRowDragMove=onRowDragMove,
        animateRows=True,
    )

    grid_options_final = gb_final.build()

    AgGrid(
        st.session_state.final_df,
        gridOptions=grid_options_final,
        update_mode=GridUpdateMode.NO_UPDATE,  # No selection updates required here
        allow_unsafe_jscode=True,
    )

    # JavaScript listener to send delete event back to Streamlit
    st.write(
        """
    <script>
        window.addEventListener('delete_row', function(event) {
            var rowID = event.detail;
            fetch("/_stcore/_st_query_params?delete_event=" + rowID, {method: "POST"});
        });
    </script>
    """,
        unsafe_allow_html=True,
    )
