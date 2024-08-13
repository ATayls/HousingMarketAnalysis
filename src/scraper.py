import json
import random
import time

from requests import get
import pandas as pd
import numpy as np
from datetime import datetime

from geo_utils import get_lat_lon


def create_url(search_area: str, property_type: str, tenure: str, page: int, years: int) -> str:
    return f'https://www.rightmove.co.uk/house-prices/{search_area}.html?propertyType={property_type}&soldIn={years}&tenure={tenure}&page={page}'


def send_property_search_request(url: str) -> pd.DataFrame:
    """
    This function sends a request to the rightmove website and returns the data
    :param url:
    :return:
    """
    # random wait time before request
    time.sleep(random.randint(1, 20)/10)
    html = get(url).text

    start = '<script>window.__PRELOADED_STATE__ = '
    end   = '</script>'
    j = html[html.find(start) + len(start):]
    j = j[:j.find(end)]

    results = json.loads(j)
    property_dict = results['results']['properties']

    return pd.DataFrame.from_dict(property_dict)


def raw_scrape_all(search_area: str, limit: int = None) -> pd.DataFrame:
    """
    This function scrapes all the data in its raw format
    :param limit:
    :param search_area:
    :return:
    """
    main_df = pd.DataFrame()
    row_counter = 0
    for property_type in ['SEMI_DETACHED', 'TERRACED', 'DETACHED', 'FLAT']:
        for tenure in ['FREEHOLD', 'LEASEHOLD']:
            subset_df = pd.DataFrame()
            page = 0
            while True:

                if limit is not None and row_counter > limit:
                    break

                page += 1
                search_url = create_url(search_area, property_type, tenure, page, 7)
                print(f'Requesting url: {search_url}')
                df = send_property_search_request(search_url)

                if df.empty:
                    break

                if subset_df.duplicated(subset='address').sum() > 50:
                    break

                subset_df = pd.concat([subset_df, df])
                row_counter += len(df)

            main_df = pd.concat([main_df, subset_df])

    if limit is not None:
        main_df = main_df.head(limit)

    return main_df


def process_raw_data(raw_df):
    """
    This function formats the raw data into a more readable format
    A more accurate location is also calculated
    :param raw_df:
    :return:
    """
    raw_df['town'] = raw_df['address'].apply(lambda x: x.split(',')[2].strip())
    raw_df['road'] = raw_df['address'].apply(lambda x: x.split(',')[1].strip())
    raw_df['number'] = raw_df['address'].apply(lambda x: x.split(',')[0].strip())
    raw_df['postcode'] = raw_df['address'].apply(lambda x: x.split(',')[-1][-7:].strip())
    raw_df['location'] = raw_df.apply(
        lambda row: get_lat_lon(row['number'], row['road'], row['town'], row['location']), axis=1)
    raw_df['lat'] = raw_df['location'].apply(lambda x: x['lat'])
    raw_df['lon'] = raw_df['location'].apply(lambda x: x['lng'])

    return raw_df


def create_transaction_list(raw_df):
    """
    This function creates a list of transactions from the raw data.
    Iterating over the transactions column and creating a new row for each transaction
    :param raw_df:
    :return:
    """
    transaction_list_of_dicts = []
    for row_num, row in raw_df.iterrows():
        address = row['address']
        trans = row['transactions']
        for t in trans:
            t['address'] = address
            transaction_list_of_dicts.append(t)

    transaction_df = pd.DataFrame.from_dict(transaction_list_of_dicts)

    # Formatting
    transaction_df['dateSold'] = pd.to_datetime(transaction_df['dateSold'])
    transaction_df['displayPrice'] = transaction_df['displayPrice'].replace('[\£,]', '', regex=True).astype(int)
    transaction_df['months_before_today'] = (
                (transaction_df['dateSold'] - datetime.now()) / np.timedelta64(1, 'D')
    ).astype('int') / 30

    return transaction_df


def run_scrape(search_area, limit=None):
    """
    This function runs the web scraping process
    :param limit:
    :param search_area:
    :return:
    """
    raw_df = raw_scrape_all(search_area, limit=limit)
    main_df = process_raw_data(raw_df)

    transaction_df = create_transaction_list(main_df)

    joined_df = pd.merge(transaction_df, main_df, on='address', how="left")
    joined_df = joined_df.drop('transactions', axis=1)

    joined_df = joined_df.drop_duplicates(subset=['address', 'dateSold'])

    return joined_df
