import logging
import os

from tatami_behaviors_aws import add_behaviors, get_logger


@add_behaviors()
def handler(event, context):
    name = os.environ["AWS_LAMBDA_FUNCTION_NAME"]

    log, traceId = get_logger()
    log.log(logging.INFO, f"Here I am: {name} ({traceId})")

    return {"Status": "ok"}
