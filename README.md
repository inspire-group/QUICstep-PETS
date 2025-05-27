# QUICstep

QUICstep circumvents QUIC SNI censorship by selectively routing
QUIC Initial and Handshake packets over a secure *handshake channel*[^1].
This implementation uses a WireGuard channel as a handshake channel.

## Requirements

Install WireGuard and generate key pairs for both the client and proxy machines.

Ref: https://www.digitalocean.com/community/tutorials/how-to-set-up-wireguard-on-ubuntu-22-04

## Setup

Update the WireGuard config files `client/wg_qs.conf`, `client/wg_vpn.conf`, `proxy/wg0.conf`
with the correct keys.

Copy `client/wg_qs.conf` and `client/wg_vpn.conf` to `/etc/wireguard` in the client machine.

Copy `proxy/wg0.conf` to `/etc/wireguard` in the proxy machine.

Run `wg-quick up wg0` in the proxy machine.

In the client machine, run the following to set up QUICstep.

```
sudo bash client/takedown.sh
wg-quick up wg_qs
```

Run the following to take down QUICstep.

```
sudo bash client/setup.sh
wg-quick down wg_qs
```

For the VPN connection, use `wg_vpn` instead of `wg_qs`.

[^1]: Any secure, blocking resistant but potentially high-latency channel
(e.g. public VPN, DNS tunnel).
