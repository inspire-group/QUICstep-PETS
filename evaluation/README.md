# QUIC and connection migration support measurements

`quic_and_port_migration_support.py` uses the Chromium QUIC client[^1] to access Tranco top 1M websites[^2]
and attempt port migration by changing ephemeral port between requests[^3].
Refer to the Playing with QUIC[^1] page and the Chromium source code[^4] page for install requirements and guidelines for the QUIC client.

# Performance measurements

`performance.py` uses Selenium driven by Chrome to access a given website
and retrieve the time to first byte (`responseStart - navigationStart`) and page load time (`domComplete - responseStart`).
Google Chrome and Python 3.7+ must be installed on the system.

[^1]: https://www.chromium.org/quic/playing-with-quic
[^2]: https://tranco-list.eu
[^3]: [https://source.chromium.org/chromium/chromium/src/+/main:net/third_party/quiche/src/quiche/quic/tools/quic_toy_client.cc](https://source.chromium.org/chromium/chromium/src/+/main:net/third_party/quiche/src/quiche/quic/tools/quic_toy_client.cc#:~:text=//%20Send%20repeated%20requests%20and%20change%20ephemeral%20port%20between%20requests)
[^4]: [https://www.chromium.org/developers/how-tos/get-the-code/](https://www.chromium.org/developers/how-tos/get-the-code/)