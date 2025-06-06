from google.cloud import bigquery
from typing import List, Dict, Any

def fetch_market_historical_data(PROJECT: str, SYMBOL: str) -> List[Dict[str, Any]]:
    """
    Executes a pre-built SQL query on BigQuery and returns the results as a list of dictionaries.

    Args:
        PROJECT (str): GCP Project ID to execute the query on.
        QUERY (str): The SQL query string to execute.

    Returns:
        List[Dict[str, Any]]: Query results, each row represented as a dictionary.
    """
    client = bigquery.Client(project=PROJECT)
    query_job = client.query("SELECT * FROM `adk-hackathon-460011.tradingdata.historical_trading_data` WHERE symbol = '" + SYMBOL + "';")
    results = query_job.result()

    return [dict(row.items()) for row in results]
