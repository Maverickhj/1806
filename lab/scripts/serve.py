"""One local Jupyter Server hosts the roadmap and JupyterLab; no CORS bypasses."""
import argparse
import json
import os
from pathlib import Path
import secrets
import sys

SITE = Path(__file__).resolve().parents[1]
RUNTIME = SITE / '.runtime'

def main():
    parser = argparse.ArgumentParser(description='18.06 local learning site with Julia notebooks')
    parser.add_argument('--port', type=int, default=4186)
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    for dirname in ['jupyter-data', 'jupyter-config', 'jupyter-runtime', 'ipython', 'matplotlib']:
        (RUNTIME / dirname).mkdir(parents=True, exist_ok=True)
    os.environ.update({
        'JUPYTER_DATA_DIR': str(RUNTIME / 'jupyter-data'),
        'JUPYTER_CONFIG_DIR': str(RUNTIME / 'jupyter-config'),
        'JUPYTER_RUNTIME_DIR': str(RUNTIME / 'jupyter-runtime'),
        'IPYTHONDIR': str(RUNTIME / 'ipython'),
        'MPLCONFIGDIR': str(RUNTIME / 'matplotlib'),
        'JULIA_DEPOT_PATH': str(RUNTIME / 'julia-depot'),
        'JULIA_PROJECT': str(SITE / 'julia'),
        'PYTHON': str(SITE / '.venv/bin/python'),
        'GKSwstype': '100',
        'MPLBACKEND': 'Agg',
        'JULIA_NUM_THREADS': '1',
    })
    from jupyter_server.serverapp import ServerApp
    from traitlets.config import Config
    token_file = RUNTIME / 'jupyter-token'
    if not token_file.exists():
        fd = os.open(token_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w') as out:
            out.write(secrets.token_urlsafe(32))
    token_file.chmod(0o600)
    config = Config()
    config.ServerApp.ip = '127.0.0.1'
    config.ServerApp.port = args.port
    config.ServerApp.port_retries = 0
    config.ServerApp.root_dir = str(SITE.parent)
    config.ServerApp.default_url = '/learn/'
    config.ServerApp.open_browser = not args.no_browser
    config.ServerApp.allow_remote_access = False
    config.ServerApp.jpserver_extensions = {
        'jupyterlab': True, 'lab_extension': True,
        'webio_jupyter_extension.serverextension': False,
    }
    config.IdentityProvider.token = token_file.read_text().strip()
    config.MappingKernelManager.default_kernel_name = 'julia-1806'
    config.MappingKernelManager.cull_idle_timeout = 3600
    config.MappingKernelManager.cull_connected = False
    config.LabApp.check_for_updates_class = 'jupyterlab.handlers.announcements.NeverCheckForUpdate'
    # Disable only unsolicited update/news requests, not authentication or XSRF.
    config.LabApp.news_url = None
    config.LabApp.extension_manager = "readonly"
    config.LabApp.expose_app_in_browser = True
    app = ServerApp.instance(config=config)
    app.initialize([])
    app.start()

if __name__ == '__main__':
    main()
