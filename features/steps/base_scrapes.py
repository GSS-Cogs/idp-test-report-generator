
import json
import logging
import time

from behave import *
from allure_behave.hooks import allure_report
from gssutils import Scraper

from helpers import parse_scrape_to_json

SCRAPER_STATE_KEY = "scraper_state"

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

class MalformedPipelineError(Exception):
    """ Raised when we're unable to acquire the expected json resources at the stated places
    """

    def __init__(self, message):
        self.message = message

@given('we know "{failing_dataset}" is broke')
def step_impl(context, failing_dataset):
    context.malformed_pipeline = failing_dataset

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
    context.scrape = Scraper(seed=context.seed_path)
    time.sleep(5)

@given('we know "{odata_api_scraper}" is an odata api scraper')
def step_impl(context, odata_api_scraper):
    context.odata_api_scraper = odata_api_scraper

@then('pass trivially')
def step_impl(context):
    pass

# A temp scraper is only ok (as-in is acceptable) if the scraper state key literally says so
@then('a temporary scraper has been flagged as an acceptable solution')
def step_impl(context):
    if not context.scrape.seed.get(SCRAPER_STATE_KEY, None) == "ok":
        raise ProvisionalScraperError("A temp scraper is in use but has not being flagged as appropriate." \
            + " A flag must be added or a full scraper implemented to clear this exception")

@then('when we scrape with the url no exception is encountered')
def step_impl(context):
    context.scrape = Scraper(context.url)

@then('no functionality issues have been flagged by the users')
def step_impl(context):
    state = context.scrape.seed.get(SCRAPER_STATE_KEY, None)
    if state is not None:
        if state.strip() != "" and state != "ok":
            raise UserDefinedError(state)

@then('the scraper contains at least one valid distribution')
def step_impl(context):
    err_msg = 'Content fault. The scrape does not appear to contain a distribution'
    try:
        try:
            assert len(context.scrape.distributions) > 0, err_msg
        except:
            context.scrape.select_dataset(latest=True)
            assert len(context.scrape.distributions) > 0, err_msg
    except Exception as err:
        raise Exception(err_msg +'\n' + json.dumps(parse_scrape_to_json(context.scrape), indent=2)) from err

allure_report("./allure-report")
