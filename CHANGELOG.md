# Changelog

All notable changes to this project are documented in this file.

## [1.3.0] - 2026-11-14

### Added

- **Messaging apps.** HouseCall can now also send through Telegram, Signal, WhatsApp (via Whatsigram), ntfy, Pushover, email and any other messaging integration in Home Assistant. Set it up under **Configure → Messaging apps**: choose when to use them, then pick which apps reach each person and, where needed, their number.
- **When to use messaging apps:** critical alerts for everyone and everything for people without the Home Assistant app (default), every message, only people without the app, or never. Info messages and critical repeats never go to messaging apps.
- **Send a test message** under **Configure**, with a ✅ or ❌ and the reason for every app tried. Also available as the `housecall.send_test` action, and as a **Test messaging apps** button on the starter dashboard.
- The card shows how many messaging apps each person has, and lists *Messaging apps* under how a message was delivered.

## [1.2.0] - 2026-11-14

### Added

- **Tap a notification to open your HouseCall dashboard.** A plain tap on a HouseCall notification now opens the dashboard with your HouseCall card, right next to the **I'm on it** button, instead of the app's home screen. If you created the starter dashboard named **HouseCall**, it's used automatically. Choose another dashboard, or none, under **Configure → Phones, speakers, Glass Message Board and repeats**.

## [1.1.1] - 2026-11-14

### Fixed

- **I'm on it on the card now responds straight away.** The button changes to *Letting everyone know…*, the card updates at once, and clearing the alert from phones happens in the background instead of making the button wait.
- Messages about the card (sent, handled, errors) now also show when the composer is turned off.

### Added

- Troubleshooting: how to find **I'm on it** in a phone notification (press and hold on iPhone, swipe down on Android).

## [1.1.0] - 2026-11-14

### Added

- **HouseCall-only people.** Under **Configure → Add a HouseCall-only person**, create people who aren't in Home Assistant, such as Grandma or the babysitter: a name, the phone(s) to notify, and optionally something that shows whether they're home. Change or remove them later under **Change or remove a HouseCall-only person**.
- Send to anyone by name, for example `to: Grandma`.

### Changed

- **Hide people from Home Assistant.** The People screen is now called **People from Home Assistant: show or hide** and explains how to hide accounts you can't delete.
- The card leaves out Home or Away for people with nothing tracking where they are.
- The **To** field of **HouseCall: Send** is now a text box, so it accepts names as well as people.

## [1.0.1] - 2026-11-14

### Added

- **Who's in HouseCall:** under **Configure → People**, tick or untick people to add them to HouseCall or leave them out, without deleting them from Home Assistant.

### Fixed

- People deleted under **Settings → People** no longer appear on the card or in **Everyone**.

## [1.0.0] - 2026-11-13

The first release of HouseCall.

### Added

- **Send to people, not devices.** HouseCall finds each person's phone from the Companion app automatically.
- **Three levels of urgency:** Info (board only), Normal (phones and board) and Critical (loud, breaks through silent mode, read aloud on speakers, repeats until someone answers).
- **Quiet hours:** Normal messages wait until morning; critical alerts always come through.
- **"I'm on it":** one tap stops the repeats, clears the alert from everyone's phone and tells the others who's handling it.
- **Glass Message Board:** messages appear as notes tinted by urgency, without a second phone notification.
- **Frosted-glass dashboard card** with a live feed, who's home, and a composer that explains where each message will go. Loaded automatically.
- Actions `housecall.send`, `housecall.acknowledge` and `housecall.clear_history`; `sensor.housecall`; events `housecall_updated` and `housecall_acknowledged`.
- Setup, people, quiet hours and speakers from the Home Assistant screens, no YAML.
- **Starter dashboard** (`examples/starter-dashboard.yaml`): one-tap quick messages, status and test buttons, and a full-screen kitchen display.
- HouseCall icon for Home Assistant and the Marketplace.
