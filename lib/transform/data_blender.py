import json
import os
import re

import pandas as pd

from lib.tracking_decorator import TrackingDecorator

key_figure_group = "berlin-lor-population"

statistic_properties = [
    "inhabitants",
    "inhabitants_with_migration_background",
    "inhabitants_germans",
    "inhabitants_germans_without_migration_background",
    "inhabitants_germans_with_migration_background",
    "inhabitants_foreigners",
    "inhabitants_age_below_6",
    "inhabitants_age_6_15",
    "inhabitants_age_15_18",
    "inhabitants_age_18_27",
    "inhabitants_age_27_45",
    "inhabitants_age_45_55",
    "inhabitants_age_55_65",
    "inhabitants_age_above_65",
    "inhabitants_female",
    "inhabitants_with_migration_background_age_below_6",
    "inhabitants_with_migration_background_age_6_15",
    "inhabitants_with_migration_background_age_15_18",
    "inhabitants_with_migration_background_age_18_27",
    "inhabitants_with_migration_background_age_27_45",
    "inhabitants_with_migration_background_age_45_55",
    "inhabitants_with_migration_background_age_55_65",
    "inhabitants_with_migration_background_age_above_65",
    "inhabitants_with_migration_background_female",
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

statistics = [
    f"{key_figure_group}-2015-01",
    f"{key_figure_group}-2015-02",
    f"{key_figure_group}-2016-01",
    f"{key_figure_group}-2016-02",
    f"{key_figure_group}-2017-01",
    f"{key_figure_group}-2017-02",
    f"{key_figure_group}-2018-01",
    f"{key_figure_group}-2018-02",
    f"{key_figure_group}-2019-01",
    f"{key_figure_group}-2019-02",
    f"{key_figure_group}-2020-01",
    f"{key_figure_group}-2020-02",
    f"{key_figure_group}-2021-01",
    f"{key_figure_group}-2021-02",
    f"{key_figure_group}-2022-01",
    f"{key_figure_group}-2022-02"
]


@TrackingDecorator.track_time
def blend_data(source_path, results_path, clean=False, quiet=False):
    # Make results path
    os.makedirs(os.path.join(results_path), exist_ok=True)

    # Initialize statistics
    json_statistics = {}

    # Iterate over LOR area types
    for lor_area_type in ["districts", "forecast-areas", "district-regions", "planning-areas"]:

        # Iterate over statistics
        for statistics_name in sorted(statistics):
            year = re.search(r"\b\d{4}\b", statistics_name).group()
            half_year = re.search(r"\b\d{2}(?<!\d{4})\b", statistics_name).group()

            # Load geojson
            if lor_area_type == "districts":
                geojson = read_geojson_file(
                    os.path.join(source_path, "berlin-lor-geodata", f"berlin-lor-{lor_area_type}.geojson"))
            elif int(year) <= 2020:
                geojson = read_geojson_file(
                    os.path.join(source_path, "berlin-lor-geodata", f"berlin-lor-{lor_area_type}-until-2020.geojson"))
            elif int(year) >= 2021:
                geojson = read_geojson_file(
                    os.path.join(source_path, "berlin-lor-geodata", f"berlin-lor-{lor_area_type}-from-2021.geojson"))
            else:
                geojson = None

            # Load statistics
            csv_statistics = read_csv_file(os.path.join(source_path, statistics_name, f"{statistics_name}.csv"))

            # Extend geojson
            extend(
                year=year,
                half_year=half_year,
                geojson=geojson,
                statistics_name=statistics_name,
                csv_statistics=csv_statistics,
                json_statistics=json_statistics
            )

            # Write geojson file
            write_geojson_file(
                file_path=os.path.join(results_path, statistics_name,
                                       f"{key_figure_group}-{year}-{half_year}-{lor_area_type}.geojson"),
                statistic_name=f"{key_figure_group}-{year}-{half_year}-{lor_area_type}",
                geojson=geojson,
                clean=clean,
                quiet=quiet
            )

    # Write json statistics file
    write_json_file(
        file_path=os.path.join(results_path, f"{key_figure_group}-statistics",
                               f"{key_figure_group}-statistics.json"),
        statistic_name=f"{key_figure_group}-statistics",
        json_content=json_statistics,
        clean=clean,
        quiet=quiet
    )


def extend(year, half_year, geojson, statistics_name, csv_statistics, json_statistics):
    """
    Extends geojson and json-statistics by statistical values
    :param year:
    :param half_year:
    :param geojson:
    :param statistics_name:
    :param csv_statistics:
    :param json_statistics:
    :return:
    """

    # Check for missing files
    if csv_statistics is None:
        print(f"✗️ No data in {statistics_name}")
        return

    # Iterate over features
    for feature in sorted(geojson["features"], key=lambda feature: feature["properties"]["id"]):
        feature_id = feature["properties"]["id"]
        area_sqm = feature["properties"]["area"]
        area_sqkm = area_sqm / 1_000_000

        # Filter statistics
        statistic_filtered = csv_statistics[csv_statistics["id"].astype(str).str.startswith(feature_id)]

        # Check for missing data
        if statistic_filtered.shape[0] == 0 or \
                int(statistic_filtered["inhabitants"].sum()) == 0 or \
                int(statistic_filtered["inhabitants_with_migration_background"].sum()) == 0:
            print(f"✗️ No data in {statistics_name} for id={feature_id}")
            continue

        # Blend data
        blend_data_into_feature(feature, statistic_filtered, area_sqkm)
        blend_data_into_json(year, half_year, feature_id, feature, json_statistics)

    # Calculate averages
    calculate_averages(year, half_year, geojson, csv_statistics, json_statistics)


def blend_data_into_feature(feature, statistics, area_sqkm):
    # Lookup data
    inhabitants = statistics["inhabitants"].sum()

    # Add new properties
    for property_name in statistic_properties:
        add_property_with_modifiers(feature, statistics, property_name, inhabitants, area_sqkm)

    return feature


def blend_data_into_json(year, half_year, feature_id, feature, json_statistics):
    # Build structure
    if year not in json_statistics:
        json_statistics[year] = {}
    if half_year not in json_statistics[year]:
        json_statistics[year][half_year] = {}

    # Add properties
    json_statistics[year][half_year][feature_id] = feature["properties"]


def calculate_averages(year, half_year, geojson, csv_statistics, json_statistics):
    # Calculate total values
    total_inhabitants = get_total_inhabitants(csv_statistics)
    total_sqkm = get_total_sqkm(geojson)

    values = {}

    # Iterate over properties
    for property_name in [property_name for property_name in statistic_properties if property_name in csv_statistics]:
        values[property_name] = sum(csv_statistics[property_name])

    json_statistics[year][half_year]["total"] = values
    json_statistics[year][half_year]["total_percentage"] = \
        {property_name: round(float(total / total_inhabitants * 100), 2) for property_name, total in values.items()}
    json_statistics[year][half_year]["total_per_sqkm"] = \
        {property_name: total / total_sqkm for property_name, total in values.items()}


def add_property(feature, statistics, property_name):
    if statistics is not None and property_name in statistics:
        try:
            feature["properties"][f"{property_name}"] = float(statistics[property_name].sum())
        except ValueError:
            feature["properties"][f"{property_name}"] = 0


def add_property_with_modifiers(feature, statistics, property_name, inhabitants, area_sqkm):
    if statistics is not None and property_name in statistics:
        try:
            feature["properties"][f"{property_name}"] = float(statistics[property_name].sum())
            if inhabitants is not None:
                feature["properties"][f"{property_name}_percentage"] = round(
                    float(statistics[property_name].sum()) / inhabitants * 100, 2)
            if area_sqkm is not None:
                feature["properties"][f"{property_name}_per_sqkm"] = round(
                    float(statistics[property_name].sum()) / area_sqkm, 2)
        except ValueError:
            feature["properties"][f"{property_name}"] = 0

            if inhabitants is not None:
                feature["properties"][f"{property_name}_percentage"] = 0
            if area_sqkm is not None:
                feature["properties"][f"{property_name}_per_sqkm"] = 0
        except TypeError:
            feature["properties"][f"{property_name}"] = 0

            if inhabitants is not None:
                feature["properties"][f"{property_name}_percentage"] = 0
            if area_sqkm is not None:
                feature["properties"][f"{property_name}_per_sqkm"] = 0


def get_total_inhabitants(csv_statistics):
    return sum(csv_statistics["inhabitants"])


def get_total_sqkm(geojson):
    return sum(feature["properties"]["area"] / 1_000_000 for feature in geojson["features"])


def read_csv_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as csv_file:
            return pd.read_csv(csv_file, dtype={"id": "str"})
    else:
        return None


def read_geojson_file(file_path):
    with open(file=file_path, mode="r", encoding="utf-8") as geojson_file:
        return json.load(geojson_file, strict=False)


def write_geojson_file(file_path, statistic_name, geojson, clean, quiet):
    if not os.path.exists(file_path) or clean:

        # Make results path
        path_name = os.path.dirname(file_path)
        os.makedirs(os.path.join(path_name), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as geojson_file:
            json.dump(geojson, geojson_file, ensure_ascii=False)

            if not quiet:
                print(f"✓ Blend data from {statistic_name} into {os.path.basename(file_path)}")


def write_json_file(file_path, statistic_name, json_content, clean, quiet):
    if not os.path.exists(file_path) or clean:

        # Make results path
        path_name = os.path.dirname(file_path)
        os.makedirs(os.path.join(path_name), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(json_content, json_file, ensure_ascii=False)

            if not quiet:
                print(f"✓ Aggregate data from {statistic_name} into {os.path.basename(file_path)}")
