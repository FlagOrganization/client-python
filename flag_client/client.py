from typing import Dict, Any
from threading import Timer, Lock, Event, Thread

from apscheduler.schedulers.background import BackgroundScheduler
import requests


class FeatureStore:

    def __init__(self):
        self._store = {}
        self._lock = Lock()

    def update(self, new_flags: Dict[str, Dict[str, Any]]):
        self._lock.acquire(blocking=True)

        # Clean removed flags
        for key in self._store.keys():
            if key not in new_flags:
                self._store.pop(key)

        # Update existing and add new flags
        self._store.update(new_flags)

        self._lock.release()

    def get(self, key: str) -> Dict:
        self._lock.acquire(blocking=True)

        flag = self._store.get(key, {})

        self._lock.release()

        return flag


class PollingManager:

    def __init__(self, interval, func, *args, **kwargs):
        self.interval = interval
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.start = 2
        self.event = Event()
        self.thread = Thread(target=self._target)

    # fuck this shit. Use APscheduler instead


def fetch_and_load(
    feature_store: FeatureStore,
    api_url: str,
    auth_token: str,
):
    headers = {
        "authorization": f"Token {auth_token}"
    }

    response = requests.get(api_url, headers=headers, stream=False)

    if response.status_code == requests.codes['ok']:
        # HTTP 200
        print("Successfully fetched the Feature Flags. \n")
        feature_store.update(response.json())

    elif response.status_code == requests.codes['not_modified']:
        print("Not modified! \n")

    else:
        print(f"Error while fetching Flags: [{response.status_code}]\n"
              f"Reason: {response.reason}\n")


class FlagClient:

    def __init__(self, interval_seconds, url, token):
        self.feature_store = FeatureStore()
        self.api_url = url
        self.auth_token = token

        # self.timer = Timer(
        #     float(interval_seconds),
        #     fetch_and_load,
        #     [self.feature_store, self.api_url, self.auth_token]
        # )
        # self.timer.name = "Pooling Thread"
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            fetch_and_load,
            'interval',
            seconds=interval_seconds,
            id="PollingJob",
            args=(
                self.feature_store,
                self.api_url,
                self.auth_token,
            )
        )

    def start_client(self):
        # self.timer.daemon = True
        # self.timer.start()
        self.scheduler.start()

    def shutdown(self, wait=True):
        # self.timer.cancel()
        self.scheduler.shutdown(wait=wait)

    @staticmethod
    def _enabled_with_ctx(flag: Dict, context: Dict[str, str]) -> bool:
        """
        Constraints are always String lists. In the dashboard you may set several constraints, each
        with a key, so when you're passing context, they can be compared. Consider this whitelisting
        values.

        :param flag: Dict[str, Any]
        :param context: Dict[str, str]
        :return: Whether the flag is enabled or not
        """
        if not context:
            return False

        constraints = flag['constraints']

        for key in constraints.keys():
            try:
                if str(context[key]) not in constraints[key].split(','):
                    return False
            except KeyError:
                return False

        return True

    def enabled(self, flag_key: str, default: bool = False, context: Dict[str, Any] = None) -> bool:
        flag = self.feature_store.get(flag_key)

        if not flag:
            return default

        if flag.get('constraints', None):
            return self._enabled_with_ctx(flag, context)

        return flag['enabled']
