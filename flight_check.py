"""
ATH to BLQ cheapest flight finder (MVP, Ryanair only).

What this does:
  - Generates every valid date pair in the next 90 days based on your rules.
  - Queries Ryanair's public API for each pair (no API key needed).
  - Applies filters: direct, ATH depart >= 18:00, BLQ return >= 17:00 on Mon/Tue
    (Sunday return has no time floor).
  - Prints the cheapest round trip per calendar week.

Setup (one time):
  pip install -r requirements.txt

Run:
  python flight_check.py
"""

from datetime import date, timedelta
from ryanair import Ryanair
import time

# Config
ORIGIN = "ATH"
DESTINATION = "BLQ"
HORIZON_DAYS = 90
OUT_DAYS = {2, 3}            # Wed=2, Thu=3
RET_DAYS = {6, 0, 1}         # Sun=6, Mon=0, Tue=1
OUT_MIN_HOUR = 18            # ATH evening departure minimum
RET_MON_TUE_MIN_HOUR = 17    # Return minimum on Mon/Tue (any time on Sun)
MIN_NIGHTS = 3
MAX_NIGHTS = 5
REQUEST_DELAY_SEC = 0.3      # be polite to Ryanair's servers


def generate_pairs():
    """Build list of (outbound_date, return_date) candidates."""
    today = date.today()
    pairs = []
    for i in range(HORIZON_DAYS):
        d = today + timedelta(days=i)
        if d.weekday() in OUT_DAYS:
            for offset in range(MIN_NIGHTS, MAX_NIGHTS + 1):
                rd = d + timedelta(days=offset)
                if rd.weekday() in RET_DAYS:
                    pairs.append((d, rd))
    return pairs


def trip_passes_filters(trip, ret_date):
    """Direct route + time-of-day rules."""
    if trip.outbound.destination != DESTINATION:
        return False
    if trip.outbound.departureTime.hour < OUT_MIN_HOUR:
        return False
    if ret_date.weekday() == 6:       # Sunday, no time floor
        return True
    return trip.inbound.departureTime.hour >= RET_MON_TUE_MIN_HOUR


def find_best_trip(api, out_date, ret_date):
    """Query Ryanair for one specific (out_date, ret_date) pair."""
    try:
        trips = api.get_cheapest_return_flights(
            ORIGIN,
            out_date, out_date,
            ret_date, ret_date,
        )
    except Exception as exc:
        return None, str(exc)

    valid = [t for t in trips if trip_passes_filters(t, ret_date)]
    if not valid:
        return None, None

    best = min(valid, key=lambda t: t.totalPrice)
    return {
        "out_date": out_date,
        "ret_date": ret_date,
        "out_time": best.outbound.departureTime,
        "ret_time": best.inbound.departureTime,
        "out_flight": best.outbound.flightNumber,
        "ret_flight": best.inbound.flightNumber,
        "total": round(best.totalPrice, 2),
        "nights": (ret_date - out_date).days,
    }, None


def collapse_by_week(trips):
    """Keep only the cheapest trip per ISO week."""
    by_week = {}
    for t in trips:
        iso = t["out_date"].isocalendar()
        key = (iso.year, iso.week)
        if key not in by_week or t["total"] < by_week[key]["total"]:
            by_week[key] = t
    return [by_week[k] for k in sorted(by_week.keys())]


def print_results(week_winners):
    print("\nCheapest Ryanair round trip per week, next 90 days")
    print("Direct ATH <-> BLQ only. Evening filters applied.\n")

    header = (
        f"{'Out':<17}{'Dep':<7}{'Back':<17}{'Dep':<7}"
        f"{'EUR total':>11}{'Nights':>8}"
    )
    print(header)
    print("-" * len(header))

    for t in week_winners:
        print(
            f"{t['out_date'].strftime('%a %d %b %y'):<17}"
            f"{t['out_time'].strftime('%H:%M'):<7}"
            f"{t['ret_date'].strftime('%a %d %b %y'):<17}"
            f"{t['ret_time'].strftime('%H:%M'):<7}"
            f"{t['total']:>11.2f}"
            f"{t['nights']:>8}"
        )

    cheapest = min(week_winners, key=lambda t: t["total"])
    print(
        f"\nCheapest overall: "
        f"{cheapest['out_date'].strftime('%a %d %b')} to "
        f"{cheapest['ret_date'].strftime('%a %d %b')} "
        f"at EUR {cheapest['total']:.2f} ({cheapest['nights']} nights)"
    )


def main():
    api = Ryanair(currency="EUR")
    pairs = generate_pairs()
    print(f"Checking {len(pairs)} date combinations. This may take a few minutes.")

    trips = []
    errors = 0
    for i, (out_d, ret_d) in enumerate(pairs, 1):
        trip, err = find_best_trip(api, out_d, ret_d)
        if trip:
            trips.append(trip)
        elif err:
            errors += 1
        time.sleep(REQUEST_DELAY_SEC)
        if i % 10 == 0:
            print(f"  progress: {i}/{len(pairs)}  (matches so far: {len(trips)})")

    print(f"\nDone. {len(trips)} pairs had valid trips. {errors} errors.")
    if not trips:
        print("No results. The route or filters may be too tight, or Ryanair may be rate limiting.")
        return

    weekly = collapse_by_week(trips)
    print_results(weekly)


if __name__ == "__main__":
    main()
