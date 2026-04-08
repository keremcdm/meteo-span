from flask import Flask, render_template, request
from utils import get_city_day_report
from api_client import CITY_NAMES, fetch_weather_data

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    """
    Main page. Handles both the initial page load (GET)
    and the form submission (POST) in a single route.
    """
    # Default values for the first page load
    report = None
    error = None
    chart_data = None
    selected_city = None
    selected_day = "0"

    if request.method == "POST":
        selected_city = request.form.get("city")
        selected_day = request.form.get("day_offset", "0")

        try:
            # Get the text report for the selected day
            report = get_city_day_report(selected_city, selected_day)

            # Get 15 days of data around today for the chart
            chart_data = build_chart_data(selected_city)

        except Exception as e:
            error = str(e)

    return render_template(
        "index.html",
        cities=CITY_NAMES,
        report=report,
        error=error,
        chart_data=chart_data,
        selected_city=selected_city,
        selected_day=selected_day,
    )


def build_chart_data(city):
    """
    Build a dict of ~15 days of temperatures (7 past + today + 7 future)
    for the given city, ready to be used by Chart.js on the frontend.
    """
    import pandas as pd

    df = fetch_weather_data()
    city_df = df[df["city"] == city].sort_values("date").reset_index(drop=True)

    # Build a 15-day window centered on today (date-only comparison)
    today = pd.Timestamp.now(tz="UTC").date()
    start_date = today - pd.Timedelta(days=7)
    end_date = today + pd.Timedelta(days=7)

    window = city_df[
        (city_df["date"].dt.date >= start_date)
        & (city_df["date"].dt.date <= end_date)
    ]

    return {
        "labels": [d.strftime("%b %d") for d in window["date"]],
        "max": window["temperature_2m_max"].round(1).tolist(),
        "min": window["temperature_2m_min"].round(1).tolist(),
        "mean": window["temperature_2m_mean"].round(1).tolist(),
    }

if __name__ == "__main__":
    app.run(debug=True)