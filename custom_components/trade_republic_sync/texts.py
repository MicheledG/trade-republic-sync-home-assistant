"""Notification texts, in the language Home Assistant is set to."""

from __future__ import annotations

from homeassistant.core import HomeAssistant

TEXTS: dict[str, dict[str, str]] = {
    "en": {
        "approve": "Sync due. Tap to log in and approve in the app.",
        "approve_again": "Login not approved. Tap to try again.",
        "approve_button": "Approve",
        "done": "Synced: {count} new records.",
        "done_problems": "Synced: {count} new records, {problems} to check.",
        "error": "Sync failed.",
        "wrong_account": "Login approved with a different account: nothing was written.",
        "unreachable": "Sync service unreachable.",
    },
    "it": {
        "approve": "Sincronizzazione pronta. Tocca per accedere e approva nell'app.",
        "approve_again": "Accesso non approvato. Tocca per riprovare.",
        "approve_button": "Approva",
        "done": "Sincronizzato: {count} nuovi movimenti.",
        "done_problems": "Sincronizzato: {count} nuovi movimenti, {problems} da controllare.",
        "error": "Sincronizzazione fallita.",
        "wrong_account": "Accesso approvato con un altro conto: non è stato scritto nulla.",
        "unreachable": "Servizio di sincronizzazione irraggiungibile.",
    },
}


def text(hass: HomeAssistant, key: str, **values: object) -> str:
    language = (hass.config.language or "en").split("-")[0]
    table = TEXTS.get(language, TEXTS["en"])
    return table[key].format(**values)
