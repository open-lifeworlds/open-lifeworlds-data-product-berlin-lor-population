import copy
import json
import os
import statistics as stats

import pandas as pd

from lib.tracking_decorator import TrackingDecorator

key_figure_group = "berlin-lor-population"

statistic_t1_properties = [
    "inhabitants",
    "inhabitants_with_migration_background",
    "inhabitants_germans",
    "inhabitants_germans_without_migration_background",
    "inhabitants_germans_with_migration_background",
    "inhabitants_foreigners"
]

statistic_t2_properties = [
    "inhabitants_age_below_6",
    "inhabitants_age_6_15",
    "inhabitants_age_15_18",
    "inhabitants_age_18_27",
    "inhabitants_age_27_45",
    "inhabitants_age_45_55",
    "inhabitants_age_55_65",
    "inhabitants_age_above_65",
    "inhabitants_female"
]

statistic_t3_properties = [
    "inhabitants_with_migration_background_age_below_6",
    "inhabitants_with_migration_background_age_6_15",
    "inhabitants_with_migration_background_age_15_18",
    "inhabitants_with_migration_background_age_18_27",
    "inhabitants_with_migration_background_age_27_45",
    "inhabitants_with_migration_background_age_45_55",
    "inhabitants_with_migration_background_age_55_65",
    "inhabitants_with_migration_background_age_above_65",
    "inhabitants_with_migration_background_female"
]

statistic_t4_properties = [
    "inhabitants_from_european_union",
    "inhabitants_from_france",
    "inhabitants_from_greece",
    "inhabitants_from_italy",
    "inhabitants_from_austria",
    "inhabitants_from_spain",
    "inhabitants_from_poland",
    "inhabitants_from_bulgaria",
    "inhabitants_from_rumania",
    "inhabitants_from_croatia",
    "inhabitants_from_united_kingdom",
    "inhabitants_from_former_yugoslavia",
    "inhabitants_from_bosnia_herzegovina",
    "inhabitants_from_serbia",
    "inhabitants_from_former_soviet_union",
    "inhabitants_from_russia",
    "inhabitants_from_ukraine",
    "inhabitants_from_kazakhstan",
    "inhabitants_from_islamic_countries",
    "inhabitants_from_turkey",
    "inhabitants_from_iran",
    "inhabitants_from_arabic_countries",
    "inhabitants_from_lebanon",
    "inhabitants_from_syria",
    "inhabitants_from_vietnam",
    "inhabitants_from_united_states",
    "inhabitants_from_undefined"
]

pre_2020_statistics = [
    ["berlin-lor-population-2015-01", "berlin-lor-population-2015-01"],
    ["berlin-lor-population-2015-02", "berlin-lor-population-2015-02"],
    ["berlin-lor-population-2016-01", "berlin-lor-population-2016-01"],
    ["berlin-lor-population-2016-02", "berlin-lor-population-2016-02"],
    ["berlin-lor-population-2017-01", "berlin-lor-population-2017-01"],
    ["berlin-lor-population-2017-02", "berlin-lor-population-2017-02"],
    ["berlin-lor-population-2018-01", "berlin-lor-population-2018-01"],
    ["berlin-lor-population-2018-02", "berlin-lor-population-2018-02"],
    ["berlin-lor-population-2019-01", "berlin-lor-population-2019-01"],
    ["berlin-lor-population-2019-02", "berlin-lor-population-2019-02"]
]

exactly_2020_statistics = [
    ["berlin-lor-population-2020-02", "berlin-lor-population-2020-02"]
]

post_2020_statistics = [
    ["berlin-lor-population-2021-01", "berlin-lor-population-2021-01"],
    ["berlin-lor-population-2021-02", "berlin-lor-population-2021-02"],
    ["berlin-lor-population-2022-01", "berlin-lor-population-2022-01"],
    ["berlin-lor-population-2022-02", "berlin-lor-population-2022-02"]
]


