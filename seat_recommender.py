from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans


TABLE_COUNT = 6
MAX_GUESTS_PER_TABLE = 10

INPUT_CSV = "guests.csv"
OUTPUT_CSV = "seating_recommendations.csv"


def _parse_weight(value: object, column_name: str) -> float:
    if pd.isna(value):
        raise ValueError(f"Empty value in '{column_name}'.")
    normalized = str(value).strip().replace(",", ".")
    try:
        return float(normalized)
    except ValueError as exc:
        raise ValueError(
            f"Cannot parse weight '{value}' in '{column_name}'."
        ) from exc


def _encode_side(value: object) -> int:
    normalized = str(value).strip().lower()
    if normalized == "невеста":
        return 0
    if normalized == "жених":
        return 1
    raise ValueError(f"Unsupported side value: '{value}'. Expected 'Невеста' or 'Жених'.")


def _encode_alcohol(value: object) -> int:
    normalized = str(value).strip().upper()
    if normalized == "TRUE":
        return 1
    if normalized == "FALSE":
        return 0
    raise ValueError(f"Unsupported alcohol value: '{value}'. Expected TRUE or FALSE.")


def _validate_global_settings(guest_count: int) -> None:
    if TABLE_COUNT <= 0:
        raise ValueError("TABLE_COUNT must be > 0.")
    if MAX_GUESTS_PER_TABLE <= 0:
        raise ValueError("MAX_GUESTS_PER_TABLE must be > 0.")
    total_capacity = TABLE_COUNT * MAX_GUESTS_PER_TABLE
    if total_capacity < guest_count:
        raise ValueError(
            f"Not enough seats: TABLE_COUNT * MAX_GUESTS_PER_TABLE = {total_capacity}, "
            f"but guests = {guest_count}."
        )


def _build_weighted_features(df: pd.DataFrame) -> np.ndarray:
    required_columns = [
        "age",
        "side",
        "alcohol",
        "age_weight",
        "side_weight",
        "alcohol_weight",
    ]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    age = pd.to_numeric(df["age"], errors="raise").astype(float)
    side_encoded = df["side"].map(_encode_side).astype(float)
    alcohol_encoded = df["alcohol"].map(_encode_alcohol).astype(float)

    age_weight = df["age_weight"].map(lambda x: _parse_weight(x, "age_weight"))
    side_weight = df["side_weight"].map(lambda x: _parse_weight(x, "side_weight"))
    alcohol_weight = df["alcohol_weight"].map(lambda x: _parse_weight(x, "alcohol_weight"))

    features = np.column_stack(
        [
            age * age_weight,
            side_encoded * side_weight,
            alcohol_encoded * alcohol_weight,
        ]
    )
    return features


def _assign_tables_with_capacity(features: np.ndarray) -> np.ndarray:
    kmeans = KMeans(n_clusters=TABLE_COUNT, random_state=42, n_init=10)
    kmeans.fit(features)

    distances = kmeans.transform(features)
    table_counts = np.zeros(TABLE_COUNT, dtype=int)
    assigned_tables = np.full(features.shape[0], -1, dtype=int)

    for guest_idx in range(features.shape[0]):
        preferred_tables = np.argsort(distances[guest_idx])
        for table_idx in preferred_tables:
            if table_counts[table_idx] < MAX_GUESTS_PER_TABLE:
                assigned_tables[guest_idx] = table_idx + 1
                table_counts[table_idx] += 1
                break

        if assigned_tables[guest_idx] == -1:
            raise RuntimeError("Failed to assign a guest to any table despite validated capacity.")

    return assigned_tables


def main() -> None:
    input_path = Path(INPUT_CSV)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path.resolve()}")

    df = pd.read_csv(input_path)
    _validate_global_settings(len(df))
    features = _build_weighted_features(df)
    df["recommended_table"] = _assign_tables_with_capacity(features)

    output_path = Path(OUTPUT_CSV)
    df.to_csv(output_path, index=False)

if __name__ == "__main__":
    main()
