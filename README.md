
# idp-test-report-generator

Generates allure formatted https://docs.qameta.io/allure reports snapshotting current state of implemented scraper components as used by the idp dissemination projects data transfromation pipelines.

_Note - doesn't just have to be just scrapers, any pass/fail tests that can be formatted for allure could be passed in) but scraper visibiliy is the initial spike focus_.

## How it works:

- Previous results are pulled down from the google bucket.
- BDD tests are created for all combinations of a scraper + source url currently specified in our pipelines.
- BDD tests are ran and a new report is created.
- The previous report/results data (from the bucket: see step 1) is updated to maintain history.
- The now updated report/results are uploaded back to the bucket.

This bucket will be used as the data source for the dashboard (see other repo).


# Adding a new family

Add a new family repo we want to monitor to `families` in `config.yaml`, it'll get picked up on the next run.


## Required Environment Variables

You'll need to set three environment variables to make this work.


| Name    | What is this?  |  Why?  |
|---------|----------------|--------|
| GIT_TOKEN | A github personnal access. | So we can get the scrapers we need to test from the family github repos. |
| GOOGLE_APPLICATION_CREDENTIALS | Path to a .json with your google cloud credentials in. | So you can read/write to the bucket. |
| REPORT_BUCKET_NAME | The bucket to read/write from/to | So you can develop without mangling existing report history |


## Usage 

**Important:** - while you _can_ run this locally to manually update the principle results/reports, that will typically be handled automatically (i.e by Jenkins) so be aware extra arbitrary snapshots could potentially make the dashboard harder to read/understand (i.e 10 snapshots on 1 day of the month, and 1 snapshot on every other day would make for a bit of an odd looking trend). 

So when developing please use your own bucket and point to it with the `REPORT_BUCKET_NAME` var instead.

To run:

- Clone this repo.
- `pipenv install`
- `pipenv shell`
- `chmod +x ./run.sh`
- `./run.sh`
