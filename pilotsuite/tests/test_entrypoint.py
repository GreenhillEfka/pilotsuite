"""Exercise the production module execution order, not just imports."""
import http.client
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest


class EntrypointTests(unittest.TestCase):
    def test_real_module_reaches_http_health(self):
        root=Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as directory:
            with socket.socket() as probe:
                probe.bind(('127.0.0.1',0)); port=probe.getsockname()[1]
            env={**os.environ, 'PYTHONPATH':str(root/'pilotsuite'),
                 'PILOTSUITE_DATA_DIR':directory, 'PILOTSUITE_OPTIONS':str(Path(directory)/'options.json'),
                 'PILOTSUITE_HOST':'127.0.0.1','PILOTSUITE_PORT':str(port),'SUPERVISOR_TOKEN':''}
            process=subprocess.Popen([sys.executable,'-m','pilotsuite.app'],env=env,cwd=root,
                                     stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
            try:
                deadline=time.monotonic()+10
                while time.monotonic()<deadline:
                    if process.poll() is not None:
                        self.fail('App exited before health: '+process.communicate()[0])
                    connection=http.client.HTTPConnection('127.0.0.1',port,timeout=.5)
                    try:
                        connection.request('GET','/health'); response=connection.getresponse()
                        self.assertEqual(200,response.status); response.read()
                        self.assertTrue((Path(directory)/'selections.sqlite3').exists())
                        break
                    except (ConnectionRefusedError,TimeoutError):
                        time.sleep(.05)
                    finally: connection.close()
                else: self.fail('Module did not become healthy within ten seconds')
            finally:
                process.terminate()
                try: output=process.communicate(timeout=5)[0]
                except subprocess.TimeoutExpired:
                    process.kill(); output=process.communicate()[0]
                self.assertNotIn('NameError',output)
