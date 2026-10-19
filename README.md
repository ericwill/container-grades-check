# Automated Container Grade Reporting in Slack

This repo provides automated container grade reporting in Slack for Red Hat OpenShift Dev Spaces.

## Architecture

The `check_container_grades.py` script runs on a cron job that sends container grade information to a Slack workflow that is triggered via webhook. The Slack workflow posts a message in the desired channel and contains pre-determined variables. Those variables are populated with the container grade data by the script and passed to the workflow's webhook via JSON. Please note that at the time of this writing, Slack only supports 20 variables per workflow.

The lists of container names are defined in the `DWO_CONTAINERS`, `WTO_CONTAINERS`, and `DEV_SPACES_CONTAINERS` files.

### WTO
* WTO has multiple supported versions to keep an eye on, so dates for grade drops are excluded.
* Supported versions are not neccessarily sequential so some special logic is required. For example, version 1.12 is excluded from the report but 1.11 is included.

## Local Environment Setup
```bash
python -m pip install --upgrade pip
pip install requests python-dateutil packaging
```

## GitHub Action Secrets
Slack workflows triggered by webhook are unauthenticated, so the webhook URL(s) needs to be kept secure. These should be defined as a secret and should not be placed in any scripts directly.