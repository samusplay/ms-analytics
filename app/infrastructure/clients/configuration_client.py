import requests

CONFIG_SERVICE_URL = "http://127.0.0.1:8004/api/v1/profiles/"

def get_active_profile():
    try:
        response = requests.get(CONFIG_SERVICE_URL)
        response.raise_for_status()
        profiles = response.json()

        # 👉 Buscar el activo
        active_profile = next((p for p in profiles if p.get("is_active")), None)

        if not active_profile:
            raise Exception("No hay perfil activo")

        return active_profile

    except Exception as e:
        print(f"Error obteniendo configuración: {e}")
        return None