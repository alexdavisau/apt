# utils/template_fetcher.py

from utils.token_checker import _make_api_request_with_retry, refresh_access_token


def get_template_details(config: dict, template_id: int, log_callback=print) -> dict:
    """
    Fetches the full details for a single template from the API.
    """
    if not template_id:
        return {}

    log_callback(f"🔍 DEBUG: Fetching full details for Template ID: {template_id}...")
    url = f"{config['alation_url'].rstrip('/')}/integration/v1/custom_template/{template_id}/"

    response = _make_api_request_with_retry(
        "GET",
        url,
        config,
        token_refresher=refresh_access_token,
        log_callback=log_callback
    )

    if response and response.status_code == 200:
        template_details = response.json()
        log_callback(f"✅ DEBUG: Successfully fetched details for Template ID: {template_id}")
        return template_details
    else:
        log_callback(f"❌ DEBUG: Error fetching details for Template ID {template_id}.")
        return {}