@TrackingDecorator.track_time
def blend_data(source_path, results_path, clean=False, quiet=False):
    # Make results path
    os.makedirs(os.path.join(results_path), exist_ok=True)

    source_geodata_path = os.path.join(source_path, "berlin-lor-geodata")

    # Statistics
    statistics_lor_districts = {}
    statistics_lor_forecast_areas = {}
    statistics_lor_district_regions = {}
    statistics_lor_planning_areas = {}

    # Load geojson
    geojson_lor_districts = read_geojson_file(os.path.join(source_geodata_path, "berlin-lor-districts.geojson"))
    geojson_lor_forecast_areas = read_geojson_file(
        os.path.join(source_geodata_path, "berlin-lor-forecast-areas-until-2020.geojson"))
    geojson_lor_district_regions = read_geojson_file(
        os.path.join(source_geodata_path, "berlin-lor-district-regions-until-2020.geojson"))
    geojson_lor_planning_areas = read_geojson_file(
        os.path.join(source_geodata_path, "berlin-lor-planning-areas-until-2020.geojson"))

    # Iterate over statistics
    for statistic_path, statistic_name in pre_2020_statistics:
        year = statistic_name.split(sep="-")[3]
        half_year = statistic_name.split(sep="-")[4]

        # Load statistics
        statistic_t1 = read_csv_file(os.path.join(source_path, statistic_path, f"{statistic_name}_T1.csv"))
        statistic_t2 = read_csv_file(os.path.join(source_path, statistic_path, f"{statistic_name}_T2.csv"))
        statistic_t3 = read_csv_file(os.path.join(source_path, statistic_path, f"{statistic_name}_T3.csv"))
        statistic_t4 = read_csv_file(os.path.join(source_path, statistic_path, f"{statistic_name}_T4.csv"))

        # Extend districts
        geojson_lor_districts_extended, statistics_lor_districts = extend_districts(
            statistics=statistics_lor_districts,
            year=year,
            half_year=half_year,
            statistic_name=statistic_name,
            statistic_t1=statistic_t1,
            statistic_t2=statistic_t2,
            statistic_t3=statistic_t3,
            statistic_t4=statistic_t4,
            geojson=geojson_lor_districts
        )

        # Extend forecast areas
        geojson_lor_forecast_areas_extended, statistics_lor_forecast_areas = extend_forecast_areas(
            statistics=statistics_lor_forecast_areas,
            year=year,
            half_year=half_year,
            statistic_name=statistic_name,
            statistic_t1=statistic_t1,
            statistic_t2=statistic_t2,
            statistic_t3=statistic_t3,
            statistic_t4=statistic_t4,
            geojson=geojson_lor_forecast_areas
        )

        # Extend district regions
        geojson_lor_district_regions_extended, statistics_lor_district_regions = extend_district_regions(
            statistics=statistics_lor_district_regions,
            year=year,
            half_year=half_year,
            statistic_name=statistic_name,
            statistic_t1=statistic_t1,
            statistic_t2=statistic_t2,
            statistic_t3=statistic_t3,
            statistic_t4=statistic_t4,
            geojson=geojson_lor_district_regions
        )

        # Extend planning areas
        geojson_lor_planning_areas_extended, statistics_lor_planning_areas = extend_planning_areas(
            statistics=statistics_lor_planning_areas,
            year=year,
            half_year=half_year,
            statistic_name=statistic_name,
            statistic_t1=statistic_t1,
            statistic_t2=statistic_t2,
            statistic_t3=statistic_t3,
            statistic_t4=statistic_t4,
            geojson=geojson_lor_planning_areas
        )

        # Write geojson files
        write_geojson_file(
            file_path=os.path.join(results_path, statistic_path,
                                   f"{key_figure_group}-{year}-{half_year}-districts.geojson"),
            statistic_name=f"{key_figure_group}-{year}-{half_year}-districts",
            geojson_content=geojson_lor_districts_extended,
            clean=clean,
            quiet=quiet
        )
        write_geojson_file(
            file_path=os.path.join(results_path, statistic_path,
                                   f"{key_figure_group}-{year}-{half_year}-forecast-areas.geojson"),
            statistic_name=f"{key_figure_group}-{year}-{half_year}-forecast-areas",
            geojson_content=geojson_lor_forecast_areas_extended,
            clean=clean,
            quiet=quiet
        )
        write_geojson_file(
            file_path=os.path.join(results_path, statistic_path,
                                   f"{key_figure_group}-{year}-{half_year}-district-regions.geojson"),
            statistic_name=f"{key_figure_group}-{year}-{half_year}-district-regions",
            geojson_content=geojson_lor_district_regions_extended,
            clean=clean,
            quiet=quiet
        )
        write_geojson_file(
            file_path=os.path.join(results_path, statistic_path,
                                   f"{key_figure_group}-{year}-{half_year}-planning-areas.geojson"),
            statistic_name=f"{key_figure_group}-{year}-{half_year}-planning-areas",
            geojson_content=geojson_lor_planning_areas_extended,
            clean=clean,
            quiet=quiet
        )

    # Iterate over statistics
    for statistic_path, statistic_name in exactly_2020_statistics:
        year = statistic_name.split(sep="-")[3]
        half_year = statistic_name.split(sep="-")[4]

        # Load statistics
        statistic_t1 = read_csv_file(os.path.join(source_path, statistic_path, f"{statistic_name}_T1a.csv"))
        statistic_t2 = read_csv_file(os.path.join(source_path, statistic_path, f"{statistic_name}_T2a.csv"))
        statistic_t3 = read_csv_file(os.path.join(source_path, statistic_path, f"{statistic_name}_T3a.csv"))
        statistic_t4 = read_csv_file(os.path.join(source_path, statistic_path, f"{statistic_name}_T4a.csv"))

        # Extend districts
        geojson_lor_districts_extended, statistics_lor_districts = extend_districts(
            statistics=statistics_lor_districts,
            year=year,
            half_year=half_year,
            statistic_name=statistic_name,
            statistic_t1=statistic_t1,
            statistic_t2=statistic_t2,
            statistic_t3=statistic_t3,
            statistic_t4=statistic_t4,
            geojson=geojson_lor_districts
        )

        # Extend forecast areas
        geojson_lor_forecast_areas_extended, statistics_lor_forecast_areas = extend_forecast_areas(
            statistics=statistics_lor_forecast_areas,
            year=year,
            half_year=half_year,
            statistic_name=statistic_name,
            statistic_t1=statistic_t1,
            statistic_t2=statistic_t2,
            statistic_t3=statistic_t3,
            statistic_t4=statistic_t4,
            geojson=geojson_lor_forecast_areas
        )

        # Extend district regions
        geojson_lor_district_regions_extended, statistics_lor_district_regions = extend_district_regions(
            statistics=statistics_lor_district_regions,
            year=year,
            half_year=half_year,
            statistic_name=statistic_name,
            statistic_t1=statistic_t1,
            statistic_t2=statistic_t2,
            statistic_t3=statistic_t3,
            statistic_t4=statistic_t4,
            geojson=geojson_lor_district_regions
        )

        # Extend planning areas
        geojson_lor_planning_areas_extended, statistics_lor_planning_areas = extend_planning_areas(
            statistics=statistics_lor_planning_areas,
            year=year,
            half_year=half_year,
            statistic_name=statistic_name,
            statistic_t1=statistic_t1,
            statistic_t2=statistic_t2,
            statistic_t3=statistic_t3,
            statistic_t4=statistic_t4,
            geojson=geojson_lor_planning_areas
        )

        # Write geojson files
        write_geojson_file(
            file_path=os.path.join(results_path, statistic_path,
                                   f"{key_figure_group}-{year}-{half_year}-districts.geojson"),
            statistic_name=f"{key_figure_group}-{year}-{half_year}-districts",
            geojson_content=geojson_lor_districts_extended,
            clean=clean,
            quiet=quiet
        )
        write_geojson_file(
            file_path=os.path.join(results_path, statistic_path,
                                   f"{key_figure_group}-{year}-{half_year}-forecast-areas.geojson"),
            statistic_name=f"{key_figure_group}-{year}-{half_year}-forecast-areas",
            geojson_content=geojson_lor_forecast_areas_extended,
            clean=clean,
            quiet=quiet
        )
        write_geojson_file(
            file_path=os.path.join(results_path, statistic_path,
                                   f"{key_figure_group}-{year}-{half_year}-district-regions.geojson"),
            statistic_name=f"{key_figure_group}-{year}-{half_year}-district-regions",
            geojson_content=geojson_lor_district_regions_extended,
            clean=clean,
            quiet=quiet
        )
        write_geojson_file(
            file_path=os.path.join(results_path, statistic_path,
                                   f"{key_figure_group}-{year}-{half_year}-planning-areas.geojson"),
            statistic_name=f"{key_figure_group}-{year}-{half_year}-planning-areas",
            geojson_content=geojson_lor_planning_areas_extended,
            clean=clean,
            quiet=quiet
        )

    # Load geojson
    geojson_lor_districts = read_geojson_file(os.path.join(source_geodata_path, "berlin-lor-districts.geojson"))
    geojson_lor_forecast_areas = read_geojson_file(
        os.path.join(source_geodata_path, "berlin-lor-forecast-areas-from-2021.geojson"))
    geojson_lor_district_regions = read_geojson_file(
        os.path.join(source_geodata_path, "berlin-lor-district-regions-from-2021.geojson"))
    geojson_lor_planning_areas = read_geojson_file(
        os.path.join(source_geodata_path, "berlin-lor-planning-areas-from-2021.geojson"))

    # Iterate over statistics
    for statistic_path, statistic_name in exactly_2020_statistics:
        year = statistic_name.split(sep="-")[3]
        half_year = statistic_name.split(sep="-")[4]

        # Load statistics
        statistic_t1 = read_csv_file(os.path.join(source_path, statistic_path, f"{statistic_name}_T1b.csv"))
        statistic_t2 = read_csv_file(os.path.join(source_path, statistic_path, f"{statistic_name}_T2b.csv"))
        statistic_t3 = read_csv_file(os.path.join(source_path, statistic_path, f"{statistic_name}_T3b.csv"))
        statistic_t4 = read_csv_file(os.path.join(source_path, statistic_path, f"{statistic_name}_T4b.csv"))

        # Extend districts
        geojson_lor_districts_extended, statistics_lor_districts = extend_districts(
            statistics=statistics_lor_districts,
            year=year,
            half_year=half_year,
            statistic_name=statistic_name,
            statistic_t1=statistic_t1,
            statistic_t2=statistic_t2,
            statistic_t3=statistic_t3,
            statistic_t4=statistic_t4,
            geojson=geojson_lor_districts
        )

        # Extend forecast areas
        geojson_lor_forecast_areas_extended, statistics_lor_forecast_areas = extend_forecast_areas(
            statistics=statistics_lor_forecast_areas,
            year=year,
            half_year=half_year,
            statistic_name=statistic_name,
            statistic_t1=statistic_t1,
            statistic_t2=statistic_t2,
            statistic_t3=statistic_t3,
            statistic_t4=statistic_t4,
            geojson=geojson_lor_forecast_areas
        )

        # Extend district regions
        geojson_lor_district_regions_extended, statistics_lor_district_regions = extend_district_regions(
            statistics=statistics_lor_district_regions,
            year=year,
            half_year=half_year,
            statistic_name=statistic_name,
            statistic_t1=statistic_t1,
            statistic_t2=statistic_t2,
            statistic_t3=statistic_t3,
            statistic_t4=statistic_t4,
            geojson=geojson_lor_district_regions
        )

        # Extend planning areas
        geojson_lor_planning_areas_extended, statistics_lor_planning_areas = extend_planning_areas(
            statistics=statistics_lor_planning_areas,
            year=year,
            half_year=half_year,
            statistic_name=statistic_name,
            statistic_t1=statistic_t1,
            statistic_t2=statistic_t2,
            statistic_t3=statistic_t3,
            statistic_t4=statistic_t4,
            geojson=geojson_lor_planning_areas
        )

        # Write geojson files
        write_geojson_file(
            file_path=os.path.join(results_path, statistic_path,
                                   f"{key_figure_group}-{year}-{half_year}-districts-new-format.geojson"),
            statistic_name=f"{key_figure_group}-{year}-{half_year}-districts",
            geojson_content=geojson_lor_districts_extended,
            clean=clean,
            quiet=quiet
        )
        write_geojson_file(
            file_path=os.path.join(results_path, statistic_path,
                                   f"{key_figure_group}-{year}-{half_year}-forecast-areas-new-format.geojson"),
            statistic_name=f"{key_figure_group}-{year}-{half_year}-forecast-areas",
            geojson_content=geojson_lor_forecast_areas_extended,
            clean=clean,
            quiet=quiet
        )
        write_geojson_file(
            file_path=os.path.join(results_path, statistic_path,
                                   f"{key_figure_group}-{year}-{half_year}-district-regions-new-format.geojson"),
            statistic_name=f"{key_figure_group}-{year}-{half_year}-district-regions",
            geojson_content=geojson_lor_district_regions_extended,
            clean=clean,
            quiet=quiet
        )
        write_geojson_file(
            file_path=os.path.join(results_path, statistic_path,
                                   f"{key_figure_group}-{year}-{half_year}-planning-areas-new-format.geojson"),
            statistic_name=f"{key_figure_group}-{year}-{half_year}-planning-areas",
            geojson_content=geojson_lor_planning_areas_extended,
            clean=clean,
            quiet=quiet
        )

    # Iterate over statistics
    for statistic_path, statistic_name in post_2020_statistics:
        year = statistic_name.split(sep="-")[3]
        half_year = statistic_name.split(sep="-")[4]

        # Load statistics
        statistic_t1 = read_csv_file(os.path.join(source_path, statistic_path, f"{statistic_name}_T1.csv"))
        statistic_t2 = read_csv_file(os.path.join(source_path, statistic_path, f"{statistic_name}_T2.csv"))
        statistic_t3 = read_csv_file(os.path.join(source_path, statistic_path, f"{statistic_name}_T3.csv"))
        statistic_t4 = read_csv_file(os.path.join(source_path, statistic_path, f"{statistic_name}_T4.csv"))

        # Extend districts
        geojson_lor_districts_extended, statistics_lor_districts = extend_districts(
            statistics=statistics_lor_districts,
            year=year,
            half_year=half_year,
            statistic_name=statistic_name,
            statistic_t1=statistic_t1,
            statistic_t2=statistic_t2,
            statistic_t3=statistic_t3,
            statistic_t4=statistic_t4,
            geojson=geojson_lor_districts
        )

        # Extend forecast areas
        geojson_lor_forecast_areas_extended, statistics_lor_forecast_areas = extend_forecast_areas(
            statistics=statistics_lor_forecast_areas,
            year=year,
            half_year=half_year,
            statistic_name=statistic_name,
            statistic_t1=statistic_t1,
            statistic_t2=statistic_t2,
            statistic_t3=statistic_t3,
            statistic_t4=statistic_t4,
            geojson=geojson_lor_forecast_areas
        )

        # Extend district regions
        geojson_lor_district_regions_extended, statistics_lor_district_regions = extend_district_regions(
            statistics=statistics_lor_district_regions,
            year=year,
            half_year=half_year,
            statistic_name=statistic_name,
            statistic_t1=statistic_t1,
            statistic_t2=statistic_t2,
            statistic_t3=statistic_t3,
            statistic_t4=statistic_t4,
            geojson=geojson_lor_district_regions
        )

        # Extend planning areas
        geojson_lor_planning_areas_extended, statistics_lor_planning_areas = extend_planning_areas(
            statistics=statistics_lor_planning_areas,
            year=year,
            half_year=half_year,
            statistic_name=statistic_name,
            statistic_t1=statistic_t1,
            statistic_t2=statistic_t2,
            statistic_t3=statistic_t3,
            statistic_t4=statistic_t4,
            geojson=geojson_lor_planning_areas
        )

        # Write geojson files
        write_geojson_file(
            file_path=os.path.join(results_path, statistic_path, f"{key_figure_group}-{year}-{half_year}-districts.geojson"),
            statistic_name=f"{key_figure_group}-{year}-{half_year}-districts",
            geojson_content=geojson_lor_districts_extended,
            clean=clean,
            quiet=quiet
        )
        write_geojson_file(
            file_path=os.path.join(results_path, statistic_path,
                                   f"{key_figure_group}-{year}-{half_year}-forecast-areas.geojson"),
            statistic_name=f"{key_figure_group}-{year}-{half_year}-forecast-areas",
            geojson_content=geojson_lor_forecast_areas_extended,
            clean=clean,
            quiet=quiet
        )
        write_geojson_file(
            file_path=os.path.join(results_path, statistic_path,
                                   f"{key_figure_group}-{year}-{half_year}-district-regions.geojson"),
            statistic_name=f"{key_figure_group}-{year}-{half_year}-district-regions",
            geojson_content=geojson_lor_district_regions_extended,
            clean=clean,
            quiet=quiet
        )
        write_geojson_file(
            file_path=os.path.join(results_path, statistic_path,
                                   f"{key_figure_group}-{year}-{half_year}-planning-areas.geojson"),
            statistic_name=f"{key_figure_group}-{year}-{half_year}-planning-areas",
            geojson_content=geojson_lor_planning_areas_extended,
            clean=clean,
            quiet=quiet
        )

    # Write json file
    write_json_file(
        file_path=os.path.join(results_path, f"{key_figure_group}-statistics", f"{key_figure_group}-districts-statistics.json"),
        statistic_name=f"{key_figure_group}-districts-statistics",
        json_content=statistics_lor_districts,
        clean=clean,
        quiet=quiet
    )
    write_json_file(
        file_path=os.path.join(results_path, f"{key_figure_group}-statistics", f"{key_figure_group}-forecast-areas-statistics.json"),
        statistic_name=f"{key_figure_group}-forecast-areas-statistics",
        json_content=statistics_lor_forecast_areas,
        clean=clean,
        quiet=quiet
    )
    write_json_file(
        file_path=os.path.join(results_path, f"{key_figure_group}-statistics", f"{key_figure_group}-district-regions-statistics.json"),
        statistic_name=f"{key_figure_group}-district-regions-statistics",
        json_content=statistics_lor_district_regions,
        clean=clean,
        quiet=quiet
    )
    write_json_file(
        file_path=os.path.join(results_path, f"{key_figure_group}-statistics", f"{key_figure_group}-planning-areas-statistics.json"),
        statistic_name=f"{key_figure_group}-planning-areas-statistics",
        json_content=statistics_lor_planning_areas,
        clean=clean,
        quiet=quiet
    )


