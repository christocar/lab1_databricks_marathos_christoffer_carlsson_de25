# Marathos – Lab 1, Data Engineering

A complete data platform built in Databricks for **Marathos**, a fictive company organizing ultra-marathons around the world. The dataset covers 7.4M results from 1798 to 2023, transformed through a medallion architecture (bronze → silver → gold) and exposed via a dashboard and a natural-language interface (Genie).

> *Some parts and solutions of this project were found through help from Claude (Anthropic).*

---

## Project info

| | |
|---|---|
| **Course** | Data Engineering, Stockholms Tekniska Institut |
| **Student** | Christoffer Carlsson |
| **Class** | DE25 |
| **Lab** | Lab 1 – Databricks medallion architecture |
| **Repo** | `lab1_databricks_marathos_christoffer_carlsson_de25` |
| **Dataset** | [TWO_CENTURIES_OF_UM_RACES.csv (Kaggle)](https://www.kaggle.com/datasets/aiaiaidavid/the-big-dataset-of-ultra-marathon-running) |

---

## What the project does

Takes a raw CSV with 7.4M ultra-marathon results and turns it into:

- A clean, validated star schema in Unity Catalog
- A dashboard with KPIs, trends and geographical breakdowns
- A Genie space where stakeholders can ask questions in natural language
- A scheduled job that re-runs the full pipeline daily
- A streaming ingestion path for new event data

---

## Architecture overview

```
                    ┌──────────────────────────────┐
                    │  Raw CSV (Unity Catalog vol) │
                    └──────────────┬───────────────┘
                                   │
                       Batch  ─────┤───── Streaming (Bonus 2)
                                   │
                    ┌──────────────▼───────────────┐
                    │  BRONZE                      │
                    │  raw_results (7.4M)          │
                    │  streaming_results (50)      │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │  SILVER                      │
                    │  results_obt (6.87M, cleaned)│
                    │  dim_country (195, Bonus 1)  │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │  GOLD (star schema)          │
                    │  fct_results (6.87M)         │
                    │  dim_event (31,117)          │
                    │  dim_athlete (1.3M)          │
                    │  dim_country (195)           │
                    │  dim_date (78,616, Bonus 5)  │
                    │  8 views                     │
                    └──────────────┬───────────────┘
                                   │
                ┌──────────────────┴──────────────────┐
                ▼                                     ▼
         ┌─────────────┐                       ┌─────────────┐
         │  Dashboard  │                       │   Genie     │
         │  (Task 6)   │◄──── link ───────────►│  (Task 7)   │
         └─────────────┘                       └─────────────┘
```

---

## Repository structure

```
lab1_databricks_marathos_christoffer_carlsson_de25/
│
├── dimensional_modeling/
│   ├── schema.dbml              ← star schema in DBML
│   └── schema.png               ← rendered ER diagram
│
├── transformations/
│   ├── bronze/
│   │   ├── 01_bronze_ingest.ipynb        ← raw CSV → bronze.raw_results
│   │   └── 02_streaming_ingest.ipynb     ← Bonus 2 streaming
│   ├── silver/
│   │   ├── 01_silver_clean.ipynb         ← OBT with cleaning, IDs, dates
│   │   └── 02_dim_country.ipynb          ← IOC code mapping
│   └── gold/
│       ├── 01_dim_date.ipynb             ← Bonus 5 date dimension
│       ├── 02_gold_tables.ipynb          ← fact + dimensions
│       └── 03_views.sql                  ← 8 views, 2 per marathon type
│
├── explorations/
│   ├── 01_eda_bronze.ipynb               ← EDA on raw data
│   ├── 02_eda_silver.ipynb               ← EDA after cleaning
│   ├── 03_eda_gold.ipynb                 ← EDA on final layer
│   ├── 04_genie_validation.ipynb         ← Task 7 manual checks
│   └── 05_validations.ipynb              ← pipeline & FK validations
│
├── utils/
│   ├── constants.py                      ← all table names & paths
│   ├── io_helpers.py                     ← read/write helpers
│   ├── cleaning.py                       ← parse & filter functions
│   ├── id_generation.py                  ← dense_rank IDs
│   ├── date_parsing.py                   ← try_to_date + dim_date builder
│   └── setup_catalog.sql                 ← Unity Catalog setup
│
└── README.md                             ← you are here
```

---

## Lab requirements checklist

### Required tasks

| Task | Description | Where |
|------|-------------|-------|
| **Task 0** | Setup, onboarding, catalog structure | `utils/setup_catalog.sql` |
| **Task 1** | EDA on the raw dataset | `explorations/01_eda_bronze.ipynb` |
| **Task 2** | Bronze layer ingestion | `transformations/bronze/01_bronze_ingest.ipynb` |
| **Task 3** | Silver layer (cleaning, OBT) | `transformations/silver/01_silver_clean.ipynb` |
| **Task 4** | Dimensional modeling | `dimensional_modeling/schema.dbml` + `.png` |
| **Task 5** | Gold layer + 2 views per event type | `transformations/gold/02_gold_tables.ipynb`, `03_views.sql` |
| **Task 6** | Dashboard with KPIs, graphs, Genie link | Dashboard *"Marathos – Ultra Marathon Analytics"* in Databricks |
| **Task 7** | Genie space + manual validation | Genie *"Marathon Event Performance Analytics"* + `explorations/04_genie_validation.ipynb` |
| **Task 8** | Video presentation | Submitted separately on the learning platform |

### Bonuses (all attempted)

| Bonus | Description | Where |
|-------|-------------|-------|
| **Bonus 1** | Add country data (full name, continent) | `transformations/silver/02_dim_country.ipynb` + `country_mapping.csv` |
| **Bonus 2** | Stream new LLM-generated marathon data | `transformations/bronze/02_streaming_ingest.ipynb` |
| **Bonus 3** | Schedule the pipeline | Databricks Job *"Marathos Pipeline"*, daily 06:00 Stockholm |
| **Bonus 4** | Comprehensive dashboard with good insights | Achieved through Task 6 dashboard |
| **Bonus 5** | Date dimension table | `transformations/gold/01_dim_date.ipynb` |

---

## How to run

The full pipeline can be re-built from scratch in four steps:

1. **Set up Unity Catalog**
   ```sql
   -- Run utils/setup_catalog.sql in a SQL Editor
   ```
   This creates the `marathos` catalog with `bronze`, `silver`, `gold`, `default` schemas and a `raw` volume.

2. **Upload the source CSV**
   Drop `TWO_CENTURIES_OF_UM_RACES.csv` and `country_mapping.csv` into `/Volumes/marathos/default/raw/`.

3. **Run the notebooks in order** (or trigger the scheduled job)
   ```
   bronze_ingest → silver_clean → dim_country → dim_date → gold_tables → views
   ```

4. **Open the dashboard** and start exploring.

For convenience, all six tasks above are wired into a Databricks Job (Bonus 3) that runs them in the correct order with the right dependencies. Manual execution takes ~4 minutes on Serverless compute.

---

## Layer-by-layer design

### Bronze – raw landing zone

**What it does:** read the raw CSV and persist it as a Delta table with no transformations beyond column-mapping setup (needed because the source has columns with spaces and slashes like `Event distance/length`).

**Why no cleaning here:** bronze is intentionally a 1:1 copy of source. If a bug is discovered downstream, we can always re-derive silver and gold without going back to the original file.

**Key fact:** 7,461,195 rows.

### Silver – cleaned & enriched

**What it does:** turns raw rows into a clean **One Big Table** (OBT) ready for dimensional modeling.

Key transformations:

- Split `Event distance/length` (e.g. `"50km"`, `"6d"`, `"24h"`) into `event_value` and `event_unit`
- Split `Athlete performance` (e.g. `"4:32:11 h"`, `"112.5 km"`) into a time in seconds OR a distance in km, depending on the unit
- Classify each row into one of three **event types** based on the unit:
  - `distance` – fixed distance (km/mi), performance is a time
  - `time` – fixed time (h), performance is a distance
  - `multi_day` – multi-day races (d), performance is a distance
- Filter out invalid rows (e.g. age outside 5–100, missing performance, mismatched unit combinations)
- Normalize country codes (`DAN→DEN`, `IRE→IRL`, `SVE→SWE`, `MDG→MAD`)
- Generate stable `event_id` and `athlete_id` using `dense_rank` over deterministic keys
- Parse event dates with `try_to_date` (a small number of rows have invalid dates like `"00.03.1998"` → kept with NULL dates rather than dropped)

**Key fact:** 6,869,385 rows after cleaning (~92% retention).

### Gold – star schema

**Design choice: Kimball star schema.** A central fact table surrounded by descriptive dimensions.

Tables:

| Table | Rows | Role |
|-------|------|------|
| `fct_results` | 6,869,385 | one row per result, with FKs to all dimensions |
| `dim_event` | 31,117 | the actual race (name, distance, type) |
| `dim_athlete` | 1,299,446 | the runner (birth year, gender, country) |
| `dim_country` | 195 | IOC code → country name + continent |
| `dim_date` | 78,616 | full calendar 1807–2023 (Bonus 5) |

**Role-playing dimension:** `dim_date` is referenced twice from fact – once as `start_date_id`, once as `end_date_id`. Standard Kimball pattern for events that span dates.

**Views (Task 5 + 2 extra for the dashboard):**

```
vw_distance_top10_fastest_per_event
vw_distance_avg_time_by_age_group
vw_time_top10_longest_per_event
vw_time_avg_distance_by_age_group
vw_multiday_top10_longest
vw_multiday_results_by_country
vw_results_per_year          ← used by dashboard
vw_results_by_country        ← used by dashboard
```

---

## Notable design decisions

**Multi-day events kept, not dropped.** The lab originally suggested dropping `d` events, but after discussion with the instructor we kept them as a separate `event_type`. This makes the dataset richer and the analysis more interesting (multi-day races are uniquely fascinating – some athletes cover 2000+ km).

**`event_num_finishers` lives in fact, not in `dim_event`.** A race has different finisher counts in different years, so it's a measurement (changes per result), not a stable attribute (does not change per event).

**`event_id` is ranked on (name, distance, unit) – not name alone.** This was a *correction* discovered when building the dashboard: organizations like Sri Chinmoy run several different races under the same paraphernalia name (a 6-day race, a 1300-mile race, a 24-hour race – all called "Sri Chinmoy Ultra Trio"). Ranking on name alone collapsed them into one `event_id`, which propagated a 1300-mile distance as if it were 1300 days. Fixed by widening the dense_rank key.

**Country codes are IOC, not ISO 3166.** The dataset uses three-letter codes that mostly match ISO but with key differences (`CHI=Chile`, `RSA=South Africa`, `TPE=Chinese Taipei`). The country mapping CSV (Bonus 1) was generated specifically for IOC codes.

**Date parsing tolerates malformed values.** A few hundred rows have invalid date strings like `"00.03.1998"`. We use `try_to_date` to convert these to NULL rather than fail the whole pipeline. The validations notebook reports the exact count (0.012% of all rows).

---

## Validation strategy

Validation lives in `explorations/05_validations.ipynb` and covers three layers:

1. **Unit tests** on individual cleaning functions (parse a known input, expect a known output)
2. **Pipeline checks** on row counts and column presence
3. **Structural invariants** on the gold layer:
   - PK uniqueness in each dimension
   - FK integrity (no orphan rows in fact)
   - Cross-layer row count consistency (silver = fct_results)

All checks pass. The orphan-checks specifically verify that every `event_id`, `athlete_id`, `country_code`, `start_date_id`, and `end_date_id` in `fct_results` exists in its corresponding dimension – critical for a star schema where any orphan breaks downstream joins.

---

## Dashboard & Genie

### Dashboard

The dashboard is structured around five questions a stakeholder might ask:

| Section | Question | Widgets |
|---------|----------|---------|
| 1. Scale | How big is the dataset? | 4 KPI tiles |
| 2. Growth | How has the sport evolved? | 2 line charts |
| 3. Demographics | Who runs ultra-marathons? | 2 bar charts |
| 4. Geography | Where does it happen? | Top-15 countries + by continent |
| 5. Extremes | What are the most extreme performances? | Top-10 multi-day table |

Filters for `year` (range slider) and `event_type` (multi-select) make it interactive.

### Genie

A Genie space with the gold tables connected and instructions describing the schema and business logic (event types, IOC codes, etc).

Three sample questions were tested and **manually validated** in `04_genie_validation.ipynb`:

1. *"What is the monthly count of events held over the years?"* – Genie: 897 months, avg 93.3 events/month, peak 920. **Match: 897 / 93.26 / 920** ✓
2. *"What is the average finish time for 100km races by gender?"* – Genie: F=16.9h, M=14.9h, X=16.0h. **Match: F=16.86, M=14.93, X=15.96** ✓
3. *"Top 5 countries by longest distance in 24-hour races?"* – Genie: Lithuania (319.6), Australia (303.5), Poland (301.9), Ukraine (295.4), Italy (288.4). **All 5 match exactly** ✓

---

## Streaming pipeline (Bonus 2)

Auto Loader (`cloudFiles`) monitors `/Volumes/marathos/default/raw/streaming/` for new CSV files. The streaming notebook can be re-run on demand:

- It uses `trigger(availableNow=True)` to process pending files once and stop (suits interactive use)
- A checkpoint at `/Volumes/marathos/default/raw/_checkpoints/streaming_results/` tracks which files have already been read, so re-runs only pick up *new* files
- The target table `marathos.bronze.streaming_results` was pre-created with `delta.columnMapping.mode = 'name'` to handle the source's special characters in column names

Demo data: a 50-row CSV for a fictive *"Göteborgsvarvet Ultra 2025"* event, generated to test the pipeline.

In a production scenario, silver would consume both `raw_results` (batch) and `streaming_results` (incremental). For this lab, the streaming path is left as a standalone proof of concept.

---

## Scheduled job (Bonus 3)

The full pipeline is wired as a Databricks Job called *"Marathos Pipeline"* with six tasks and explicit dependencies:

```
bronze_ingest → silver_clean → dim_country → dim_date → gold_tables → views
```

Schedule: **daily at 06:00 Europe/Stockholm**. Manual end-to-end execution takes ~4 minutes on Serverless compute.

---

## What I learned

A few things that surprised me during the build:

- **EDA in every layer is genuinely valuable.** The Sri Chinmoy bug was caught by *visualizing* the multi-day table in the dashboard, not by reading code. Without that visualization step, I would have shipped a broken model.
- **`groupBy("athlete_id").agg(F.first(...))` saved the dimension.** A naïve `distinct()` returned ~1.4M rows; after switching to `groupBy + first`, ~1.3M. The 100k difference was the same athlete appearing with slightly different gender/country/birth-year values in different rows of the source data – classic dimension-modeling gotcha.
- **Auto Loader is surprisingly clean.** Once column mapping is configured on the target table, streaming a CSV is essentially one `readStream → writeStream` chain. The hard part is checkpoint management when something goes wrong.
- **Genie's quality depends almost entirely on the Instructions.** Without describing what `distance` vs `time` vs `multi_day` mean, it gave wrong answers on the 24-hour question. With instructions, it nailed all three test questions.

---

## Acknowledgement

This project was built as part of the Data Engineering course at Stockholms Tekniska Institut. Some implementation details and code patterns were developed with help from Claude (Anthropic) – particularly the streaming setup and the Sri Chinmoy debugging. All design decisions, validations and the architecture were made by me.