# Pull the previous results from the google bucket then generate new test reports
# NOTE - we're nuking whats in the bucket after we copy it (to clean old kruft before we uplaod again later)
# longer term, we probably want something a bit less drastic (or a backup at least).
./generate_results.sh

# Turn the new reports into test results
docker run -v $PWD:/workspace -w /workspace frankescobar/allure-docker-service /bin/bash -c "allure generate allure-results --clean"

# Update history with previous report stuff, so we can track trends
cp -r $PWD/allure-report/history/. $PWD/allure-results/history

# Write everything back to the google bucket
python3 ./upload_to_bucket.py