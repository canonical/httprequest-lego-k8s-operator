# httpreq-acme-operator

## Description

ACME operator implementing the provider side of the `tls-certificates`
interface to get signed certificates from the `Let's Encrypt` ACME server
using the HTTP Request plugin for DNS-01 challenge.

# Pre-requisites

This charm is a provider of the [`tls-certificates-interface`](https://github.com/canonical/tls-certificates-interface),
charms that require Let's Encrypt certificates need to implement the requirer side.

## Usage

Create a YAML configuration file with the following fields:

```yaml
httpreq-acme-operator:
  email: <Account email address>
  httpreq_endpoint: <HTTP/HTTPS URL>
```

Deploy `httpreq-acme-operator`:

```bash
juju deploy httpreq-acme-operator --config <yaml config file>
```

Relate it to a `tls-certificates-requirer` charm:

```bash
juju relate httpreq-acme-operator:certificates <tls-certificates-requirer>
````

## Config

### Required configuration properties

- email: Let's Encrypt email address
- httpreq_endpoint: HTTP/HTTPS URL to the service implementing the HTTPREQ API

### Optional configuration properties

- server: Let's Encrypt server to use (default: `https://acme-v02.api.letsencrypt.org/directory`)
- httpreq_http_timeout: API request timeout
- httpreq_mode: "'RAW' or None"
- httpreq_password: Basic authentication password
- httpreq_polling_interval: Time between DNS propagation checks
- httpreq_propagation_timeout: Maximum waiting time for DNS propagation
- httpreq_username: Basic authentication username

## Relations

- `certificates`: `tls-certificates-interface` provider

## OCI Images

-  [Lego Rock Image](https://github.com/canonical/lego-rock)