def read_csv_file(file_path):
    if "None" not in file_path:
        with open(file_path, "r") as csv_file:
            return pd.read_csv(csv_file)
    else:
        return None


def read_geojson_file(file_path):
    with open(file_path, "r") as geojson_file:
        return json.load(geojson_file)


def write_geojson_file(file_path, statistic_name, geojson_content, clean, quiet):
    if not os.path.exists(file_path) or clean:
        path_name = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)

        os.makedirs(os.path.join(path_name), exist_ok=True)

        with open(file_path, "w") as geojson_file:
            json.dump(geojson_content, geojson_file)

            if not quiet:
                print(f"✓ Blend data from {statistic_name} into {file_name}")


def write_json_file(file_path, statistic_name, json_content, clean, quiet):
    if not os.path.exists(file_path) or clean:
        path_name = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)

        os.makedirs(os.path.join(path_name), exist_ok=True)

        with open(file_path, "w") as json_file:
            json.dump(json_content, json_file)

            if not quiet:
                print(f"✓ Aggregate data from {statistic_name} into {file_name}")


def extend_districts(statistics, year, half_year,
                     statistic_name, statistic_t1, statistic_t2, statistic_t3, statistic_t4, geojson):
    geojson_extended = copy.deepcopy(geojson)

    # Check if file needs to be created
    for feature in geojson_extended["features"]:
        feature_id = feature["properties"]["id"]
        district_id = feature_id
        area_sqm = feature["properties"]["area"]
        area_sqkm = area_sqm / 1_000_000

        # Filter statistics
        statistic_t1_filtered = statistic_t1.loc[(statistic_t1["district"] == int(district_id))]
        statistic_t2_filtered = statistic_t2.loc[(statistic_t2["district"] == int(district_id))]
        statistic_t3_filtered = statistic_t3.loc[(statistic_t3["district"] == int(district_id))]
        statistic_t4_filtered = statistic_t4.loc[(statistic_t4["district"] == int(district_id))]

        # Check for missing data
        if statistic_t1_filtered.shape[0] == 0 or statistic_t2_filtered.shape[0] == 0 or \
                statistic_t3_filtered.shape[0] == 0 or statistic_t4_filtered.shape[0] == 0 or \
                int(statistic_t1_filtered["inhabitants"].sum()) == 0 or \
                int(statistic_t1_filtered["inhabitants_with_migration_background"].sum()) == 0:
            print(f"✗️ No data in {statistic_name} for district={district_id}")
            continue

        # Blend data
        feature = blend_data_into_feature(
            feature=feature, area_sqkm=area_sqkm,
            statistic_t1=statistic_t1_filtered,
            statistic_t2=statistic_t2_filtered,
            statistic_t3=statistic_t3_filtered,
            statistic_t4=statistic_t4_filtered
        )

        # Build structure
        if year not in statistics:
            statistics[year] = {}
        if half_year not in statistics[year]:
            statistics[year][half_year] = {}

        # Add properties
        statistics[year][half_year][feature_id] = feature["properties"]

    # Calculate average and median values
    for year, half_years in statistics.items():
        for half_year, feature_ids in half_years.items():
            values = {}

            for feature_id, properties in feature_ids.items():
                for property_name, property_value in properties.items():
                    if property_name in statistic_t1_properties + statistic_t2_properties + statistic_t3_properties \
                            + statistic_t4_properties:
                        if property_name not in values:
                            values[property_name] = []
                        values[property_name].append(property_value)

            statistics[year][half_year]["average"] = {key: stats.mean(lst) for key, lst in values.items()}
            statistics[year][half_year]["median"] = {key: stats.median(lst) for key, lst in values.items()}

    return geojson_extended, statistics


