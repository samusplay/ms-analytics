import httpx


def get_active_profile():

    url = "http://ms-configuration:8000/api/v1/configuration/profiles/active"

    try:
        response = httpx.get(url)

        if response.status_code == 200:
            return response.json()

        return None

    except Exception as e:
        print(f"Error conectando con ms-configuration: {e}")
        return None