# Geospatial Processing for NC Wastewater PatRN Project

## Initial setup

### Main software

Install GRASS GIS 7.8. It is needed for all processing except the daily COVID
cases table which just needs pure Python.

For the rnoaa-based precipitation data retrieval, R is needed.

### Extensions

Install extensions, e.g., from command line:

```
g.extension v.db.pyupdate
g.extension v.vect.stats.multi
```

To deal with CSV files easily, install also:

```
g.extension m.csv.clean
g.extension v.in.csv
```

v.out.keplergl module is not in addons yet, so you need to take the script manually
from a GitHub repo and specify path to it when you want to run it.
The script is in this repo: <https://github.com/ncsu-geoforall-lab/v.out.keplergl/>.
This is optional dependency for visualization (and publishing).

The rnoaa-based workflow requires R package `rnoaa`.

## Workflows

### Flow within a sewershed

See the file `travel_time_workflow.sh` for individual steps to do in GRASS GIS.
The file shows that most steps can be done running modules or scripts in command line.

The scripts behave like GRASS GIS modules in the sense that in command line
you can add `--help` and get basic usage instructions
(you can also view the code for complete, but less readable version of that).
Adding `--ui` in the command line makes GUI for the script appear
which might be good especially for the first-time exploration of the script.

### Convert daily COVID data to one table

Use the following command to execute the script:

```
python daily_cases_for_day_zip.py nc-covid-data/zip_level_data/time_series_data/csv/
```

where `python` is whatever path or way you use to run Python scripts,
`daily_cases_for_day_zip.py` is the path to the script, and
`nc-covid-data/zip_level_data/time_series_data/csv/` is the path to the directory with
WRAL Data Desk CSV files from <https://github.com/wraldata/nc-covid-data>.

The resulting CSV table looks something like this:

date | zip_code_27101 | zip_code_27102 | zip_code_27103 | ... |
--- | --- | --- | --- | --- |
2020-05-01 | 3 | 4 | 3 | ... |
2020-05-02 | 1 | 5 | 8 | ... |

To compute cases proportional to sewershed population, a separate CSV file
with ZIP code - proportion pairs as rows can be specified:

```
python daily_cases_for_day_zip.py nc-covid-data/... --proportions data/proportions.csv
```

This also results in the output table containing only the ZIP codes with specified
proportion, i.e., filtering out ZIP codes not specified in the file.

### Precipitation

#### Sewersheds precipitation as mean of contained weather stations

This workflow assumes you have vector points with precipitation for each day (or time)
in attribute columns and that you have sewersheds a vector areas (polygons).
The workflow is captured in the file `precipitation_mean_workflow.sh`.

The core of this workflow is newly developed *v.vect.stats.multi*.
The workflow could be simplified by employing *v.in.csv* used in the
other precipitation workflow for import.

The resulting CSV looks something like this:

id/name... | date_2020_05_15 | date_2020_05_16 | ...
--- | --- | --- | ---
Sewershed ABC | 15.2 | 0 | ...

#### Sewersheds precipitation using rnoaa

This workflow is based on `WWTPclimdata.R` script from
<https://github.com/wiesnerfriedman/NCpathUNC>
imports the data into a GRASS GIS location. The workflow is in `precipitation_noaa.sh`.