def extend_forecast_areas(statistics, year, half_year,
                          statistic_name, statistic_t1, statistic_t2, statistic_t3, statistic_t4, geojson):
    geojson_extended = copy.deepcopy(geojson)

    # Check if file needs to be created
    for feature in geojson_extended["features"]:
        feature_id = feature["properties"]["id"]
        district_id, forecast_area_id, district_region_id, planning_area_id = build_ids(feature_id)
        area_sqm = feature["properties"]["area"]
        area_sqkm = area_sqm / 1_000_000

        # Filter statistics
        statistic_t1_filtered = statistic_t1.loc[
            (statistic_t1["district"] == int(district_id)) &
            (statistic_t1["forecast_area"] == int(forecast_area_id))]
        statistic_t2_filtered = statistic_t2.loc[
            (statistic_t2["district"] == int(district_id)) &
            (statistic_t2["forecast_area"] == int(forecast_area_id))]
        statistic_t3_filtered = statistic_t3.loc[
            (statistic_t3["district"] == int(district_id)) &
            (statistic_t3["forecast_area"] == int(forecast_area_id))]
        statistic_t4_filtered = statistic_t4.loc[
            (statistic_t4["district"] == int(district_id)) &
            (statistic_t4["forecast_area"] == int(forecast_area_id))]

        # Check for missing data
        if statistic_t1_filtered.shape[0] == 0 or statistic_t2_filtered.shape[0] == 0 or \
                statistic_t3_filtered.shape[0] == 0 or statistic_t4_filtered.shape[0] == 0 or \
                statistic_t1_filtered["inhabitants"].sum() == 0 or \
                statistic_t1_filtered["inhabitants_with_migration_background"].sum() == 0:
            print(f"✗️ No data in {statistic_name} for district={district_id}, forecast area={forecast_area_id}")
            continue

        # Blend data
        blend_data_into_feature(
            feature=feature, area_sqkm=area_sqkm,
            statistic_t1=statistic_t1_filtered,
            statistic_t2=statistic_t2_filtered,
            statistic_t3=statistic_t3_filtered,
            statistic_t4=statistic_t4_filtered
        )

        # Build structure
        if year not in statistics:
            statistics[year] = {}
        if half_year not in statistics[year]:
            statistics[year][half_year] = {}

        # Add properties
        statistics[year][half_year][feature_id] = feature["properties"]

    # Calculate average and median values
    for year, half_years in statistics.items():
        for half_year, feature_ids in half_years.items():
            values = {}

            for feature_id, properties in feature_ids.items():
                for property_name, property_value in properties.items():
                    if property_name in statistic_t1_properties + statistic_t2_properties + statistic_t3_properties \
                            + statistic_t4_properties:
                        if property_name not in values:
                            values[property_name] = []
                        values[property_name].append(property_value)

            statistics[year][half_year]["average"] = {key: stats.mean(lst) for key, lst in values.items()}
            statistics[year][half_year]["median"] = {key: stats.median(lst) for key, lst in values.items()}

    return geojson_extended, statistics


