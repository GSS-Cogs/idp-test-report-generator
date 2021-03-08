
import json
import logging

from behave import *
from allure_behave.hooks import allure_report
from gssutils import Scraper

from helpers import parse_scrape_to_json

@given('we specify the url "{url}"')
def step_impl(context, url):
    context.url = url

@given(u'we use the seed "{seed_path}"')
def step_impl(context, seed_path):
    context.seed_path = seed_path

@then('when we scrape with the seed no exception is encountered')
def step_impl(context):
    context.scrape = Scraper(seed=context.seed_path)

@then('when we scrape with thr url no exception is encountered')
def step_impl(context):
    context.scrape = Scraper(context.url)

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
