# http_server — from-scratch TCP/HTTP server in Python

this readme was derived from my notes in the repository itself using claude.ai

A minimal HTTP server built directly on top of raw TCP sockets — no `http.server`,
no frameworks. Built to understand what's actually happening underneath a web
framework: sockets, the TCP handshake, and manual HTTP parsing.

## Concepts

### IP addresses
- IPv4 supports `2**32` addresses. IPv6 supports `2**128`.
- Every reachable host has an IP (e.g. `142.250.189.206` for Google). DNS maps
  human-readable domains to these addresses.

### TCP vs UDP
- `socket.SOCK_STREAM` → TCP. `socket.SOCK_DGRAM` → UDP.
- TCP establishes a connection first via the **three-way handshake**:
  1. **SYN** — client requests a connection ("knock on the door")
  2. **SYN-ACK** — server acknowledges and responds ("acknowledges the knock")
  3. **ACK** — client acknowledges back ("says hi")
- UDP sends packets with no handshake and no delivery guarantee — faster, but
  the sender never confirms the receiver got (or wanted) anything.
- **QUIC** (used in HTTP/3) improves on both: it's encrypted by default, adds
  its own handshake, and identifies connections by a **connection ID** rather
  than IP address — so switching networks (e.g. Wi-Fi → mobile data) doesn't
  force a new connection the way it does with plain TCP/UDP.

### Sockets
- `AF_INET`, `SOCK_STREAM` are constants identifying the address family
  (IPv4) and socket type (TCP stream).
- `setsockopt(level, optname, value)` configures socket behavior:
  - `level` — which protocol layer the option applies to. Most general socket
    options (like `SO_REUSEADDR`) live at `SOL_SOCKET`, the layer above any
    specific protocol. TCP-specific options (e.g. `TCP_NODELAY`) instead use
    `IPPROTO_TCP` as the level. `SO_REUSEADDR` is `SOL_SOCKET` regardless of
    whether the underlying socket is TCP or UDP — it's not protocol-specific.
  - `optname` — the specific option, e.g. `SO_REUSEADDR`.
  - `value` — `1` = on, `0` = off.
- **Why `SO_REUSEADDR` matters:** after a socket closes, the OS holds it in a
  `TIME_WAIT` state briefly to guarantee any in-flight data is fully
  delivered. Without `SO_REUSEADDR`, restarting the server immediately during
  this window throws "address already in use." Setting it lets the socket be
  reused right away.
- **Host binding:**
  - `0.0.0.0` — accept connections from anyone on the LAN.
  - `127.0.0.1` — restrict to this machine only.
- **Port choice:** 80 = HTTP, 443 = HTTPS. Ports 0–1023 are OS-reserved —
  avoid binding to those directly.
- `listen(n)` sets the backlog — how many pending connections can queue
  before the OS starts declining/ignoring new ones.
- `accept()` blocks until a client connects, then returns `(client_socket,
  client_address)`.

### Blocking vs non-blocking (proto1)
By default, `accept()` **blocks** — the loop stops there until a client
connects. `proto1` set `setblocking(False)` to experiment with non-blocking
mode, which raises an exception immediately if no client is waiting instead
of pausing execution:

```python
while True:
    try:
        client_socket, client_address = my_server_socket.accept()
        print(client_socket)
        print(client_address)
    except:
        time.sleep(0.5)
        continue
```

This busy-polls: try to accept, and if nothing's there yet, sleep briefly and
retry. It keeps the loop alive indefinitely without crashing on an empty
queue. Note this by itself doesn't add concurrent multi-client handling —
each accepted connection is still processed one at a time; it just means the
server doesn't hang/die waiting on `accept()`. **proto2 drops this** and goes
back to plain blocking `accept()`, since the try/except was for
understanding the mechanism, not something the final version needs.

### Parsing the HTTP request (proto2)
`client_socket.recv(1500).decode()` reads up to 1500 bytes off the socket and
decodes it to a string — this is the raw HTTP request text.

A request's first line ("request line") has three space-separated parts:

1. **Method** — `GET` (fetch a resource), `POST` (create/submit data),
   `PUT`/`DELETE` (update/remove), `HEAD` (like GET but headers only, no
   body — useful for checking a large file's size before downloading),
   `OPTIONS` (ask the server what methods/options it supports).
2. **Path** — e.g. `/` or `/search?docid=69`. In a full URL like
   `http://www.abc.xyz:1600/whateverpage/search?docid=69`, DNS resolves
   `www.abc.xyz` to an IP, the port follows the `:`, and everything after
   that is the path. So plain `/` just means the site root —
   `http://0.0.0.0:1600/`.
3. **HTTP version** — e.g. `HTTP/1.1`.

Subsequent lines are headers, e.g.:
- `Host:` — the domain/localhost being requested.
- `Connection: keep-alive` / `close` — whether the client wants the TCP
  connection kept open after this request.
- `User-Agent:` — client's browser/OS/rendering engine details.
- `Accept:` — content types the client can handle, ordered by preference,
  with an optional `q=` quality weight per type.

## Building the response

HTTP responses need `\r\n` (CRLF) line endings, not just `\n` — this is part
of the HTTP spec, not a style choice. `nano`/`print()` debugging won't catch
this because you're eyeballing raw output rather than parsing it strictly,
but real HTTP clients (Thunder Client, browsers, curl) do parse strictly and
will throw a parse error like `Missing expected CR after response line` if
the CR is missing:

```python
response = 'HTTP/1.1 200 OK\r\n\r\n' + content
```

The blank line (`\r\n\r\n`) separates headers from the body — proto2 doesn't
send any headers yet, just status line + blank line + body.

## Files

| File | Purpose |
|---|---|
| `tcp_server_proto_1.py` | Blocking vs. non-blocking `accept()` experiment |
| `tcp_server_proto_2.py` | Working server: parses GET requests, serves `index.html`, returns proper `\r\n` line endings |
| `index.html` | Served on `GET /` |

## Known gaps / next steps
- Only `/` is routed — any other GET path currently falls through to the
  same block with no dedicated 404-for-missing-file handling (only
  method-level 404 exists, for non-GET verbs).
- No concurrency — each client is accepted and handled fully before the next
  `accept()` call runs (no threading yet).
- File path in `open()` is relative to the process's working directory, not
  the script's location — moving the launch directory breaks it silently.
  Consider `os.path.dirname(os.path.abspath(__file__))` for a stable path.
- No `Content-Type` or `Content-Length` headers sent yet.