def extend_district_regions(statistics, year, half_year,
                            statistic_name, statistic_t1, statistic_t2, statistic_t3, statistic_t4, geojson):
    geojson_extended = copy.deepcopy(geojson)

    # Check if file needs to be created
    for feature in geojson_extended["features"]:
        feature_id = feature["properties"]["id"]
        district_id, forecast_area_id, district_region_id, planning_area_id = build_ids(feature_id)
        area_sqm = feature["properties"]["area"]
        area_sqkm = area_sqm / 1_000_000

        # Filter statistics
        statistic_t1_filtered = statistic_t1.loc[
            (statistic_t1["district"] == int(district_id)) &
            (statistic_t1["forecast_area"] == int(forecast_area_id)) &
            (statistic_t1["district_region"] == int(district_region_id))]
        statistic_t2_filtered = statistic_t2.loc[
            (statistic_t2["district"] == int(district_id)) &
            (statistic_t2["forecast_area"] == int(forecast_area_id)) &
            (statistic_t2["district_region"] == int(district_region_id))]
        statistic_t3_filtered = statistic_t3.loc[
            (statistic_t3["district"] == int(district_id)) &
            (statistic_t3["forecast_area"] == int(forecast_area_id)) &
            (statistic_t3["district_region"] == int(district_region_id))]
        statistic_t4_filtered = statistic_t4.loc[
            (statistic_t4["district"] == int(district_id)) &
            (statistic_t4["forecast_area"] == int(forecast_area_id)) &
            (statistic_t4["district_region"] == int(district_region_id))]

        # Check for missing data
        if statistic_t1_filtered.shape[0] == 0 or statistic_t2_filtered.shape[0] == 0 or \
                statistic_t3_filtered.shape[0] == 0 or statistic_t4_filtered.shape[0] == 0 or \
                statistic_t1_filtered["inhabitants"].sum() == 0 or \
                statistic_t1_filtered["inhabitants_with_migration_background"].sum() == 0:
            print(
                f"✗️ No data in {statistic_name} for district={district_id}, forecast area={forecast_area_id}, "
                f"district_region_id={district_region_id}")
            continue

        # Blend data
        feature = blend_data_into_feature(
            feature=feature, area_sqkm=area_sqkm,
            statistic_t1=statistic_t1_filtered,
            statistic_t2=statistic_t2_filtered,
            statistic_t3=statistic_t3_filtered,
            statistic_t4=statistic_t4_filtered
        )

        # Build structure
        if year not in statistics:
            statistics[year] = {}
        if half_year not in statistics[year]:
            statistics[year][half_year] = {}

        # Add properties
        statistics[year][half_year][feature_id] = feature["properties"]

    # Calculate average and median values
    for year, half_years in statistics.items():
        for half_year, feature_ids in half_years.items():
            values = {}

            for feature_id, properties in feature_ids.items():
                for property_name, property_value in properties.items():
                    if property_name in statistic_t1_properties + statistic_t2_properties + statistic_t3_properties \
                            + statistic_t4_properties:
                        if property_name not in values:
                            values[property_name] = []
                        values[property_name].append(property_value)

            statistics[year][half_year]["average"] = {key: stats.mean(lst) for key, lst in values.items()}
            statistics[year][half_year]["median"] = {key: stats.median(lst) for key, lst in values.items()}

    return geojson_extended, statistics


