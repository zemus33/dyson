"""Dyson Fan macOS menu bar app using PyObjC directly."""
import json
import os
import threading

import objc
from Foundation import NSObject, NSRunLoop, NSDate
from AppKit import (
    NSApplication,
    NSStatusBar,
    NSMenu,
    NSMenuItem,
    NSVariableStatusItemLength,
    NSImage,
    NSApp,
)
import libdyson

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
ICON_OFF = os.path.join(os.path.dirname(__file__), "icon_off.png")
ICON_ON_DARK = os.path.join(os.path.dirname(__file__), "icon_on_dark.png")
ICON_ON_LIGHT = os.path.join(os.path.dirname(__file__), "icon_on_light.png")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


class DysonMenuApp(NSObject):
    def init(self):
        self = objc.super(DysonMenuApp, self).init()
        self.device = None
        self.config = load_config()

        self.status_item = NSStatusBar.systemStatusBar().statusItemWithLength_(
            NSVariableStatusItemLength
        )
        self.icon_off = NSImage.alloc().initWithContentsOfFile_(ICON_OFF)
        self.icon_off.setTemplate_(True)
        self.icon_on_dark = NSImage.alloc().initWithContentsOfFile_(ICON_ON_DARK)
        self.icon_on_dark.setTemplate_(False)
        self.icon_on_light = NSImage.alloc().initWithContentsOfFile_(ICON_ON_LIGHT)
        self.icon_on_light.setTemplate_(False)
        self.status_item.setImage_(self.icon_off)

        menu = NSMenu.new()
        menu.addItemWithTitle_action_keyEquivalent_("Connecting...", None, "")
        menu.addItem_(NSMenuItem.separatorItem())
        quit_item = menu.addItemWithTitle_action_keyEquivalent_("Quit", "quit:", "q")
        quit_item.setTarget_(self)
        self.status_item.setMenu_(menu)

        threading.Thread(target=self.connect, daemon=True).start()
        return self

    def connect(self):
        try:
            cfg = self.config
            self.device = libdyson.get_device(
                cfg["serial"], cfg["credential"], cfg["device_type"]
            )
            ip = cfg.get("device_ip")
            if not ip:
                ip = self.discover_ip(cfg["serial"])
            self.device.connect(ip)
            self.device.add_message_listener(self._on_device_message)
            self.performSelectorOnMainThread_withObject_waitUntilDone_(
                "rebuildMenu", None, False
            )
        except Exception as e:
            print(f"Connection failed: {e}")

    @objc.python_method
    def discover_ip(self, serial):
        import threading as th
        from libdyson import DysonDiscovery
        found = th.Event()
        result = {}

        def on_found(address):
            result["ip"] = address
            found.set()

        discovery = DysonDiscovery()
        discovery.register_device(self.device, on_found)
        discovery.start_discovery()
        if not found.wait(timeout=30):
            discovery.stop_discovery()
            raise TimeoutError("Could not find Dyson fan on network")
        discovery.stop_discovery()
        return result["ip"]

    @objc.python_method
    def _is_dark_mode(self):
        button = self.status_item.button()
        if button and button.effectiveAppearance():
            name = button.effectiveAppearance().name()
            return "Dark" in str(name)
        return True

    @objc.python_method
    def _build_menu(self):
        d = self.device
        if d.is_on:
            icon = self.icon_on_dark if self._is_dark_mode() else self.icon_on_light
        else:
            icon = self.icon_off
        self.status_item.setImage_(icon)
        menu = NSMenu.new()

        status = "ON" if d.is_on else "OFF"
        speed_str = f"Speed: {d.speed}" if d.speed else "Speed: Auto"
        menu.addItemWithTitle_action_keyEquivalent_(f"Fan: {status}", None, "")
        menu.addItemWithTitle_action_keyEquivalent_(speed_str, None, "")
        menu.addItem_(NSMenuItem.separatorItem())

        on_item = menu.addItemWithTitle_action_keyEquivalent_("Turn On", "turnOn:", "")
        on_item.setTarget_(self)
        off_item = menu.addItemWithTitle_action_keyEquivalent_("Turn Off", "turnOff:", "")
        off_item.setTarget_(self)
        menu.addItem_(NSMenuItem.separatorItem())

        for spd in range(1, 11):
            item = menu.addItemWithTitle_action_keyEquivalent_(
                f"Speed {spd}", "setSpeed:", ""
            )
            item.setTarget_(self)
            item.setTag_(spd)
            if d.speed == spd:
                item.setState_(1)
        auto_item = menu.addItemWithTitle_action_keyEquivalent_("Auto", "toggleAuto:", "")
        auto_item.setTarget_(self)
        if d.auto_mode:
            auto_item.setState_(1)
        menu.addItem_(NSMenuItem.separatorItem())

        osc_item = menu.addItemWithTitle_action_keyEquivalent_("Oscillation", "toggleOsc:", "")
        osc_item.setTarget_(self)
        if d.oscillation:
            osc_item.setState_(1)

        night_item = menu.addItemWithTitle_action_keyEquivalent_("Night Mode", "toggleNight:", "")
        night_item.setTarget_(self)
        if d.night_mode:
            night_item.setState_(1)
        menu.addItem_(NSMenuItem.separatorItem())

        quit_item = menu.addItemWithTitle_action_keyEquivalent_("Quit", "quit:", "q")
        quit_item.setTarget_(self)

        self.status_item.setMenu_(menu)

    def rebuildMenu(self):
        self._build_menu()

    @objc.python_method
    def _on_device_message(self, msg_type):
        self.performSelectorOnMainThread_withObject_waitUntilDone_(
            "rebuildMenu", None, False
        )

    def turnOn_(self, sender):
        self.device.turn_on()

    def turnOff_(self, sender):
        self.device.turn_off()

    def setSpeed_(self, sender):
        self.device.set_speed(sender.tag())

    def toggleAuto_(self, sender):
        if self.device.auto_mode:
            self.device.disable_auto_mode()
        else:
            self.device.enable_auto_mode()

    def toggleOsc_(self, sender):
        if self.device.oscillation:
            self.device.disable_oscillation()
        else:
            self.device.enable_oscillation()

    def toggleNight_(self, sender):
        if self.device.night_mode:
            self.device.disable_night_mode()
        else:
            self.device.enable_night_mode()

    def quit_(self, sender):
        if self.device and self.device.is_connected:
            self.device.disconnect()
        NSApp.terminate_(None)


if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    delegate = DysonMenuApp.new()
    app.setActivationPolicy_(1)  # NSApplicationActivationPolicyAccessory
    app.run()
