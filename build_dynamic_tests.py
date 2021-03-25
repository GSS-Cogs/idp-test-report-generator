
import os
from os import listdir
import json
import yaml
from pathlib import Path

from github import Github
import requests

def git_if_needed() -> Github():

    token = os.environ.get("GIT_TOKEN", None)
    if token is None:
        raise Exception('Aborting. No GIT_TOKEN env variable has been set.')
    
    try:
        g = Github(token)
    except Exception as err:
        raise Exception('Unable to create PyGithub class from acces token') from err

    return g


def info_as_dict(url: str) -> (str):
    r = requests.get(url)
    
    if r.status_code != 200 and r.status_code != 404:
        raise Exception(f'Failed to get {url} with status code {r.status_code}')

    if r.status_code == 404:
        print(f'got a 404 for {url}')
        return None

    try:
        info_dict = r.json()
    except Exception as err:
        raise Exception(f'Failed to convert response from url {url} into a dictionary') from err

    return info_dict


def build_failing_test_for_known_edge_case(failing_dataset: str, edgecase_text: str) -> (str):
    """
    Create simple fail scenarios for visibility
    """
    return f"""
  Scenario: Scraper for {failing_dataset}
    Given we know "{failing_dataset}" is broke
    Then bubble up the edge case message "{edgecase_text}"
    """

def build_failing_test_for_malformed_pipeline(failing_dataset: str) -> (str):
    """
    Create simple fail scenarios for visibility
    """
    return f"""
  Scenario: Scraper for {failing_dataset}
    Given we know "{failing_dataset}" is broke
    Then bubble up an exception
    """


# TODO - not a path the is it?
def build_test_for_odata_api_scraper(info_json_path :str, dataset: str, is_temp: bool = False) -> (str):
    """
    Simple passing scanrio for odata scrapers
    NOTE: bit beyond our scope here to tests these
    """
    return f"""
  Scenario: Scraper for {dataset}
    Given we know "{dataset}" is an odata api scraper
    Then pass trivially
    """

# TODO - not a path the is it?
def build_test_with_seed(info_json_path: str, dataset: str, is_temp: bool =False) -> (str):
    """
    Create a scenario for using a scraper from a seed
    """

    # Test the scraper content is adequate
    if is_temp:
        contents_check1 = f'And a temporary scraper for "{dataset}" has been flagged as an acceptable solution'
    else:
        contents_check1 = "And the scraper contains at least one valid distribution"

    return f"""
  Scenario: Scraper for {dataset}
    Given we use the seed "{info_json_path}"
    Then when we scrape with the seed no exception is encountered
    And no functionality issues for "{dataset}" have been flagged by the users
    {contents_check1}
    """

def build_test_with_url(url, dataset:str , is_temp: bool = False) -> (str):
    """
    Create a scenario for using a scraper from a simple url
    """
    mod_text = "Temp " if is_temp else ""
    return f"""
  Scenario: Scraper for {dataset}
    Given we specify the url "{url}"
    Then when we scrape with the url no exception is encountered 
    """

g = git_if_needed()
[os.remove(f'./features/{f}') for f in listdir("./features") if f.endswith(".feature")]

with open("./config.yaml") as f:
    config_dict = yaml.load(f, Loader=yaml.FullLoader)
    familes = config_dict["families"]
    known_issues = config_dict["known_issues"]

seed_path = Path("out/seeds")
seed_path.mkdir(exist_ok=True, parents=True)

for family in familes:

    feature_path = f"./features/{family.split('/')[1]}-scrapers.feature"
    # Base (i.e standard) scrapers
    with open(feature_path, 'w+') as f:
        f.write(f"""Feature: {family.split('/')[1]} - Scrapers
    As a data engineer.
    I want to know that what base scrapers are in use by our pipelines.
    I want to know each base scraper completes without error with our chosen urls
    """.lstrip('\n'))

    repo = g.get_repo(family)
    contents = repo.get_contents("datasets")
    for content_file in contents:

        if content_file.path != 'datasets/info.json':
            continue

        root_info_json_url = f'https://raw.githubusercontent.com/{family}/master/{content_file.path}'
        r = requests.get(root_info_json_url)
        if r.status_code != 200:
            raise Exception(f'Unable to get root info json from {root_info_json_url}')

        root_info_as_dict = r.json()

        with open(f"./{family.split('/')[1]}.json", "w") as f:
            json.dump(root_info_as_dict, f, indent=2)

        for pipeline in root_info_as_dict["pipelines"]:
            
            info_url = f'https://raw.githubusercontent.com/{family}/master/datasets/{pipeline}/info.json'
            info_dict = info_as_dict(info_url)

            if info_dict is None: # denotes a 404
                scenario = build_failing_test_for_malformed_pipeline(pipeline)
                with open(feature_path, 'a') as f:
                    f.write(scenario)
                continue

            info_dict_path = f"./out/seeds/{pipeline}_info.json"
            with open(info_dict_path, "w") as f:
                json.dump(info_dict, f, indent=2)

            # If it's a known issue, catch with a suitable error
            if pipeline in known_issues:
                scenario = build_failing_test_for_known_edge_case(pipeline, known_issues[pipeline])
                with open(feature_path, 'a') as f:
                    f.write("\n")
                    f.write(scenario)
                    
            # Multiple landingPage urls specified
            elif isinstance(info_dict.get("landingPage", None), list):
                for i, url in enumerate(info_dict["landingPage"]):
                    scenario = build_test_with_url(url, f'{pipeline}_{i}', is_temp="dataURL" in info_dict.keys())
                    with open(feature_path, 'a') as f:
                        f.write("\n")
                        f.write(scenario)

            # Single landing page specified
            else:
                if "dataURL" in info_dict:

                    if "odataConversion" in info_dict:
                        with open(feature_path, 'a') as f:
                            scenario = build_test_for_odata_api_scraper(info_dict_path, pipeline, is_temp=True)
                            f.write("\n")
                            f.write(scenario)
                    else:
                        with open(feature_path, 'a') as f:
                            scenario = build_test_with_seed(info_dict_path, pipeline, is_temp=True)
                            f.write("\n")
                            f.write(scenario)
                else:
                    with open(feature_path, 'a') as f:
                        scenario = build_test_with_seed(info_dict_path, pipeline, is_temp=False)
                        f.write("\n")
                        f.write(scenario)