def extend_planning_areas(statistics, year, half_year,
                          statistic_name, statistic_t1, statistic_t2, statistic_t3, statistic_t4, geojson):
    geojson_extended = copy.deepcopy(geojson)

    # Check if file needs to be created
    for feature in geojson_extended["features"]:
        feature_id = feature["properties"]["id"]
        district_id, forecast_area_id, district_region_id, planning_area_id = build_ids(feature_id)
        area_sqm = feature["properties"]["area"]
        area_sqkm = area_sqm / 1_000_000

        # Filter statistics
        statistic_t1_filtered = statistic_t1.loc[
            (statistic_t1["district"] == int(district_id)) &
            (statistic_t1["forecast_area"] == int(forecast_area_id)) &
            (statistic_t1["district_region"] == int(district_region_id)) &
            (statistic_t1["planning_area"] == int(planning_area_id))]
        statistic_t2_filtered = statistic_t2.loc[
            (statistic_t2["district"] == int(district_id)) &
            (statistic_t2["forecast_area"] == int(forecast_area_id)) &
            (statistic_t2["district_region"] == int(district_region_id)) &
            (statistic_t2["planning_area"] == int(planning_area_id))]
        statistic_t3_filtered = statistic_t3.loc[
            (statistic_t3["district"] == int(district_id)) &
            (statistic_t3["forecast_area"] == int(forecast_area_id)) &
            (statistic_t3["district_region"] == int(district_region_id)) &
            (statistic_t3["planning_area"] == int(planning_area_id))]
        statistic_t4_filtered = statistic_t4.loc[
            (statistic_t4["district"] == int(district_id)) &
            (statistic_t4["forecast_area"] == int(forecast_area_id)) &
            (statistic_t4["district_region"] == int(district_region_id)) &
            (statistic_t4["planning_area"] == int(planning_area_id))]

        # Check for missing data
        if statistic_t1_filtered.shape[0] == 0 or statistic_t2_filtered.shape[0] == 0 or \
                statistic_t3_filtered.shape[0] == 0 or statistic_t4_filtered.shape[0] == 0 or \
                statistic_t1_filtered["inhabitants"].sum() == 0 or \
                statistic_t1_filtered["inhabitants_with_migration_background"].sum() == 0:
            print(
                f"✗️ No data in {statistic_name} for district={district_id}, forecast area={forecast_area_id}, "
                f"district_region_id={district_region_id}, planning_area_id={planning_area_id}")
            continue

        # Blend data
        feature = blend_data_into_feature(
            feature=feature, area_sqkm=area_sqkm,
            statistic_t1=statistic_t1_filtered,
            statistic_t2=statistic_t2_filtered,
            statistic_t3=statistic_t3_filtered,
            statistic_t4=statistic_t4_filtered
        )

        # Build structure
        if year not in statistics:
            statistics[year] = {}
        if half_year not in statistics[year]:
            statistics[year][half_year] = {}

        # Add properties
        statistics[year][half_year][feature_id] = feature["properties"]

    # Calculate average and median values
    for year, half_years in statistics.items():
        for half_year, feature_ids in half_years.items():
            values = {}

            for feature_id, properties in feature_ids.items():
                for property_name, property_value in properties.items():
                    if property_name in statistic_t1_properties + statistic_t2_properties + statistic_t3_properties \
                            + statistic_t4_properties:
                        if property_name not in values:
                            values[property_name] = []
                        values[property_name].append(property_value)

            statistics[year][half_year]["average"] = {key: stats.mean(lst) for key, lst in values.items()}
            statistics[year][half_year]["median"] = {key: stats.median(lst) for key, lst in values.items()}

    return geojson_extended, statistics


