# Trade Republic Sync for Home Assistant

Starts a Trade Republic sync from Home Assistant, by a button or on a
schedule, and reports how it went. Each run asks you to approve the login in
the Trade Republic app on your phone; no PIN is stored anywhere.

It talks to a sync service you run yourself, which exposes three routes:

| Route | Use |
|---|---|
| `POST /runs` (header `X-Api-Key`, body `{"arm_hours": n}`) | arm a run; answers `run_id`, `state`, `approve_url` |
| `GET /runs/<run_id>` (header `X-Api-Key`) | the run's `state`, and when it ends its `summary` and `problems` |
| `DELETE /runs/<run_id>` (header `X-Api-Key`) | cancel a run that has not started syncing; `409` once it has |
| `GET /go?run=<run_id>` | the link in the notification: starts the login and opens the app |

States: `armed`, `starting`, `waiting`, `claimed`, `syncing`, then `ok`,
`error`, `expired`, `wrong_account` or `cancelled`. A lapsed login goes back to `armed`.

## Install

1. In the Marketplace (HACS before Home Assistant 2026.11): *Custom
   repositories*, add this repository as an *Integration*.
2. Install **Trade Republic Sync** and restart Home Assistant.
3. *Settings → Devices & services → Add integration → Trade Republic Sync*:
   enter the service URL and the API key.
4. In the integration's options, choose the schedule and the notify service
   of your phone (the Home Assistant companion app).

## Notifications

The approval notification rings (high priority) and offers *Later* (again in
2 hours, within the run's window) and *Cancel*. Progress and outcomes arrive
on a silent channel; a failure offers *Retry*.

## Entities

- `button.trade_republic_sync_sync_now`
- `sensor.trade_republic_sync_state`
- `sensor.trade_republic_sync_last_sync`, with the new records, the balance
  gap and the problems of the last run as attributes
- `sensor.trade_republic_sync_next_sync`

Not affiliated with Trade Republic.
