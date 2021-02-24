import requests

STATUS_OK = 200
STATUS_NOT_MODIFIED = 304


def fetch_job(
    feature_store,
    api_url,
    api_token,
):
    headers = {
        "authorization": f"Token {api_token}"
    }

    # Stream is set to False, so we can have Keep-Alive for pooling purposes.
    response = requests.get(api_url, headers=headers, stream=False)

    if response.status_code != STATUS_OK and response.status_code != STATUS_NOT_MODIFIED:
        # error_callback(response.status_code)
        print('b')
    elif response.status_code == STATUS_OK:
        # success_callback()
        print('a')
        # print(str(response.json()))

        # Maybe this approach can go wrong ? I can see we clearing the dict, executing other python code
        # then we update the feature store. In this scenario, the user could evaluate a flag that we just
        # destroyed. :thinking:
        feature_store.clear()
        feature_store.update(response.json())
