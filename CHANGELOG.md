# Changelog

All notable changes to this project are documented in this file.

## [0.1.1] - 2026-11-13

### Added

- **Starter dashboard** (`examples/starter-dashboard.yaml`): the HouseCall card, one-tap quick messages, status and test buttons, and a full-screen kitchen display. See Part 6 of the README.

## [0.1.0] - 2026-11-13

### Added

- **Send to people, not devices.** HouseCall finds each person's phone from the Companion app automatically.
- **Three levels of urgency:** Info (board only), Normal (phones and board) and Critical (loud, breaks through silent mode, read aloud on speakers, repeats until someone answers).
- **Quiet hours:** Normal messages wait until morning; critical alerts always come through.
- **"I'm on it":** one tap stops the repeats, clears the alert from everyone's phone and tells the others who's handling it.
- **Glass Message Board:** messages appear as notes tinted by urgency, without a second phone notification.
- **Frosted-glass dashboard card** with a live feed, who's home, and a composer that explains where each message will go. Loaded automatically.
- Actions `housecall.send`, `housecall.acknowledge` and `housecall.clear_history`; `sensor.housecall`; events `housecall_updated` and `housecall_acknowledged`.
- Setup, people, quiet hours and speakers from the Home Assistant screens, no YAML.
- HouseCall icon for Home Assistant and the Marketplace.
