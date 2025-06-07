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

    print(f"THE SYMBOLOOOOO:{SYMBOL}")

    client = bigquery.Client(project=PROJECT)
    query = """
            SELECT CAST(Date as STRING) AS Date, Open, High, Low, Close, adj_close, Volume, symbol
            FROM `adk-hackathon-460011.tradingdata.historical_trading_data`
            WHERE symbol = @symbol \
            """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("symbol", "STRING", SYMBOL)
        ]
    )
    query_job = client.query(query, job_config=job_config)

    results = query_job.result()
    # print(f"Resul length: {len(results.)}")
    return [dict(row.items()) for row in results]
