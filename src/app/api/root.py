from html import escape
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from app.core.security import get_optional_user

router = APIRouter()

_PAGE_TEMPLATE = """\
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>FastAPI + Keycloak</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 32rem; margin: 4rem auto; text-align: center; }}
    a.button {{
      display: inline-block; margin-top: 1rem; padding: 0.6rem 1.2rem;
      background: #0b5fff; color: #fff; text-decoration: none; border-radius: 0.4rem;
    }}
  </style>
</head>
<body>
  {body}
</body>
</html>
"""


@router.get("/", response_class=HTMLResponse)
async def read_root(user: dict[str, Any] | None = Depends(get_optional_user)) -> str:  # noqa: B008
    if user is None:
        body = """
          <h1>Welcome</h1>
          <p>Please log in to continue.</p>
          <a class="button" href="/auth/login">Log in</a>
        """
    else:
        name = escape(str(user.get("name", user.get("sub", "there"))))
        body = f"""
          <h1>Hello, {name}!</h1>
          <a class="button" href="/auth/logout">Log out</a>
        """
    return _PAGE_TEMPLATE.format(body=body)


@router.get(path="/favicon.ico", status_code=204)
async def favicon() -> None:
    """Favicon endpoint to suppress 404 warnings."""
