from google.adk.agents.callback_context import CallbackContext
import os

from agent_core.tools.big_query_execution_tool import fetch_market_historical_data


def initialize_state_var(callback_context: CallbackContext):
    PROJECT = os.environ.get("BQ_PROJECT_ID")
    BQ_LOCATION = os.environ.get("BQ_LOCATION")
    DATASET =  os.environ.get("BQ_DATASET_ID")

    callback_context.state["PROJECT"] = PROJECT
    callback_context.state["BQ_LOCATION"] = BQ_LOCATION
    callback_context.state["DATASET"] =DATASET

    # bigquery_metadata = fetch_market_historical_data(PROJECT=PROJECT)
    #
    # callback_context.state["bigquery_metadata"] = bigquery_metadata
    #
    # print("Metadata : " + str(callback_context.state["bigquery_metadata"]))