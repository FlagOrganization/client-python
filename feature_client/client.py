from apscheduler.schedulers.background import BackgroundScheduler
from .fetch_flags import fetch_job
from .logger import LOGGER

FETCH_JOB_ID = "fetch_job"


class FeatureClient:

    """
    Hello there. This client spawns another Thread to keep polling Feature Flags from the our
    servers over HTTP.

    The flags are stored in a simple dict, as long as the project has the GIL protecting it, this
    practice is Thread-Safe. The Python GIL makes sure only one threads runs at a time, there is no parallelism.

    For some fucking reason, it seems that APScheduler creates infinite threads:
    https://github.com/agronholm/apscheduler/issues/207
    """

    def __init__(
        self,
        url: str = "http://localhost:8000/fetch?project-id=2&environment-id=1",
        interval_seconds: int = 20,
        api_token: str = None,
        log_success: bool = True,
        log_error: bool = True,
    ):
        self.api_url = url
        self.scheduler = BackgroundScheduler()
        self.interval = interval_seconds
        self.feature_store = {}
        self.api_token = api_token
        self.log_success = log_success
        self.log_error = log_error

    # Flag methods

    def enabled(self, flag_name, default_state=False):
        try:
            return self.feature_store[flag_name]['enabled']
        except KeyError:
            return default_state

    # == All other types of output, like string, json or int will have their own methods.
    # E.g.: getIntVariant

    # Scheduler methods

    def start(self):
        self.scheduler.add_job(
            fetch_job,
            'interval',
            seconds=self.interval,
            id=FETCH_JOB_ID,
            args=(
                self.feature_store,
                self.api_url,
                self.api_token
            )
        )
        self.scheduler.start()

    def stop(self):
        self.scheduler.remove_job(FETCH_JOB_ID)

    def shutdown(self, wait=True):
        self.scheduler.shutdown(wait=wait)

    # Callbacks
    def on_fetch_success(self):
        if not self.log_success:
            return
        print("SUCCESS CARALHO")
        LOGGER.info("Successfully fetched flags.")

    def on_fetch_error(self, status_code):
        if not self.log_error:
            return
        print("ERRO CARALHO")
        LOGGER.error(f"Failed to fetch feature flags."
                     f"\nStatus Code: [{status_code}]")
