import http.server
import json
import os.path
import _thread
import urllib.parse

DOC_DIR = os.path.join(os.path.dirname(__file__), 'mmap_app')


class Server(http.server.HTTPServer):
  def __init__(self, handler, address='', port=9999, module_state=None):
    http.server.HTTPServer.__init__(self, (address, port), handler)
    self.allow_reuse_address = True
    self.module_state = module_state


class Handler(http.server.BaseHTTPRequestHandler):
  def do_GET(self):
    scheme, host, path, params, query, frag = urllib.parse.urlparse(self.path)
    if path == '/data':
      state = self.server.module_state
      data = {'lat': state.lat,
              'lon': state.lon,
              'heading': state.heading,
              'alt': state.alt,
              'airspeed': state.airspeed,
              'groundspeed': state.groundspeed}
      self.send_response(200)
      self.end_headers()
      self.wfile.write(json.dumps(data))
    else:
      # Remove leading '/'.
      path = path[1:]
      # Ignore all directories.  E.g.  for ../../bar/a.txt serve
      # DOC_DIR/a.txt.
      unused_head, path = os.path.split(path)
      # for / serve index.html.
      if path == '':
        path = 'index.html'
      content = None
      error = None
      try:
        import pkg_resources
        name = __name__
        if name == "__main__":
          name = "MAVProxy.modules.mavproxy_mmap.????"
        content = pkg_resources.resource_stream(name, "mmap_app/%s" % path).read()
      except IOError as e:
        error = str(e)
      if content:
        self.send_response(200)
        self.end_headers()
        self.wfile.write(content)
      else:
        self.send_response(404)
        self.end_headers()
        self.wfile.write('Error: %s' % (error,))


def start_server(address, port, module_state):
  server = Server(
    Handler, address=address, port=port, module_state=module_state)
  _thread.start_new_thread(server.serve_forever, ())
  return server
