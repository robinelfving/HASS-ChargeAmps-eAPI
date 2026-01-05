# ChargeAmps eAPI Custom Component for Home Assistant

This is a custom component for **Home Assistant** to integrate with **ChargeAmps** EV chargers using the official eAPI.  
It provides real-time data from your ChargeAmps chargers, including status, power consumption, and total energy.

## Features

- Discover all owned ChargeAmps charge points.
- Retrieve charge point and connector status.
- Monitor power per phase and total energy consumption.
- Control charge points remotely:
  - Start/stop charging sessions
  - Set maximum current
  - Lock/unlock charging cable
  - Control LED lights on the charge point
- Compatible with **Luna** and **Halo** chargers.

## Installation

### HACS (recommended)

1. Add this repository as a **Custom Repository** in HACS (type: Integration).
2. Install the ChargeAmps eAPI integration.
3. Restart Home Assistant.

### Manual Installation

1. Download the `chargeamps` folder from this repository.
2. Place it in your Home Assistant `custom_components/` directory.
3. Restart Home Assistant.

## Configuration

Add the following to your `configuration.yaml`:

```yaml
chargeamps:
  username: "YOUR_EMAIL"
  password: "YOUR_PASSWORD"
  api_key: "YOUR_API_KEY"
  url: "https://eapi.charge.space"  # optional if default
  scan_interval: 30  # optional, in seconds
  readonly: false
  chargepoints:
    - "CP_ID_1"
    - "CP_ID_2"