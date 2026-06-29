# Dyson Fan Menu Bar App

A macOS menu bar app to control your Dyson fan, using [libdyson-neon](https://github.com/libdyson-wg/libdyson-neon).

## Setup

```bash
pip install -r requirements.txt
```

## Get Your Device Credentials

Run the credential helper (one-time):

```bash
python get_credentials.py
```

This logs into your Dyson cloud account and prints your device serial, credential, and type.

## Configure

Copy `config.example.json` to `config.json` and fill in your values:

```json
{
  "serial": "AB1-US-ABC1234A",
  "credential": "your-credential-here",
  "device_type": "438"
}
```

- **device_ip** (optional): Your fan's local IP address. If omitted, the app auto-discovers it via mDNS.
- **device_type**: Common types: `438` (Pure Cool), `455` (Hot+Cool), `469` (Pure Cool Link)

## Run

```bash
python dyson_menu.py
```

A 💨 icon appears in your menu bar with controls for power, speed, oscillation, and night mode.
