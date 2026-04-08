from api_client import (
    CITY_NAMES,
    CITY_TO_PLATE,
    PLATE_TO_CITY,
    fetch_weather_data,
)
from weather_codes import WEATHER_CODES

import pandas as pd


def get_city_or_plate(user_input):
    """Resolve a user input (city name or plate code) to city info."""
    text = user_input.strip()

    # If the input is digits, treat it as a plate code
    if text.isdigit():
        plate = f"{int(text):02d}"
        city = PLATE_TO_CITY.get(plate)
        if city is None:
            raise ValueError("Invalid plate code.")
    else:
        # Otherwise, find the city by name (case-insensitive)
        city = None
        for name in CITY_NAMES:
            if name.casefold() == text.casefold():
                city = name
                break
        if city is None:
            raise ValueError("Invalid city name.")
        plate = CITY_TO_PLATE[city]

    return {"city": city, "plate": plate}


def get_date(user_input: str):
    """Parse a day offset string like '+3', '-1', or '0'."""
    text = user_input.strip()

    if text.lstrip("+-").isdigit():
        return int(text)
    raise ValueError("Invalid input! Enter in the format +N, -N or 0.")


def get_city_day_row(city_or_plate, day_offset):
    """
    Get a single weather row for a given city and day offset.

    Pulls data from the in-memory cache via fetch_weather_data(),
    so no CSV file is required. The target date is computed from
    today + offset and looked up by date rather than by position,
    which avoids any off-by-one errors from the API's past/forecast split.
    """
    sel = get_city_or_plate(city_or_plate)
    offset = get_date(day_offset)

    # Get the full DataFrame from the cache (or fetch if expired)
    df = fetch_weather_data()

    # Filter to the chosen city
    city_df = df[df["city"] == sel["city"]].sort_values("date").reset_index(drop=True)

    # Compute the target date based on today + offset (date only, no time)
    today = pd.Timestamp.now(tz="UTC").date()
    target_date = today + pd.Timedelta(days=offset)

    # Compare dates only (ignore time and timezone)
    matching = city_df[city_df["date"].dt.date == target_date]

    if matching.empty:
        min_date = city_df["date"].min().date()
        max_date = city_df["date"].max().date()
        raise ValueError(
            f"No data for {target_date}. "
            f"Valid range: {min_date} to {max_date}."
        )

    row = matching.iloc[0]
    return {
        "city": row["city"],
        "plate": row["plate"],
        "date": row["date"].date().isoformat(),
        "weather_code": int(row["weather_code"]),
        "t_mean": float(row["temperature_2m_mean"]),
        "t_max": float(row["temperature_2m_max"]),
        "t_min": float(row["temperature_2m_min"]),
    }


def get_city_day_report(city_or_plate, day_offset):
    """Build a human-readable weather report for a city and day offset."""
    data = get_city_day_row(city_or_plate, day_offset)

    code = data["weather_code"]
    desc = WEATHER_CODES.get(code, f"Unknown code {code}")

    return (
        f"{data['city']} ({data['plate']}) – {data['date']}\n"
        f"Weather: {desc}\n"
        f"Average: {data['t_mean']:.1f}°C  |  "
        f"Min: {data['t_min']:.1f}°C  |  "
        f"Max: {data['t_max']:.1f}°C"
    )