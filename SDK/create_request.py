from typing import Any, Callable
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from SDK.utils import get_api_key, get_lichess_token


def create_request(
    url: str,
    method: str = "GET",
    *,
    content_type: str = "application/json",
    accept: str = "application/json",
    api_key: str | None = None,
    use_bearer: bool = False,
    payload_func: Callable[..., Any] | None = None,
    json: object | None = None,
    data: object | None = None,
    params: dict[str, str] | None = None,
    extra_headers: dict[str, str] | None = None,
    timeout: tuple[int | float, int | float] = (5, 15),
    retries: int = 2,
    backoff_factor: float = 0.5,
    retry_statuses: tuple[int, ...] = (429, 500, 502, 503, 504),
    stream: bool = False,
) -> requests.Response | None:
    """
    Sends an HTTP request with standard headers and resiliency options.
    Args:
        url (str): The target URL for the request.
        method (str): The HTTP method to use (e.g., "GET", "POST").
        content_type (str): The content type for the Content-Type header (default: application/json).
        accept (str): The content type accepted for the Accept header (default: application/json).
        api_key (str): The API key (if not provided, it will be obtained using get_api_key()).
        payload_func (callable): A function that returns the payload; used only if json/data are not passed.
        json (dict): The request body as a JSON object.
        data (dict): The request body as form data.
        params (dict): Query parameters to be included in the URL.
        extra_headers (dict): Additional headers to be included in the request.
        timeout (tuple): Timeout for connection and reading (default: (5, 15)).
        retries (int): The number of retry attempts in case of failure (default: 2).
        backoff_factor (float): The exponential backoff factor for retries (default: 0.5).
        retry_statuses (tuple): Status codes that should trigger a retry (default: (429, 500, 502, 503, 504)).
    Returns:
        Response: The response object from the request, or None in case of failure.
    """
    # Resolve token/key when needed. For Lichess, Bearer token is optional for public data.
    if api_key is None and use_bearer:
        api_key = get_lichess_token()

    headers = {
        "Accept": accept,
        "Content-Type": content_type,
    }
    # Attach auth header if provided
    if api_key:
        if use_bearer:
            headers["Authorization"] = f"Bearer {api_key}"
        else:
            headers["X-API-KEY"] = api_key
    if extra_headers:
        headers.update(extra_headers)

    if payload_func and json is None and data is None:
        try:
            generated = payload_func()
            if content_type == "application/json":
                json = generated
            else:
                data = generated
        except Exception as e:
            print(f"Erro ao gerar payload: {e}")
            return None  # antes retornava sempre, mesmo sem erro
    session = requests.Session()
    retry = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=retry_statuses,
        allowed_methods={"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"},
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    try:
        response: requests.Response = session.request(
            method=method.upper(),
            url=url,
            headers=headers,
            params=params,
            json=json,
            data=data,
            timeout=timeout,
            stream=stream,
        )
        return response
    except requests.exceptions.Timeout:
        print("The request timed out")
        return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
