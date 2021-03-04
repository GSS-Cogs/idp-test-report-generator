
import os
from os import listdir
import json
import yaml

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
    if r.status_code != 200:
        raise Exception(f'Faile to get {url} with status code {r.status_code}')

    try:
        info_dict = r.json()
    except Exception as err:
        raise Exception(f'Failed to convert response from url {url} into a dictionary') from err

    return info_dict


def build_per_scraper_temp_scenario(info_json_path, dataset):
    """
    Create a scenario for a temp scraper
    """
    return f"""
  Scenario: Temp Scraper for {dataset}
    Given we specify the info json "{info_json_path}"
    Then when we scrape no exception is encountered 
    """

def build_per_scraper_non_temp_scenario(landing_page, dataset):
    """
    Given a scraper and a url, write the test scenario
    """
    return f"""
  Scenario: Scraper for {dataset}
    Given we specify the url "{landing_page}"
    Then when we scrape no exception is encountered 
    """

g = git_if_needed()
[os.remove(f'./features/{f}') for f in listdir("./features") if f.endswith(".feature")]

with open("./config.yaml") as f:
    config_dict = yaml.load(f, Loader=yaml.FullLoader)
    familes = config_dict["families"]

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
        file_content = contents.pop(0)
        if file_content.type == "dir" and "." not in content_file.path and 'Makefile' not in content_file.path:

            info_url = f'https://raw.githubusercontent.com/{family}/master/{content_file.path}/info.json'
            info_dict = info_as_dict(info_url)

            # TODO
            if "dataURL" in info_dict.keys():
                seed = "./info.json"
                
                with open(seed, 'w') as f:
                    json.dump(info_dict, f)

                scenario = build_per_scraper_temp_scenario(info_dict, f'{content_file.path.split("/")[1]}')
                with open(f"./features/{family.split('/')[1]}-temp-scrapers.feature", 'a') as f_temp:
                    f_temp.write("\n")
                    f_temp.write(scenario)

            # Multiple landingPage urls specified
            elif isinstance(info_dict["landingPage"], list):
                for i, url in enumerate(info_dict["landingPage"]):
                    scenario = build_per_scraper_non_temp_scenario(url, f'{content_file.path.split("/")[1]}_{i}')
                    with open(f"./features/{family.split('/')[1]}-multi-url-scrapers.feature", 'a') as f_multi:
                        f_multi.write("\n")
                        f_multi.write(scenario)

            # Single landing page specified
            else:
                with open(f"./features/{family.split('/')[1]}-standard-scrapers.feature", 'a') as f_base:
                    scenario = build_per_scraper_non_temp_scenario(info_dict["landingPage"], content_file.path.split('/')[1])
                    f_base.write("\n")
                    f_base.write(scenario)


