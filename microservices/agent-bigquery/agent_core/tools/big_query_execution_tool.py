from google.cloud import bigquery
from typing import List, Dict, Any

def query_execution_tool(PROJECT: str, QUERY: str) -> List[Dict[str, Any]]:
    """
    Executes a pre-built SQL query on BigQuery and returns the results as a list of dictionaries.

    Args:
        PROJECT (str): GCP Project ID to execute the query on.
        QUERY (str): The SQL query string to execute.

    Returns:
        List[Dict[str, Any]]: Query results, each row represented as a dictionary.
    """
    client = bigquery.Client(project=PROJECT)
    query_job = client.query(QUERY)
    results = query_job.result()

    return [dict(row.items()) for row in results]
