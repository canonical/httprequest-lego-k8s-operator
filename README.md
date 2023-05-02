# httpreq-acme-operator

## Description

Let's Encrypt certificates in the Juju ecosystem for answering the DNS-01
challenge through the HTTP Request plugin.

# Pre-requisites

This charm is a provider of the [`tls-certificates-interface`](https://github.com/canonical/tls-certificates-interface),
charms that require Let's Encrypt certificates need to implement the requirer side.

## Usage

Create a YAML configuration file with the following fields:

```yaml
httpreq-acme-operator:
  email: <Account email address>
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

### Optional configuration properties

- server: Let's Encrypt server to use (default: `https://acme-v02.api.letsencrypt.org/directory`)

## Relations

- `certificates`: `tls-certificates-interface` provider

## OCI Images

-  [Lego Rock Image](https://github.com/canonical/lego-rock)
