# ihealth — Apple Health

Read the user's Apple Health / HealthKit data — sleep, heart rate, HRV, activity, overnight vitals, gait — pulled off the Watch and iPhone. **One access method, no auth:** an iPhone app (Health Auto Export) writes one JSON file per day into an iCloud container that syncs down to this Mac. Reading it is a plain local file read — no token, no server, no permission prompt.

| Method | Reaches | Auth | Status |
|---|---|---|---|
| **Local — daily JSON drop** | every HealthKit metric the Watch/iPhone records, one file per day | none — plain file read from the synced iCloud container | **✅ working** |

**Prerequisite (one-time, reproducible).** The daily drop only exists once the *Health Auto Export* iPhone app + an iOS Shortcut automation are set up per the runbook in [[WIRE Health Auto Export]] — a paid app and ~10 min of config, not a personal hack; a fresh person can stand it up from that page. Once wired it is **zero-touch** (one file/day, no expiring token), which is why it reads more reliably than the weekly-re-auth Google cards. There is no cloud/API fallback and none is needed — the file is already local by the time you read it. Read-shape and the traps that cost a mistake live in [[Lumen Data Sources]] § Health.

## Where the data lives

```
~/Library/Mobile Documents/iCloud~com~ifunography~HealthExport/Documents/New Automation/
    HealthAutoExport-YYYY-MM-DD.json    # one per day, all HealthKit metrics, 300–750 KB
```

Top-level shape: `data.metrics[]` — each entry a group with `name`, `units`, and a `data[]` array of points. **`data` holds only `metrics`** — there is no sibling `workouts` key (verified across 25 files, 2026-08-05).

**Durable archive (prefer this for history).** The container above is a rolling **~26-day** window — older days age off and are gone. They are now mirrored into a permanent, git-versioned vault archive at `~/ob/kmr/Topic/MED/MED Data/Apple/`: `raw/` holds the daily JSON verbatim (the full window and everything already captured before it rolled), and `series/daily-long.csv` + `daily.csv` give one aggregated row per day for trends. For anything beyond the last ~26 days, or for a ready-made time series, read the archive — not the container. Refresh it with `MED Data/bin/sync-apple-health.sh` then `build-series.py`. Full design: [[MED Data]].

## How to read it

Load the file, walk `data.metrics[]` matching on `name`, then read `data[]` inside the matched group:

- **Daily-summary metrics** (`resting_heart_rate`, `heart_rate_variability`, …) put the value at `data[0].qty`.
- **`sleep_analysis`** puts its named fields directly on `data[0]` — `totalSleep`, `deep`, `core`, `rem`, `awake`, `inBed`, `sleepStart`, `sleepEnd`.
- **`heart_rate`** points carry `Min`/`Avg`/`Max` (not `qty`), ~240 points/day.
- **A time series** (resting HR over N days, sleep trend) = walk one file per date and pull `data[0]` from each.

## Four traps before trusting a number

- **Files are rewritten, not append-only.** A given day's file can change mtime and contents after the fact (the 08-03 and 08-04 files once shared an 08-04 17:08 mtime). Re-pull rather than caching a value.
- **Today's file does not exist until the export runs** (~08:00 for the prior day). The newest *complete* day is normally yesterday — never report "no data" for today as if it meant zero activity.
- **No `workouts` key.** If workouts matter, they are not here; do not assume a sibling array.
- **Metric count drifts** ~25–27 groups day-to-day depending on what the Watch recorded — match by `name`, never by position.

## What's in a file (25–27 groups)

| Domain | Groups |
|---|---|
| **Heart** | `resting_heart_rate`, `heart_rate` (Min/Avg/Max, ~240/day), `heart_rate_variability`, `walking_heart_rate_average` |
| **Sleep** | `sleep_analysis` (one record/night), `respiratory_rate`, `blood_oxygen_saturation`, `apple_sleeping_wrist_temperature`, `breathing_disturbances` |
| **Activity** | `step_count`, `walking_running_distance`, `active_energy`, `basal_energy_burned`, `apple_exercise_time`, `apple_stand_hour`, `apple_stand_time`, `flights_climbed`, `physical_effort` |
| **Gait / mobility** | `walking_speed`, `walking_step_length`, `walking_double_support_percentage`, `stair_speed_up`, `stair_speed_down` |
| **Environment** | `time_in_daylight`, `environmental_audio_exposure` |

## Recipes

**Resting-HR (or any daily-summary) series over the whole window:**

```
cd ~/Library/Mobile\ Documents/iCloud~com~ifunography~HealthExport/Documents/New\ Automation/
python3 - <<'PY'
import json, glob
for fp in sorted(glob.glob("HealthAutoExport-2026-*.json")):
    date = fp.replace("HealthAutoExport-","").replace(".json","")
    with open(fp) as f: d = json.load(f)
    g = next((m for m in d["data"]["metrics"] if m["name"]=="resting_heart_rate"), None)
    if g and g["data"]:
        print(date, g["data"][0]["qty"])
PY
```

Swap `resting_heart_rate` for any daily-summary group name. For `sleep_analysis`, read `data[0]["totalSleep"]`/`["deep"]`/etc.; for `heart_rate`, aggregate the `Avg` field across points.

**List every metric present in the newest file** (when you need to know what's recordable): load the newest file and print `[m["name"] for m in d["data"]["metrics"]]`.

## When to reach for this

Sleep gaps, recovery tracking, post-procedure heart-rate trends, activity/exercise questions, any "what do my vitals show" question — anything the Watch measures. It is the primary source behind [[MED]] recovery tracking and Lumen's morning health read. **Prefer this over asking the user** — the machine already has 25 days of it on disk.
