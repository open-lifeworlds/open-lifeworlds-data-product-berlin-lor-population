import json
import os
import unittest

file_path = os.path.realpath(__file__)
script_path = os.path.dirname(file_path)

data_path = os.path.join(script_path, "..", "..", "data")

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


class FilesTestCase(unittest.TestCase):
    pass


for year in [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]:
    for half_year in ["01", "02"]:
        for lor_area_type in ["districts", "forecast-areas", "district-regions", "planning-areas"]:
            file = os.path.join(data_path, f"{key_figure_group}-{year}-{half_year}",
                                f"{key_figure_group}-{year}-{half_year}-{lor_area_type}.geojson")
            setattr(
                FilesTestCase,
                f"test_{key_figure_group}_{year}_{half_year}_{lor_area_type}".replace('-', '_'),
                lambda self, file=file: self.assertTrue(os.path.exists(file))
            )


class PropertiesTestCase(unittest.TestCase):
    pass


for year in [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]:
    for half_year in ["01", "02"]:
        for lor_area_type in ["districts", "forecast-areas", "district-regions", "planning-areas"]:
            file = os.path.join(data_path, f"{key_figure_group}-{year}-{half_year}",
                                f"{key_figure_group}-{year}-{half_year}-{lor_area_type}.geojson")
            if os.path.exists(file):
                with open(file=file, mode="r", encoding="utf-8") as geojson_file:
                    geojson = json.load(geojson_file, strict=False)

                for feature in geojson["features"]:
                    feature_id = feature["properties"]["id"]
                    setattr(
                        PropertiesTestCase,
                        f"test_{key_figure_group}_{year}_{half_year}_{lor_area_type}_{feature_id}".replace('-', '_'),
                        lambda self, feature=feature: self.assertTrue(
                            all(property in feature["properties"] for property in statistic_properties))
                    )

if __name__ == '__main__':
    unittest.main()
