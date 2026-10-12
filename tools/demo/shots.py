#!/usr/bin/env python3
# The book's pictures of the demo fleet (fleet.sh up first): a console of
# its own in /tmp/adc, signed in to with Chromium's virtual security
# key through chromedriver, the three hosts added, and each page
# photographed by its address.  Python's own library only.
#
#	shots.py ARCANA-TREE OUT-DIR

import base64, json, os, shutil, socket, subprocess, sys, time, urllib.request

tree, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
C = '/tmp/adc'
HOSTS = {'hq': '192.0.2.10', 'branch-a': '192.0.2.20',
         'branch-b': '192.0.2.30'}


def free_port():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    p = s.getsockname()[1]
    s.close()
    return p


def wait(cond, secs, what):
    t = time.time() + secs
    while time.time() < t:
        if cond():
            return
        time.sleep(0.25)
    raise SystemExit('shots.py: timed out waiting for ' + what)


port, wdport = free_port(), free_port()
shutil.rmtree(C, ignore_errors=True)
os.makedirs(C + '/data', mode=0o700)
os.makedirs(out, exist_ok=True)
so = tree + '/obj/www/arcana-console/arcana-console.so'
routes = tree + '/www/arcana-console/conf/routes.conf'
web = tree + '/obj/www/arcana-ui/dist'
kore = tree + '/build/kore-src/kore'
dh = tree + '/build/kore-src/misc/ffdhe4096.pem'
open(C + '/web.conf', 'w').write(
    'rp_id = "localhost";\norigin = "http://localhost:%d";\n'
    'datadir = "%s/data";\ncookie_secure = false;\nlocal_agent = "";\n'
    'update_check = false;\ntls {\n\tca = "/tmp/ad/ca.pem";\n'
    '\tcert = "/tmp/ad/client.pem";\n\tkey = "/tmp/ad/client.key";\n}\n'
    % (port, C))
open(C + '/kore.conf', 'w').write(
    'server t {\n\tbind 127.0.0.1 %d\n\ttls no\n}\n'
    'load %s arcw_onload\ntls_dhparam %s\nworkers 1\ntask_threads 8\n'
    'http_body_max 1048576\nfilemap_index index.html\n'
    'http_media_type application/wasm wasm\n'
    'http_media_type application/manifest+json webmanifest\n'
    'http_media_type image/svg+xml svg\nhttp_media_type font/woff2 woff2\n'
    'domain * {\n\tattach t\n\tinclude %s\n\tfilemap / %s\n}\n'
    % (port, so, dh, routes, web))
env = dict(os.environ, ARCANA_WEB_CONF=C + '/web.conf')
procs = [subprocess.Popen([kore, '-f', '-n', '-r', '-c', C + '/kore.conf'],
                          cwd=C, env=env, stdout=open(C + '/kore.out', 'w'),
                          stderr=subprocess.STDOUT),
         subprocess.Popen(['chromedriver', '--port=%d' % wdport],
                          stdout=open(C + '/chromedriver.out', 'w'),
                          stderr=subprocess.STDOUT)]
sid = None


def wd(method, path, body=None):
    # "/session/x" is of the session made: its id goes in.
    if sid and path.startswith('/session/'):
        path = '/session/' + sid + path[len('/session'):]
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request('http://127.0.0.1:%d%s' % (wdport, path),
                                 data=data, method=method,
                                 headers={'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(req, timeout=60))['value']


def js(script):
    return wd('POST', '/session/execute/sync', {'script': script, 'args': []})


def shot(name, wait_for=None, secs=20, phone=False):
    if wait_for:
        try:
            wait(lambda: js('return !!(' + wait_for + ')'), secs, wait_for)
        except SystemExit:
            png = base64.b64decode(wd('GET', '/session/screenshot'))
            open('%s/failed-%s.png' % (out, name), 'wb').write(png)
            print(js('return document.body.innerText.slice(0, 600)'))
            raise
    time.sleep(1.5)
    js("var t = document.querySelector('.toasts'); if (t) t.remove();")
    png = base64.b64decode(wd('GET', '/session/screenshot'))
    open('%s/%s.png' % (out, name), 'wb').write(png)
    print('shots.py:', name)


try:
    wait(lambda: os.path.exists(C + '/data/setup-token'), 20, 'the console')
    wait(lambda: socket.create_connection(('127.0.0.1', wdport)), 10,
         'chromedriver')
    s = wd('POST', '/session', {'capabilities': {'alwaysMatch': {
        'browserName': 'chrome', 'webauthn:virtualAuthenticators': True,
        'goog:chromeOptions': {'args': [
            '--headless=new', '--no-sandbox', '--window-size=1280,800',
            '--user-data-dir=' + C + '/chrome']}}}})
    sid = s['sessionId']
    wd('POST', '/session/webauthn/authenticator', {
        'protocol': 'ctap2', 'transport': 'usb', 'hasResidentKey': False,
        'hasUserVerification': True, 'isUserConsenting': True,
        'isUserVerified': True})
    base = 'http://localhost:%d/' % port
    wd('POST', '/session/url', {'url': base})
    wait(lambda: js("return !!document.querySelector('form[data-form=enrol]')"),
         20, 'the sign-in form')
    token = open(C + '/data/setup-token').read().strip()
    js("const f = document.querySelector('form[data-form=enrol]'); "
       "f.token.value = '%s'; f.name.value = 'a key'; f.requestSubmit();"
       % token)
    wait(lambda: js("return !!document.querySelector('.shell')"), 20,
         'the panel')
    # The hosts, by their agents' sockets.
    for h in HOSTS:
        js("fetch('/api/servers', {method: 'POST', headers: {'Content-Type': "
           "'application/json', 'X-Arcana': '1'}, body: JSON.stringify({name: "
           "'%s', uri: 'tcp://%s:4310'})});" % (h, HOSTS[h]))
        time.sleep(1)
    ids = json.loads(js("var x = new XMLHttpRequest(); x.open('GET', "
                        "'/api/servers', false); x.send(); return x.responseText;"))
    ids = {s['name']: s['id'] for s in ids['servers']}
    hq = ids['hq']
    # The page read the servers before they were added: once again.
    js('location.reload()')
    wait(lambda: js("return !!document.querySelector('.shell') && "
                    "document.body.textContent.includes('branch-b')"), 30,
         'the hosts in the tree')
    # A minute of samples, for the lines to have a shape.
    time.sleep(int(os.environ.get('SHOTS_WAIT', '70')))

    def go(addr):
        wd('POST', '/session/url', {'url': base + addr})

    go('#/')
    shot('demo-fleet', "document.querySelectorAll('.card, .host-card').length "
         ">= 3 || document.body.textContent.includes('branch-b')")
    go('#/network')
    shot('demo-map', "document.querySelector('svg.topo')", 30)
    go('#/hosts/%s' % hq)
    shot('demo-host', "document.body.textContent.includes('hq.example.org')")
    go('#/hosts/%s/jails' % hq)
    shot('demo-jails', "document.body.textContent.includes('mail')")
    go('#/hosts/%s/network' % hq)
    shot('demo-routes', "document.body.textContent.includes('198.51.100.1')")
    go('#/hosts/%s/processes' % hq)
    shot('demo-processes', "document.body.textContent.includes('sshd')")
    go('#/usage')
    shot('demo-usage', "document.body.textContent.includes('branch-a')")
finally:
    if sid:
        try:
            wd('DELETE', '/session/')
        except Exception:
            pass
    for p in procs:
        p.terminate()
