"""Serve the course and original notebooks from the same authenticated Jupyter origin."""
from pathlib import Path
from tornado import web
from jupyter_server.base.handlers import APIHandler, AuthenticatedFileHandler, JupyterHandler
from jupyter_server.utils import url_path_join

SITE = Path(__file__).resolve().parents[1]

class CourseAssetHandler(AuthenticatedFileHandler):
    @property
    def content_security_policy(self):
        # Only our fixed, trusted application bundle is served here. Notebook
        # HTML still uses Jupyter's normal sandboxed files handler.
        return JupyterHandler.content_security_policy.fget(self)

class CourseStatusHandler(APIHandler):
    @web.authenticated
    def get(self):
        root = Path(self.settings['server_root_dir']).expanduser().resolve()
        specs = self.kernel_spec_manager.get_all_specs()
        self.finish({
            'connected': True,
            'root': str(root),
            'notebooks': [p.name for p in sorted((root / 'notes').glob('*.ipynb'))],
            'julia_kernel': 'julia-1806' if 'julia-1806' in specs else None,
            'lab_url': url_path_join(self.base_url, 'lab/workspaces/linear-algebra'),
        })

def _jupyter_server_extension_points():
    return [{'module': 'lab_extension'}]

def _load_jupyter_server_extension(serverapp):
    base = serverapp.web_app.settings['base_url']
    serverapp.web_app.add_handlers('.*$', [
        (url_path_join(base, 'learn-api/status'), CourseStatusHandler),
        (url_path_join(base, r'learn/python-runtime/(.*)'), CourseAssetHandler,
         {'path': str(SITE / '.runtime' / 'pyodide')}),
        (url_path_join(base, r'learn/(.*)'), CourseAssetHandler,
         {'path': str(SITE / 'dist'), 'default_filename': 'index.html'}),
    ])
    serverapp.log.info('18.06 learning site and notebook integration enabled.')
