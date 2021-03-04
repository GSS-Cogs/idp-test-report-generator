
python3 ./download_from_bucket.py
python3 ./build_dynamic_tests.py
behave -f allure_behave.formatter:AllureFormatter -o allure-results ./features
cp ./categories.json ./allure-results/categories.json