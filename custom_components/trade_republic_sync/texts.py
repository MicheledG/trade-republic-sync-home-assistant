"""Notification texts, in the language Home Assistant is set to."""

from __future__ import annotations

from homeassistant.core import HomeAssistant

TEXTS: dict[str, dict[str, str]] = {
    "en": {
        "approve": "Start the sync. Tap to approve in the Trade Republic app.",
        "approve_again": "Login not approved. Tap to try again in the Trade Republic app.",
        "syncing": "Login approved. Syncing.",
        "done": "Sync complete: {parts}.",
        "new_one": "1 new record",
        "new_many": "{count} new records",
        "new_none": "no new records",
        "adopted": "{adopted} manual linked",
        "problems": "{problems} to check",
        "open_wallet": " Tap to open Wallet.",
        "error": "Sync failed.",
        "nothing_written": " No records written.",
        "wrong_account": "Login approved with a different Trade Republic account. No records written.",
        "unreachable": "Service unreachable. Sync not started.",
        "snooze": "Later",
        "cancel": "Cancel",
        "retry": "Retry",
    },
    "it": {
        "approve": "Avvia la sincronizzazione. Tocca per approvare nell'app Trade Republic.",
        "approve_again": "Accesso non approvato. Tocca per riprovare nell'app Trade Republic.",
        "syncing": "Accesso approvato. Sincronizzazione in corso.",
        "done": "Sincronizzazione completata: {parts}.",
        "new_one": "1 nuovo movimento",
        "new_many": "{count} nuovi movimenti",
        "new_none": "nessun movimento nuovo",
        "adopted": "{adopted} manuali collegati",
        "problems": "{problems} da controllare",
        "open_wallet": " Tocca per aprire Wallet.",
        "error": "Sincronizzazione non riuscita.",
        "nothing_written": " Nessun movimento scritto.",
        "wrong_account": "Accesso approvato con un altro conto Trade Republic. Nessun movimento scritto.",
        "unreachable": "Servizio non raggiungibile. Sincronizzazione non avviata.",
        "snooze": "Più tardi",
        "cancel": "Annulla",
        "retry": "Riprova",
    },
}


def text(hass: HomeAssistant, key: str, **values: object) -> str:
    language = (hass.config.language or "en").split("-")[0]
    table = TEXTS.get(language, TEXTS["en"])
    return table[key].format(**values)
