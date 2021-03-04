# Pull the previous results from the google bucket
# NOTE - we're nuking whats in the bucket after we copy it (to clean old kruft before we upload again later)
# longer term, we probably want something a bit less drastic (or a backup at least).
python3 ./download_from_bucket.py

# generate new tests
python3 ./build_dynamic_tests.py

# run test, format output for allure
behave -f allure_behave.formatter:AllureFormatter -o allure-results ./features

# copy in our custom categories (in case we've changed them)
cp ./categories.json ./allure-results/categories.json

# Turn the new reports into test results
docker run -v $PWD:/workspace -w /workspace frankescobar/allure-docker-service /bin/bash -c "allure generate allure-results --clean"

# Update history with previous report stuff, so we can track trends
cp -r $PWD/allure-report/history/. $PWD/allure-results/history

# Write everything back to the google bucket
python3 ./upload_to_bucket.py
