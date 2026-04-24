# ATH to BLQ flight checker

Finds the cheapest direct Ryanair round trips from Athens to Bologna over the next 90 days, filtered by your travel rules.

## What it does

- Checks every valid Wed/Thu outbound + Sun/Mon/Tue return combination in the next 90 days
- Filters for direct flights only
- Applies time rules: ATH departure after 18:00, BLQ return at or after 17:00 on Mon/Tue (Sunday has no time floor)
- Trip length between 3 and 5 nights
- Prints the cheapest round trip per calendar week

Ryanair only for now, no API key needed. Aegean comes in phase 2.

## Requirements

- macOS or Linux
- Python 3.9 or newer

Check Python version:

```
python3 --version
```

If missing, install from [python.org/downloads](https://www.python.org/downloads/).

## Setup (one time)

Open Terminal, navigate to the folder that contains `flight_check.py`:

```
cd ~/path/to/your/folder
```

Create a virtual environment:

```
python3 -m venv venv
```

Activate it:

```
source venv/bin/activate
```

Your prompt should now start with `(venv)`.

Install dependencies:

```
pip install -r requirements.txt
```

## Running the script

The easiest way is the bundled `flight_check` wrapper, which activates the virtual environment and runs the script for you:

```
./flight_check
```

If the wrapper is not executable, run `chmod +x flight_check` once.

Or run the steps manually:

```
cd ~/path/to/your/folder
source venv/bin/activate
python flight_check.py
```

Runtime is 2 to 4 minutes. Progress updates print every 10 date pairs.

When done, exit the virtual environment with:

```
deactivate
```

## Output

Example:

```
Out              Dep    Back             Dep     EUR total  Nights
--------------------------------------------------------------------
Wed 29 Apr 26    23:30  Mon 04 May 26    19:05       58.42       5
Thu 07 May 26    19:15  Sun 10 May 26    06:30       72.10       3
Wed 13 May 26    23:30  Mon 18 May 26    19:05       64.88       5
...

Cheapest overall: Wed 29 Apr to Mon 04 May at EUR 58.42 (5 nights)
```

One row per week, showing the cheapest valid combination.

## Configuration

Edit the top of `flight_check.py` to tweak:

- `HORIZON_DAYS`: how far ahead to search (default 90)
- `OUT_MIN_HOUR`: earliest ATH departure hour (default 18)
- `RET_MON_TUE_MIN_HOUR`: earliest BLQ return hour on Mon/Tue (default 17)
- `MIN_NIGHTS`: shortest allowed trip (default 3)
- `MAX_NIGHTS`: longest allowed trip (default 5)
- `REQUEST_DELAY_SEC`: pause between API calls (default 0.3)

## Troubleshooting

**`command not found: python3`**
Install Python from [python.org/downloads](https://www.python.org/downloads/).

**`externally-managed-environment` during pip install**
You skipped the virtual environment. Run `source venv/bin/activate` first, then retry.

**`No module named ryanair`**
The virtual environment is not active. Run `source venv/bin/activate`, then retry.

**Many errors during run**
Ryanair may be rate-limiting. Open `flight_check.py`, change `REQUEST_DELAY_SEC = 0.3` to `0.8`, save, re-run.

**Zero matches**
Time filters may be too strict, or the API returned nothing. Try lowering `OUT_MIN_HOUR` to `17` temporarily to confirm the script works, then restore.

## Notes on pricing

- Prices shown are Ryanair base fares, no seat selection, no checked bag.
- Actual checkout total will be within a few euros if you travel with cabin bag only.
- If a week shows nothing, Aegean may still have a flight. Worth a manual check on aegeanair.com for that specific week.

## Next phase (later)

- Add Aegean via Amadeus API
- Write results to a Google Sheet
- Run daily via GitHub Actions cron (no laptop needed)

## License

MIT. See [LICENSE](LICENSE).
