# utils/visual_config_fetcher.py

from utils.token_checker import _make_api_request_with_retry, refresh_access_token


def get_all_visual_configs(config: dict, log_callback=print) -> list:
    """
    Fetches all visual configurations from the /integration/visual_config/ endpoint.
    """
    log_callback("🔍 Fetching all Visual Configs...")

    # CORRECTED: Use the endpoint path confirmed by your curl command
    url = f"{config['alation_url'].rstrip('/')}/integration/visual_config/"

    response = _make_api_request_with_retry(
        "GET",
        url,
        config,
        token_refresher=refresh_access_token,
        log_callback=log_callback
    )

    if response and response.status_code == 200:
        visual_configs = response.json()
        log_callback(f"✅ Found {len(visual_configs)} Visual Configs.")
        return visual_configs
    else:
        log_callback(
            "❌ Error fetching Visual Configs. This may be a permissions issue or an incorrect endpoint for your Alation version.")
        return []