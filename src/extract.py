import os
import pandas as pd

from scraper import run_scrape


def get_data(search_area, limit=None):
    """
    This function reads the data from a csv file if it exists,
    otherwise it runs the web extraction and saves the data to a csv file
    :param limit: maximum number of properties to scrape
    :param search_area: Region to search for
    :return: DataFrame with sold properties
    """
    data_path = os.path.abspath(r'saved_extracts')
    os.makedirs(data_path, exist_ok=True)

    csv_filename = os.path.join(data_path, f'{search_area}.csv')

    if os.path.exists(csv_filename):
        sold_properties_df = pd.read_csv(csv_filename)
        sold_properties_df['dateSold'] = pd.to_datetime(sold_properties_df['dateSold'])
    else:
        sold_properties_df = run_scrape(search_area, limit=limit)
        sold_properties_df.to_csv(csv_filename, index=False)

    return sold_properties_df
