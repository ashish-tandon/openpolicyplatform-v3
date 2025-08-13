import time, random, requests

def polite_get(url, timeout=20, retries=3, user_agent="OpenPolicyBot/1.0"):
    last_exc = None
    headers = {"User-Agent": user_agent}
    for i in range(retries):
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            if 200 <= resp.status_code < 400:
                return resp
        except Exception as e:
            last_exc = e
        time.sleep((i+1) + random.random())
    if last_exc:
        raise last_exc
    raise RuntimeError(f"Failed to fetch {url}")