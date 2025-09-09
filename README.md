# QUICstep

Paper title: **QUICstep: Evaluating connection migration based QUIC censorship circumvention**

Requested Badge(s):
  - [x] **Available**
  - [ ] **Functional**
  - [ ] **Reproduced**

## Description

This artifact contains the source code for **QUICstep: Evaluating connection migraton based QUIC censorship circumvention** (*Seungju Lee, Mona Wang, Watson Jia, Mingshi Wu, Henry Birge-Lee, Liang Wang, and Prateek Mittal*, PoPETS 2026).
QUICstep circumvents QUIC SNI censorship by selectively routing QUIC Initial and Handshake packets over a secure *handshake channel*[^1].
This repo contains an implementation using a WireGuard channel as a handshake channel.

### Security/Privacy Issues and Ethical Concerns

QUICstep, being a censorship circumvention tool, carries fundamental security risks for users when accessing censored domains.
In our experiments with real-world censors we used a client machine under our control hosted at a large-scale commercial VPS provider with a dedicated IP address to avoid harming real users, and accessed only a limited number of real-world domains to avoid the client machine itself being blocked.

## Environment

### Accessibility 

Our artifacts are accessible at https://github.com/inspire-group/QUICstep.

### Requirements

QUICstep requires two machines; a client machine and a proxy machine.
We used AWS EC2 Ubuntu 22.04 instances as clients and AWS Lightsail Debian 11 instances as proxies.
While our implementation of QUICstep can run on minimal hardware (1 GB RAM, 40 GB SSD), performance measurements require greater resources.
See `evaluation/README.md` for details.
Be sure to allow ingress UDP traffic on port 51820 for both machines.
Install WireGuard and generate key pairs for both the client and proxy machines.

Ref: https://www.digitalocean.com/community/tutorials/how-to-set-up-wireguard-on-ubuntu-22-04

### Setup

Update the WireGuard config files `client/wg_qs.conf`, `client/wg_vpn.conf`, `proxy/wg0.conf` with the correct keys and IP addresses.

Copy `client/wg_qs.conf` and `client/wg_vpn.conf` to `/etc/wireguard` in the client machine.

Copy `proxy/wg0.conf` to `/etc/wireguard` in the proxy machine.

Run `wg-quick up wg0` in the proxy machine.

In the client machine, run the following to set up QUICstep.

```
sudo bash client/takedown.sh
wg-quick up wg_qs
```

Run `sudo wg` to check that the WireGuard handshake has successfully completed.

Run the following to take down QUICstep.

```
sudo bash client/setup.sh
wg-quick down wg_qs
```

For the VPN connection, use `wg_vpn` instead of `wg_qs`.

## Notes on Reusability

We would like to emphasize that the idea of QUICstep is not constrained to a particular handshake channel; while we chose WireGuard for our implementation, any secure blocking resistant channel that the client can access for every connection can be a handshake channel.
Our implementation in particular can be altered to support handshake channels that provide a virtual network interface.
We encourage other researchers to create implementations of QUICstep with other secure channels.

[^1]: Any secure, blocking resistant but potentially high-latency channel (e.g. VPN)