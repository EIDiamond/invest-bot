import logging

from tinkoff.invest import InvestError, RequestError, AioRequestError

logger = logging.getLogger(__name__)


# Method extends logging for Tinkoff api request if it has been failed
def invest_error_logging(func):
    def log_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RequestError as ex:
            tracking_id = ex.metadata.tracking_id if ex.metadata else ""
            logger.error("RequestError tracking_id=%s code=%s repr=%s details=%s",
                         tracking_id, str(ex.code), repr(ex), ex.details)
            raise ex
        except AioRequestError as ex:
            # tracking_id = ex.metadata.tracking_id if ex.metadata else ""
            logger.error("AioRequestError code=%s repr=%s details=%s",
                         str(ex.code), repr(ex), ex.details)
            raise ex
        except InvestError as ex:
            logger.error("InvestError repr=%s", repr(ex))
            raise ex

    return log_wrapper
