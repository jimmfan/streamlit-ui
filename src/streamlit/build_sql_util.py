def build_where_clause(filter_values):
    """
    Given a dict like:
        filter_values = {
            "source": ["team rocket", "team pikachu"],
            "process": ["process name 1"],
            "owner": []
        }
    return (where_clause, params) such that
        where_clause = "WHERE source IN (%s,%s) AND process IN (%s)"
        params = ["team rocket", "team pikachu", "process name 1"]
    """
    conditions = []
    params = []

    for col_name, selected_values in filter_values.items():
        # Skip if no values selected
        if selected_values:
            # e.g. for 2 values -> placeholders = '%s,%s'
            placeholders = ",".join(["%s"] * len(selected_values))
            condition = f"{col_name} IN ({placeholders})"

            conditions.append(condition)

            # Add these values to the parameter list
            params.extend(selected_values)

    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)
    else:
        where_clause = ""  # No conditions applied

    return where_clause, params


# Example usage:
filter_values = {
    "source": ["team rocket", "team pikachu"],
    "process": ["process name 1"],
    "owner": [],
}

where_clause, params = build_where_clause(filter_values)

base_query = "SELECT * FROM my_table"
query = f"{base_query} {where_clause}"

# Print or log:
print("QUERY:", query)
print("PARAMS:", params)
