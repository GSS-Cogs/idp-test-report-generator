
from behave import *
from allure_behave.hooks import allure_report

from gssutils import Scraper

@given('we specify the url "{url}"')
def step_impl(context, url):
    context.url = url
    
@then('when we scrape no exception is encountered')
def step_impl(context):
    Scraper(context.url)

allure_report("./allure-report")
