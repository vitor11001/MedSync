from pathlib import Path
import tomllib

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path


def get_project_version() -> str:
    """Lê a versão do projeto a partir do pyproject.toml."""
    pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"

    try:
        with pyproject_path.open("rb") as pyproject_file:
            pyproject_data = tomllib.load(pyproject_file)
        return pyproject_data["project"]["version"]
    except (FileNotFoundError, KeyError, tomllib.TOMLDecodeError):
        return "0.0.0"


admin.site.site_header = f"Portal MedSync v{get_project_version()}"
admin.site.site_title = "Portal MedSync"
admin.site.index_title = "Portal MedSync"

urlpatterns = [
    path('', lambda request: redirect('admin/')),
    path('admin/', admin.site.urls),
    path("api/clinic/", include("clinic.urls")),
]