def build_ids(combined_id):
    return combined_id[0:2], combined_id[2:4], combined_id[4:6], combined_id[6:8]


def blend_data_into_feature(feature, area_sqkm, statistic_t1, statistic_t2, statistic_t3, statistic_t4):
    # Lookup data
    inhabitants = statistic_t1["inhabitants"].sum()

    # Add new properties
    for property_name in statistic_t1_properties:
        add_property_with_modifiers(feature, statistic_t1, property_name, inhabitants, area_sqkm)
    for property_name in statistic_t2_properties:
        add_property_with_modifiers(feature, statistic_t2, property_name, inhabitants, area_sqkm)
    for property_name in statistic_t3_properties:
        add_property_with_modifiers(feature, statistic_t3, property_name, inhabitants, area_sqkm)
    for property_name in statistic_t4_properties:
        add_property_with_modifiers(feature, statistic_t4, property_name, inhabitants, area_sqkm)

    return feature


def add_property(feature, statistics, property_name):
    if property_name in statistics:
        try:
            feature["properties"][f"{property_name}"] = float(statistics[property_name])
        except ValueError:
            feature["properties"][f"{property_name}"] = 0


def add_property_with_modifiers(feature, statistics, property_name, inhabitants, total_area_sqkm):
    if property_name in statistics:
        try:
            feature["properties"][f"{property_name}"] = float(statistics[property_name].sum())
            if inhabitants is not None:
                feature["properties"][f"{property_name}_percentage"] = round(
                    float(statistics[property_name].sum()) / inhabitants * 100, 2)
            if total_area_sqkm is not None:
                feature["properties"][f"{property_name}_per_sqkm"] = round(
                    float(statistics[property_name].sum()) / total_area_sqkm)
        except ValueError:
            feature["properties"][f"{property_name}"] = 0

            if inhabitants is not None:
                feature["properties"][f"{property_name}_percentage"] = 0
            if total_area_sqkm is not None:
                feature["properties"][f"{property_name}_per_sqkm"] = 0
