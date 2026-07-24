def profile_data(df):
    profile = {}

    profile["rows"] = df.shape[0]
    profile["columns"] = df.shape[1]
    profile["column_names"] = list(df.columns)
    profile["data_types"] = df.dtypes.astype(str).to_dict()
    profile["missing_values"] = df.isnull().sum().to_dict()
    profile["duplicate_rows"] = int(df.duplicated().sum())
    profile["unique_values"] = df.nunique().to_dict()
    # Numeric column statistics
    profile["numeric_summary"] = (
    df.describe()
    .to_dict()
)

# Sample rows
    profile["sample_rows"] = df.head(5).to_dict(orient="records")

# Memory usage
    profile["memory_usage_mb"] = round(
    df.memory_usage(deep=True).sum() / (1024 ** 2), 2
)


    return profile