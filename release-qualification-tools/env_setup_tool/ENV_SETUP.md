# `env-setup-tool`

**Usage**:

```console
$ python -m env_setup_tool.src.env_setup [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--feature TEXT`: Either Base or the Feature to be applied  [default: base]
* `--branch TEXT`: Custom branch to retrieve the base configuration from  [default: master]
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `apply-configs`: Apply all base/feature configurations
* `apply-sleeping-area-rules`: Apply sleeping-area-rules configurations
* `apply-wave-plans`: Apply wave plans configurations
* `ims`: Subcommand to access IMS Configurations
* `product-catalog`: Subcommand to access Product Catalog...
* `tsc`: Subcommand to access TSC Configurations

## `env-setup-tool apply-configs`

Apply all base/feature configurations

**Usage**:

```console
$ python -m env_setup_tool.src.env_setup apply-configs [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `env-setup-tool apply-sleeping-area-rules`

Apply sleeping-area-rules configurations

**Usage**:

```console
$ python -m env_setup_tool.src.env_setup apply-sleeping-area-rules [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `env-setup-tool apply-wave-plans`

Apply wave plans configurations

**Usage**:

```console
$ python -m env_setup_tool.src.env_setup apply-wave-plans [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `env-setup-tool ims`

Subcommand to access IMS Configurations

**Usage**:

```console
$ python -m env_setup_tool.src.env_setup ims [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `apply-addresses`: Apply IMS-Addresses configurations
* `apply-configs`: Apply all IMS configurations
* `apply-reason-codes`: Apply IMS-Reason-Codes configurations

### `env-setup-tool ims apply-addresses`

Apply IMS-Addresses configurations

**Usage**:

```console
$ python -m env_setup_tool.src.env_setup ims apply-addresses [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `env-setup-tool ims apply-configs`

Apply all IMS configurations

**Usage**:

```console
$ python -m env_setup_tool.src.env_setup ims apply-configs [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `env-setup-tool ims apply-reason-codes`

Apply IMS-Reason-Codes configurations

**Usage**:

```console
$ python -m env_setup_tool.src.env_setup ims apply-reason-codes [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `env-setup-tool product-catalog`

Subcommand to access Product Catalog Configurations

**Usage**:

```console
$ python -m env_setup_tool.src.env_setup product-catalog [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `upload`: Upload product catalog to env.

### `env-setup-tool product-catalog upload`

Upload product catalog to env.

**Usage**:

```console
$ python -m env_setup_tool.src.env_setup product-catalog upload [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `env-setup-tool tsc`

Subcommand to access TSC Configurations

**Usage**:

```console
$ python -m env_setup_tool.src.env_setup tsc [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `apply-config-items`: Apply TSC-Config-Items configurations
* `apply-configs`: Apply all TSC configurations
* `apply-flow-racks`: Apply TSC-Flow-Racks configurations
* `apply-locations`: Apply TSC-Locations configurations
* `apply-routes`: Apply TSC-Routes configurations
* `apply-spokes`: Apply TSC-Spokes configurations
* `apply-staging-config`: Apply TSC-Staging-Config configurations
* `apply-staging-locations`: Apply TSC-Staging-Locations configurations
* `apply-tote-types`: Apply TSC-Tote-Types configurations
* `pull-from-prod`: Takes a prod TSC configuration per...

### `env-setup-tool tsc apply-config-items`

Apply TSC-Config-Items configurations

**Usage**:

```console
$ python -m env_setup_tool.src.env_setup tsc apply-config-items [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `env-setup-tool tsc apply-configs`

Apply all TSC configurations

**Usage**:

```console
$ python -m env_setup_tool.src.env_setup tsc apply-configs [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `env-setup-tool tsc apply-flow-racks`

Apply TSC-Flow-Racks configurations

**Usage**:

```console
$ python -m env_setup_tool.src.env_setup tsc apply-flow-racks [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `env-setup-tool tsc apply-locations`

Apply TSC-Locations configurations

**Usage**:

```console
$ python -m env_setup_tool.src.env_setup tsc apply-locations [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `env-setup-tool tsc apply-routes`

Apply TSC-Routes configurations

**Usage**:

```console
$ python -m env_setup_tool.src.env_setup tsc apply-routes [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `env-setup-tool tsc apply-spokes`

Apply TSC-Spokes configurations

**Usage**:

```console
$ python -m env_setup_tool.src.env_setup tsc apply-spokes [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `env-setup-tool tsc apply-staging-config`

Apply TSC-Staging-Config configurations

**Usage**:

```console
$ python -m env_setup_tool.src.env_setup tsc apply-staging-config [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `env-setup-tool tsc apply-staging-locations`

Apply TSC-Staging-Locations configurations

**Usage**:

```console
$ python -m env_setup_tool.src.env_setup tsc apply-staging-locations [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `env-setup-tool tsc apply-tote-types`

Apply TSC-Tote-Types configurations

**Usage**:

```console
$ python -m env_setup_tool.src.env_setup tsc apply-tote-types [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `env-setup-tool tsc pull-from-prod`

Takes a prod TSC configuration per retailer per location and saves to file

**Usage**:

```console
$ python -m env_setup_tool.src.env_setup tsc pull-from-prod [OPTIONS] RETAILER LOCATIONS...
```

**Arguments**:

* `RETAILER`: Name of the retailer  [required]
* `LOCATIONS...`: A list of MFC locations {location1} {location2}. For example ABS3116 1531  [required]

**Options**:

* `--help`: Show this message and exit.
