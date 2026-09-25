"""Progressive workspace shell. The existing HTML and configuration owners stay canonical."""
from pathlib import Path
from aiohttp import web

ASSETS = ("workspace-model.js", "workspace.js", "workspace.css")


def workspace_page(web_dir: Path) -> str:
    """Enhance the one canonical document, keeping a functional no-JS fallback."""
    source = (web_dir / "index.html").read_text(encoding="utf-8")
    source = source.replace('</head>', '<link rel="stylesheet" href="assets/workspace.css">\n  </head>')
    return source.replace('</body>', '<script src="assets/workspace-model.js" defer></script>\n'
                          '    <script src="assets/workspace.js" defer></script>\n  </body>')


def register_workspace(app: web.Application, web_dir: Path) -> None:
    async def asset(request: web.Request) -> web.Response:
        name = request.match_info["name"]
        if name not in ASSETS:
            raise web.HTTPNotFound()
        return web.FileResponse(web_dir / name, headers={"Cache-Control": "no-cache"})
    app.router.add_get('/assets/{name:workspace(?:-model)?\\.js|workspace\\.css}', asset)
