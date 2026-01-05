"""Tjänster för ChargeAmps."""
from .handler import ChargeAmpsHandler

SERVICE_MAP = {
    "set_light": "async_set_light",
    "set_max_current": "async_set_max_current",
    "enable": "async_enable_ev",
    "disable": "async_disable_ev",
}

def register_services(hass, handler: ChargeAmpsHandler):
    for service_name, func_name in SERVICE_MAP.items():
        async def service_call(call):
            func = getattr(handler, func_name)
            await func(call.data)
        hass.services.async_register("chargeamps", service_name, service_call)