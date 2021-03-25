import backoff
import logging
import json
import requests
import time
import yaml

from behave import *
from allure_behave.hooks import allure_report
from gssutils import Scraper

from helpers import parse_scrape_to_json

# Be a good citizen and avoid rinsing peoples apis 
DELAY_BETWEEN_REQUESTS = 5 # seconds

# exponentially backoff a scrape request if it hits a 429
# shouldnt be necessary with a built in delay, but sadly it is...
def fatal_code(e):
    logging.warning(f'Backoff got response code {e.response.status_code}')
    return e.response.status_code != 429

# retry but backoff scrapes if we hit a 429
@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_time=300, giveup=fatal_code)
def get_scrape(seed_path):
    """Wrap the http get so we can use backoff"""
    return Scraper(seed=seed_path)

# load config once, save us some overhead
with open("config.yaml") as f:
    CONFIG_DICT = yaml.load(f, Loader=yaml.FullLoader)

class ProvisionalScraperError(Exception):
    """ Raised when we're using a temp scraper where a full scraper implementation may be required
    """

    def __init__(self, message):
        self.message = message

class UserDefinedError(Exception):
    """ Raised when a DE has flagged the scraper has missing or inadequte functionality
    """

    def __init__(self, message):
        self.message = message

class KnownEdgeCaseError(Exception):
    """ Raised when a a scraper has a known edge case associated with it
    """

    def __init__(self, message):
        self.message = message

class MalformedPipelineError(Exception):
    """ Raised when we're unable to acquire the expected json resources at the stated places
    """

    def __init__(self, message):
        self.message = message

@given('we know "{failing_dataset}" is broke')
def step_impl(context, failing_dataset):
    context.malformed_pipeline = failing_dataset

@then('bubble up the edge case message "{edgecase_text}"')
def step_omp(context, edgecase_text):
    raise KnownEdgeCaseError(f'This is a known issue: {edgecase_text}') 

@then('bubble up an exception')
def step_impl(context):
    raise MalformedPipelineError(f'The pipeline {context.malformed_pipeline} cannot be tested, something in the config' \
        + ' and/or json files is wrong')

@given('we specify the url "{url}"')
def step_impl(context, url):
    context.url = url

@given(u'we use the seed "{seed_path}"')
def step_impl(context, seed_path):
    context.seed_path = seed_path

@then('when we scrape with the seed no exception is encountered')
def step_impl(context):
    context.scrape = get_scrape(context.seed_path)
    time.sleep(DELAY_BETWEEN_REQUESTS)

@given('we know "{odata_api_scraper}" is an odata api scraper')
def step_impl(context, odata_api_scraper):
    context.odata_api_scraper = odata_api_scraper

@then('pass trivially')
def step_impl(context):
    pass

# A temp scraper is only ok (as-in is acceptable) if the scraper state key literally says so
@then('a temporary scraper for "{dataset}" has been flagged as an acceptable solution')
def step_impl(context, dataset):
    if dataset not in CONFIG_DICT["acceptable_temp_scrapers"]:
        raise ProvisionalScraperError("A temp scraper is in use but has not being flagged as appropriate." \
            + " A flag must be added or a full scraper implemented to clear this exception")

@then('when we scrape with the url no exception is encountered')
def step_impl(context):
    context.scrape = Scraper(context.url)

@then('no functionality issues for "{dataset}" have been flagged by the users')
def step_impl(context, dataset):
    if dataset in CONFIG_DICT["known_gssutils_issues"]:
        raise UserDefinedError(f'Known gssutils issue: "{CONFIG_DICT["known_gssutils_issues"][dataset]}". \n'
            'When said issue has been resolved please update config.yaml to reflect this.')

@then('the scraper contains at least one valid distribution')
def step_impl(context):
    err_msg = 'Content fault. The scrape does not appear to contain a distribution'
    try:
        try:
            assert len(context.scrape.distributions) > 0, err_msg
        except:
            found = False
            for dataset in context.scraper.catalog.dataset:
                if len(dataset.distribution) > 0:
                    found = True
            if not found:
                raise err_msg
    except Exception as err:
        raise Exception(err_msg +'\n' + json.dumps(parse_scrape_to_json(context.scrape), indent=2)) from err

allure_report("./allure-report")
