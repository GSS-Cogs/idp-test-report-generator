
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


def info_as_dict(url):
    r = requests.get(url)
    if r.status_code != 200 and r.status_code != 404:
        raise Exception(f'Faile to get {url} with status code {r.status_code}')

    if r.status_code == 404:
        print(f'got a 404 for {url}')
        return None

    try:
        info_dict = r.json()
    except Exception as err:
        raise Exception(f'Failed to convert response from url {url} into a dictionary') from err

    return info_dict


def build_failing_test_for_malformed_pipeline(failing_dataset):
    """
    Create simple fail scenarios for visibility
    """
    return f"""
  Scenario: The pipeline for {failing_dataset} is broken
    Given we know "{failing_dataset}" is broke
    Then bubble up an exception
    """

def build_test_with_seed(info_json_path, dataset, is_temp=False):
    """
    Create a scenario for using a scraper from a seed
    """
    mod_text = "Temp " if is_temp else ""

    # Test the scraper content is adequate
    if is_temp:
        contents_check1 = "And a temporary scraper has been flagged as an acceptable solution"
    else:
        contents_check1 = "And the scraper contains at least one valid distribution"

    return f"""
  Scenario: {mod_text}Scraper for {dataset}
    Given we use the seed "{info_json_path}"
    Then when we scrape with the seed no exception is encountered
    And no functionality issues have been flagged by the users
    {contents_check1}
    """

def build_test_with_url(url, dataset, is_temp=False):
    """
    Create a scenario for using a scraper from a simple url
    """
    mod_text = "Temp " if is_temp else ""
    return f"""
  Scenario: {mod_text}Scraper for {dataset}
    Given we specify the url "{url}"
    Then when we scrape with the url no exception is encountered 
    """

g = git_if_needed()
[os.remove(f'./features/{f}') for f in listdir("./features") if f.endswith(".feature")]

with open("./config.yaml") as f:
    config_dict = yaml.load(f, Loader=yaml.FullLoader)
    familes = config_dict["families"]

seed_path = Path("out/seeds")
seed_path.mkdir(exist_ok=True, parents=True)

# Scrapers we are unable to test for whatever reason (typically, the Jenkins job/info.json is malformed)
# Note: this is a bit hacky, but we're gonna creata a feature of tests that always
# fail, so an appropriate exception per malformed pipeline bubbles up and can be categorised for the dashboard
with open(f"./features/malformed.feature", 'w+') as f_base:
    f_base.write(f"""Feature: Pipeline Not Correctly Configured
As a data engineer.
I want to know when the configuration for a pipeline is malformed.
""".lstrip('\n'))


for family in familes:

    # Base (i.e standard) scrapers
    with open(f"./features/{family.split('/')[1]}-standard-scrapers.feature", 'w+') as f_base:
        f_base.write(f"""Feature: {family.split('/')[1]} - Scrapers
    As a data engineer.
    I want to know that what base scrapers are in use by our pipelines.
    I want to know each base scraper completes without error with our chosen urls
    """.lstrip('\n'))

    # Temp scrapers
    with open(f"./features/{family.split('/')[1]}-temp-scrapers.feature", 'w+') as f_temp:
        f_temp.write(f"""Feature: {family.split('/')[1]} - Temp Scrapers
    As a data engineer.
    I want to know that what temp base scrapers are in use by our pipelines.
    I want to know each temp scraper completes without error with our chosen urls
    """.lstrip('\n'))

    # Multi url scrapers
    with open(f"./features/{family.split('/')[1]}-multi-url-scrapers.feature", 'w+') as f_multi:
        f_multi.write(f"""Feature: {family.split('/')[1]} - Multi-URI Scrapers
    As a data engineer.
    I want to know that what multi url scrapers are in use by our pipelines.
    I want to know each multi url scraper completes without error with our chosen urls
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
                with open(f"./features/malformed.feature", 'a') as f_malformed:
                    f_malformed.write(scenario)
                continue

            info_dict_path = f"./out/seeds/{pipeline}_info.json"
            with open(info_dict_path, "w") as f:
                json.dump(info_dict, f, indent=2)
                
            # Multiple landingPage urls specified
            if isinstance(info_dict.get("landingPage", None), list):
                for i, url in enumerate(info_dict["landingPage"]):
                    scenario = build_test_with_url(url, f'{pipeline}_{i}', is_temp="dataURL" in info_dict.keys())
                    with open(f"./features/{family.split('/')[1]}-multi-url-scrapers.feature", 'a') as f_multi:
                        f_multi.write("\n")
                        f_multi.write(scenario)

            # Single landing page specified
            else:
                if "dataURL" in info_dict.keys():
                    with open(f"./features/{family.split('/')[1]}-temp-scrapers.feature", 'a') as f_temp:
                        scenario = build_test_with_seed(info_dict_path, pipeline, is_temp=True)
                        f_temp.write("\n")
                        f_temp.write(scenario)
                else:
                    with open(f"./features/{family.split('/')[1]}-standard-scrapers.feature", 'a') as f_base:
                        scenario = build_test_with_seed(info_dict_path, pipeline, is_temp=False)
                        f_base.write("\n")
                        f_base.write(scenario)
