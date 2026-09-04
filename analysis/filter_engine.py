def apply_filters(df, filters):

    filtered_df = df.copy()

    for column, value in filters.items():

        filtered_df = filtered_df[
            filtered_df[column] == value
        ]

    return filtered_df