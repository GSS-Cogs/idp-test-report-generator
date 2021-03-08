import datetime

IGNORE_AT_SCRAPE_LEVEL = [
    "catalog",
    "dataset",
    "session",
    "_base_uri",
    "_dataset_id",
    "_graph",
    "_uri",
    "session"
]

IGNORE_AT_CATALOG_LEVEL = [
    "_graph",
    "_uri",
    "session"
]

IGNORE_AT_DATASET_LEVEL = [
    "_graph",
    "_uri",
    "session"
]

IGNORE_AT_DISTRIBUTION_LEVEL = [
    "_graph",
    "_uri",
    "session"
]


def type_parse(value):

    if isinstance(value, datetime.date):
        return value.strftime("%Y-%m-%dT%H:%M:%S")

    return value


def parse_distribution_to_json(distribution_scrape):

    list_of_distributions_as_dict = []
    for distribution in distribution_scrape:
        distribution_as_dict = {}
        for k, v in distribution.__dict__.items():
            if k not in IGNORE_AT_DISTRIBUTION_LEVEL and not k.startswith("_"):
                distribution_as_dict[k] = type_parse(v)
        list_of_distributions_as_dict.append(distribution_as_dict)
    return list_of_distributions_as_dict

def parse_dataset_to_json(scrape_dataset):

    list_of_datasets_as_dict = []
    for dataset in scrape_dataset:
        dataset_as_dict = {}
        for k, v in dataset.__dict__.items():
            if k not in IGNORE_AT_DATASET_LEVEL and not k.startswith("_"):
                if k == "distribution":
                    dataset_as_dict[k] = parse_distribution_to_json(dataset.__dict__["distribution"])
                else:
                    dataset_as_dict[k] = type_parse(v)
        list_of_datasets_as_dict.append(dataset_as_dict)
    return list_of_datasets_as_dict


def parse_catalog_to_json(scrape_catalog):

    cataog_as_dict = {}
    for k, v in scrape_catalog.__dict__.items():
        if k not in IGNORE_AT_CATALOG_LEVEL and not k.startswith("_"):
            if k == "dataset":
                cataog_as_dict["dataset"] = parse_dataset_to_json(scrape_catalog.__dict__["dataset"])
            else:
                cataog_as_dict[k] = type_parse(v)
    return cataog_as_dict


def parse_scrape_to_json(scrape):

    # First, get the top level scrape data
    scrape_as_dict = {}
    for k,v in scrape.__dict__.items():
        if k not in IGNORE_AT_SCRAPE_LEVEL and not k.startswith("_"):
            scrape_as_dict[k] = type_parse(v)

    # add the catalog
    scrape_as_dict["catalog"] = parse_catalog_to_json(scrape.__dict__["catalog"])

    # add any top level distributions
    scrape_as_dict["distributions"] = parse_distribution_to_json(scrape.__dict__["distributions"])

    return scrape_as_dict
