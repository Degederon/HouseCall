# Changelog

All notable changes to this project are documented in this file.

## [3.1.0] - 2026-11-14

### Removed

- **The Discord channel.** Telegram is now HouseCall's only messaging service. The settings page is called **Telegram**, with one switch: **Use Telegram**. A Discord channel set up earlier is ignored.

## [3.0.0] - 2026-11-14

### Changed

- **Messaging is now Telegram and Discord only.** The settings page is called **Telegram and Discord**, with two simple switches: **Use Telegram** and **Use a Discord channel**.

### Removed

- **ntfy, email, and "Other apps already in Home Assistant"** (such as Signal). Only Telegram and a Discord channel remain. Settings for removed services are ignored, and removed the next time you save that person.

## [2.1.1] - 2026-11-14

### Fixed

- **`to: me` now means whoever pressed the button.** The starter dashboard's test buttons work for everyone without editing. Before, they looked for someone called "Me".
- When a name isn't found, the error now lists the names HouseCall knows.

## [2.1.0] - 2026-11-14

### Removed

- **WhatsApp and Facebook Messenger.** They depended on CallMeBot, an outside service. Neither WhatsApp nor Messenger offers a free, official way for a home system to send messages, so they're no longer part of HouseCall. Any WhatsApp or Messenger keys you entered are ignored and removed the next time you save that person.

## [2.0.2] - 2026-11-14

### Fixed

- The **Messaging services** page no longer shows a `MISSING_VALUE` error if Home Assistant or the browser is still using the previous version's wording.

## [2.0.1] - 2026-11-14

### Fixed

- The Telegram setup page's help link no longer promises pictures. The guide is written steps.

## [2.0.0] - 2026-11-14

### Added

- **Built-in messaging services, nothing else to install, all free:** Telegram, ntfy, email, WhatsApp and Facebook Messenger (through the free CallMeBot service), and a Discord or Slack family channel.
- **Messaging services page:** tick the services you want. Anything not ticked is ignored.
- **Guided setup for each service:** numbered steps, a help link, and a check that it works before saving (Telegram checks the bot token, email signs in, the channel gets a hello).
- **Telegram:** people tap **Start** in your bot and HouseCall finds their chat for you. Alarms come with an **I'm on it** button right in Telegram. Tapping it works like the Home Assistant app's button, and the button is removed once someone answers.
- **ntfy:** each person gets their own private topic, shown with step-by-step subscribe instructions.
- **Each person's page only asks about the services you ticked.**
- **Send a test message** covers the built-in services, with plain explanations when something fails.

### Changed

- Messaging integrations already in Home Assistant, such as Signal, are now under **Other apps already in Home Assistant (advanced)** on each person's page. Settings from 1.3 and 1.4 keep working.

## [1.4.0] - 2026-11-14

### Changed

- **Clearer instructions.** The README is rewritten in plain language and in the order you need it: what HouseCall does, the three levels of urgency, setup in 5 steps, everyday use, settings, and the optional extras.

### Added

- **Each messaging app gets its own address for each person.** After ticking a person's apps, HouseCall asks where each one should send: a number for Signal, Facebook Messenger or text messages, an email address, a Discord, Slack or Matrix channel, or a Threema ID. Separate several with commas. Settings from 1.3.0 keep working.
- Guide for Facebook Messenger, Discord, Slack, Microsoft Teams and 100+ more through Apprise, Matrix, Threema, email and text messages (SMS), plus which apps can't be used (iMessage, Google Messages, Instagram).

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
