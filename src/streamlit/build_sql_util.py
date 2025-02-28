def build_where_clause(filter_values):
    conditions = []
    for col_name, vals in filter_values.items():
        if vals:
            # Escape or quote carefully if doing raw strings
            escaped_vals = ", ".join([v for v in vals])
            conditions.append(f"{col_name} IN ({escaped_vals})")

    where_clause = " AND ".join(conditions)
    if where_clause:
        where_clause = "WHERE " + where_clause

    return where_clause
