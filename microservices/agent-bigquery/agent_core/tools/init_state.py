from google.adk.agents.callback_context import CallbackContext
import os
from agent_core.tools.metadata_extraction_tool import bigquery_metdata_extraction_tool

def initialize_state_var(callback_context: CallbackContext):
    PROJECT = os.environ.get("BQ_PROJECT_ID")
    BQ_LOCATION = os.environ.get("BQ_LOCATION")
    DATASET =  os.environ.get("BQ_DATASET_ID")

    callback_context.state["PROJECT"] = PROJECT
    callback_context.state["BQ_LOCATION"] = BQ_LOCATION
    callback_context.state["DATASET"] =DATASET

    bigquery_metadata = bigquery_metdata_extraction_tool(PROJECT=PROJECT,
        BQ_LOCATION=BQ_LOCATION,
        DATASET=DATASET)

    callback_context.state["bigquery_metadata"] = bigquery_metadata

    print("Metadata : " + str(callback_context.state["bigquery_metadata"]))