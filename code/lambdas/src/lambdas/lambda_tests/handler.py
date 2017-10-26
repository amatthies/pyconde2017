import sys
from pathlib import Path

import pandas as pd


def country_test() -> pd.DataFrame:
    f = Path('country_data.tsv')
    more_country_data = pd.read_table(f)
    df = more_country_data[['name_short', 'ISO2']]
    df = df.rename(columns={'name_short': 'country_name',
                            'ISO2': 'country_code2'})
    return df


def lambda_handler(event, context):
    country_columns = country_test().columns.tolist()

    return {
        'message': 'Returning from python handler',
        'sys.path': sys.path,
        'version': sys.version,
        'country_columns': country_columns
    }
