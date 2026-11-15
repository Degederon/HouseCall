<div align="center">

<img src="https://raw.githubusercontent.com/Degederon/HouseCall/main/docs/images/icon.png" alt="HouseCall icon" width="128">

# HouseCall

**Every alert in the house, in one place.**

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/docs/faq/custom_repositories)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.11%2B-18BCF2.svg?logo=homeassistant&logoColor=white)](https://www.home-assistant.io/)
[![Version](https://img.shields.io/badge/version-1.4.0-6E56CF.svg)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

Beautiful design and ease of use. https://github.com/Degederon/HouseCall

HouseCall makes sending alerts in Home Assistant simple:

- You send a message to **people** (*Me*, *Jay*, *Everyone*), not to phones or devices.
- You choose how urgent it is: **Info**, **Normal** or **Critical**.
- HouseCall does the rest. It picks the right phones, waits during quiet hours, reads critical alerts aloud, and keeps ringing until someone taps **I'm on it**.

It matches the look of [Glass Message Board](https://github.com/Degederon/GlassMessageBoard) and [Grand Marquee](https://github.com/Degederon/grand-marquee), and posts its messages to your Glass Message Board too.

## Contents

1. [What HouseCall does](#what-housecall-does)
2. [Take a tour](#take-a-tour)
3. [The three levels of urgency](#the-three-levels-of-urgency)
4. [Before you start](#before-you-start)
5. [Set up HouseCall](#set-up-housecall) (5 steps)
6. [Everyday use](#everyday-use)
7. [Change settings](#change-settings)
8. [Reach people who don't use the Home Assistant app](#reach-people-who-dont-use-the-home-assistant-app) (optional)
9. [Send a test message](#send-a-test-message)
10. [Use HouseCall in automations](#use-housecall-in-automations)
11. [Card options](#card-options)
12. [Troubleshooting](#troubleshooting)

## What HouseCall does

| Feature | What it means for you |
|---|---|
| **People, not devices** | Send to *Me*, *Jay* or *Everyone*. HouseCall finds each person's phone by itself. |
| **Three levels of urgency** | Quiet notes, ordinary messages, or loud alarms. See [below](#the-three-levels-of-urgency). |
| **Quiet hours** | Ordinary messages wait until morning. Alarms always get through. |
| **"I'm on it"** | One tap stops the alarm on everyone's phone and tells the others who's handling it. |
| **Speakers** | Alarms are read aloud on the speakers you choose. |
| **Glass Message Board** | Every message also appears as a note on your board. |
| **Messaging apps** | Optionally reach people on Telegram, Signal, WhatsApp, Messenger, email and more. |
| **Send a test message** | Check that someone can be reached, without a real alarm. |
| **Frosted-glass card** | Today's messages, who's home, and a message box, all in one card. |
| **No YAML** | Everything is set up from the Home Assistant screens. |

## Take a tour

All pictures show the HouseCall card on a Home Assistant dashboard with example messages.

<table>
<tr>
<td width="50%" valign="top"><img src="https://raw.githubusercontent.com/Degederon/HouseCall/main/docs/images/tour/01-wall-tablet.jpg" alt="The full card on a wall tablet: today's messages, who's home, and the composer." width="100%"><br><sub>The full card on a wall tablet: today's messages, who's home, and the message box. A critical leak alert is waiting for an answer.</sub></td>
<td width="50%" valign="top"><img src="https://raw.githubusercontent.com/Degederon/HouseCall/main/docs/images/tour/02-compose-critical.jpg" alt="Sending a critical alert to Jay. The card explains exactly what will happen." width="100%"><br><sub>Sending a critical alert to Jay. The card explains exactly what will happen before you press Send.</sub></td>
</tr>
<tr>
<td width="50%" valign="top"><img src="https://raw.githubusercontent.com/Degederon/HouseCall/main/docs/images/tour/03-compose-info.jpg" alt="An Info message only shows on the board. Nobody's phone buzzes." width="100%"><br><sub>An Info message only shows on the board. Nobody's phone buzzes.</sub></td>
<td width="50%" valign="top"><img src="https://raw.githubusercontent.com/Degederon/HouseCall/main/docs/images/tour/04-handled.jpg" alt="After someone taps I'm on it, the alert is marked as handled." width="100%"><br><sub>After someone taps <b>I'm on it</b>, the alarm stops and the alert is marked as handled.</sub></td>
</tr>
<tr>
<td width="50%" valign="top"><img src="https://raw.githubusercontent.com/Degederon/HouseCall/main/docs/images/tour/05-feed-only.jpg" alt="Feed only, without the composer, for a kitchen display." width="100%"><br><sub>Messages only, without the message box, here as a kitchen display.</sub></td>
<td width="50%" valign="top"><img src="https://raw.githubusercontent.com/Degederon/HouseCall/main/docs/images/tour/06-phone.jpg" alt="On a phone, the composer moves below the messages." width="100%"><br><sub>On a phone, the message box moves below the messages.</sub></td>
</tr>
</table>

## The three levels of urgency

Every message has one of three levels. This is the only choice you make when you send something.

| Level | Use it for | What happens |
|---|---|---|
| **Info** | Things nice to know: *"Dogs fed"*, *"Rain tonight"* | Shows on the card and board only. **No phone buzzes.** |
| **Normal** | Everyday messages: *"Dinner's ready"*, *"Dryer finished"* | A normal phone notification, plus the board. **During quiet hours it waits until morning.** |
| **Critical** | Emergencies: *"Water leak"*, *"Smoke alarm"* | **Loud on phones, even on silent.** Read aloud on speakers. **Repeats every 5 minutes until someone taps "I'm on it".** |

When someone taps **I'm on it**:

1. The alarm stops on everyone's phone.
2. Everyone else gets a short note: *"Jay is handling it: Water leak"*.
3. The card shows **Handled by Jay**.

If nobody answers, HouseCall stops after 6 repeats and marks the alert **Nobody answered**.

## Before you start

You need:

- **Home Assistant 2024.11 or later.**
- **A "person" for each family member** in Home Assistant (**Settings → People**).
- **The Home Assistant app** on each phone, signed in. This is how phones get alerts.
- **On iPhone:** allow **Critical Alerts** for the Home Assistant app (iPhone **Settings → Notifications → Home Assistant**), so alarms can sound on silent.

Optional extras: speakers for read-aloud alarms, [Glass Message Board](https://github.com/Degederon/GlassMessageBoard), and messaging apps for people without the Home Assistant app.

## Set up HouseCall

Do these five steps once, in order.

### Step 1: Install HouseCall

**Home Assistant 2026.11 and later (Marketplace)**

1. Go to **Settings → Marketplace**.
2. Choose **Add via link** and paste `https://github.com/Degederon/HouseCall`.
3. Open **HouseCall** and select **Install**.
4. Restart Home Assistant: **Settings → System → ⏻ (top right) → Restart Home Assistant**.

**Earlier versions (HACS)**

1. In HACS, open **⋮ → Custom repositories**.
2. Paste `https://github.com/Degederon/HouseCall`, choose **Integration**, and select **Add**.
3. Search for **HouseCall**, install it, and restart Home Assistant.

### Step 2: Add HouseCall to Home Assistant

1. Go to **Settings → Devices & services**.
2. Select **+ Add integration** and search for **HouseCall**.
3. HouseCall shows the people and phones it found. Select **Submit**.

### Step 3: Add the HouseCall card to a dashboard

1. Open a dashboard and select the pencil (top right) to edit it.
2. Select **+ Add card**, search for **HouseCall**, and select it.
3. Select **Save**.

> [!TIP]
> Prefer a ready-made page? Use the [starter dashboard](#optional-use-the-starter-dashboard) instead.

### Step 4: Send your first message

1. In the card, type *Dinner's ready!*
2. Choose **Everyone** and **Normal**.
3. Read **Where it will go**, then select **Send now**. Your phone buzzes.

### Step 5: Try an alarm

1. Type *Test*, choose **only yourself**, and choose **Critical**.
2. Select **Send now**. Your phone rings loudly, even on silent.
3. Stop it by tapping **I'm on it**, either on the card or on the notification ([how to find it](#answering-an-alarm)).

That's it. HouseCall is set up.

### Optional: use the starter dashboard

The [starter dashboard](examples/starter-dashboard.yaml) is a ready-made page with:

- the HouseCall card,
- one-tap buttons such as *Dinner's ready*, *Leaving now* and *Good night*,
- how many alarms are waiting, and test buttons,
- a second page for a kitchen display.

To add it:

1. Go to **Settings → Dashboards → + Add dashboard → New dashboard from scratch**. Name it **HouseCall** and open it.
2. Select the pencil, then **⋮ → Raw configuration editor**.
3. Delete everything there, paste the [starter dashboard](examples/starter-dashboard.yaml), and select **Save**.

If you name it **HouseCall**, tapping a HouseCall notification opens this page automatically.

## Everyday use

### Sending a message

In the card: type the message, choose **Who** and **How urgent**, check **Where it will go**, and select **Send now**.

### Answering an alarm

You can tap **I'm on it** in two places:

- **On the card:** the alert has a red border and an **I'm on it** button.
- **On your phone:** the button is on the notification, but hidden at first.
  - **iPhone:** press and hold the notification.
  - **Android:** swipe down on the notification.
  - A plain tap opens your HouseCall dashboard, where the button is on the card.

## Change settings

All settings are in one place: **Settings → Devices & services → HouseCall → Configure**.

| Menu item | What you can change |
|---|---|
| **People from Home Assistant: show or hide** | Who appears in HouseCall, and their phones. |
| **Add a HouseCall-only person** | Add someone who isn't in Home Assistant, such as Grandma. |
| **Change or remove a HouseCall-only person** | Edit or delete them. |
| **Messaging apps** | Telegram, Signal, WhatsApp and more. [Details](#reach-people-who-dont-use-the-home-assistant-app). |
| **Send a test message** | Check how someone can be reached. [Details](#send-a-test-message). |
| **Quiet hours** | When Normal messages wait. Default: 10 PM to 7 AM. |
| **Phones, speakers, Glass Message Board and repeats** | Which page opens when a notification is tapped, speakers and voice for alarms, posting to Glass Message Board, and how often alarms repeat. |

### People

HouseCall uses the people in **Settings → People**. You can also hide some, or add your own.

**Hide someone** (for example a guest or service account you can't delete):

1. **Configure → People from Home Assistant: show or hide**.
2. Untick them and select **Submit**. They stay in Home Assistant but disappear from HouseCall.

**Add someone who isn't in Home Assistant** (such as Grandma or a babysitter):

1. **Configure → Add a HouseCall-only person**.
2. Type their name. If they have the Home Assistant app, pick their phone.
3. Optionally, pick something that shows whether they're home.
4. Select **Submit**. In automations, send to them by name: `to: Grandma`.

**Add a new family member from Home Assistant:**

1. Add them under **Settings → People**, and under **Track device** pick their phone.
2. **Configure → People from Home Assistant: show or hide**, tick them, and select **Submit**.

### Speakers and Glass Message Board

Under **Configure → Phones, speakers, Glass Message Board and repeats**:

- **Speakers and voice:** pick both, and alarms are read aloud.
- **Glass Message Board:** on by default if it's installed. Notes are tinted blue (Info), amber (Normal) or rose (Critical), and alarms are pinned.
- **Repeats:** how often alarms repeat (default every 5 minutes) and when to give up (default after 6 times).
- **Dashboard to open:** the page that opens when someone taps a notification.

## Reach people who don't use the Home Assistant app

**This part is optional.** Everyone with the Home Assistant app already gets everything.

For people who won't install the Home Assistant app, you have three choices, best first:

1. **Give them a login to your Home Assistant** (free). Add them under **Settings → People** with **Allow login** on, and have them install the Home Assistant app. They then get everything, including loud alarms. Their app must be able to reach your Home Assistant from outside your house.
2. **Use a messaging app they already have**, such as Telegram, Signal or WhatsApp. See below.
3. **Text messages (SMS).** This needs a paid service or a spare phone with a SIM card. See [Text messages](#text-messages-sms).

> [!NOTE]
> Messaging apps and texts can't sound an alarm on silent. Only the Home Assistant app (and Pushover) can.

### Using a messaging app: 3 steps

**Step 1. Connect the app to Home Assistant.** Pick one from the list below and add its integration. Start with just one: **Telegram is the easiest and free.**

**Step 2. Tell HouseCall who it reaches.**

1. Go to **Configure → Messaging apps**.
2. Under **Set up messaging apps for**, pick the person and select **Submit**.
3. Tick the apps that reach them and select **Submit**.
4. If an app needs to know where to send, HouseCall asks. Type their phone number with country code (`+15551234567`), email address, or channel. Leave it empty if the app already knows. Select **Submit**.

**Step 3. Check it works.** Use [Send a test message](#send-a-test-message) and choose **Messaging apps only**.

### When messaging apps are used

Set this under **Configure → Messaging apps → When to use messaging apps**:

| Choice | What happens |
|---|---|
| **Recommended** | Alarms go to everyone's messaging apps. People without the Home Assistant app get every Normal message there too. |
| **Every Normal and Critical message** | Everyone gets everything in their messaging apps as well. |
| **Only for people without the Home Assistant app** | Messaging apps are only used for those people. |
| **Never** | Messaging apps are off. |

Info messages and alarm repeats never go to messaging apps, so chats don't get flooded.

### Which messaging apps work

You only need the apps your family actually uses.

| App | Cost | How to connect it (Settings → Devices & services → Add integration) | What the person needs |
|---|---|---|---|
| **Telegram** ⭐ easiest | Free | **Telegram bot**. Create a bot with Telegram's *BotFather*, then add each person's chat under **⋮ → Add allowed chat ID**. | Telegram, and to send **/start** to your bot once. |
| **Signal** | Free | **Signal Messenger**, plus the *Signal Messenger REST API* add-on. Needs a spare phone number to send from. | Signal. You type their number in HouseCall. |
| **WhatsApp** | Free for personal use | **Whatsigram Messenger** from HACS (uses the free CallMeBot service). | WhatsApp, and to activate CallMeBot once. |
| **Facebook Messenger** | Free, but complex | **Facebook Messenger** (in `configuration.yaml`). Needs a Facebook Page and a Facebook developer app; until Facebook approves the app, add family as testers. | Messenger. You type their number in HouseCall. |
| **Pushover** | $4.99 once | **Pushover**. Can sound alarms on silent. | The Pushover app. |
| **ntfy** | Free | **ntfy**. | The ntfy app. |
| **Email** | Free | **Google Mail**, or **SMTP** for any email. | An email address. |
| **Discord, Slack, Matrix, Threema** | Mostly free | Their own integrations. | You type their channel, room or ID in HouseCall. |
| **Teams, Google Chat and 100+ others** | Mostly free | **Apprise** (in `configuration.yaml`). Only needed for services with no integration of their own. | Depends on the service. |

**Not possible:** Apple iMessage, Google Messages (RCS) and Instagram don't let Home Assistant send messages.

### Text messages (SMS)

The free email-to-text addresses of AT&T, T-Mobile and Verizon no longer work. To send real texts, connect one of these to Home Assistant, then add it in HouseCall like a messaging app and type the person's mobile number:

- **A paid service:** Twilio SMS, ClickSend or Sinch.
- **A phone modem with a SIM card** plugged into your Home Assistant computer (**SMS notifications via GSM-modem** integration).
- **A spare Android phone with a SIM card**, using a gateway app such as *SMS Gateway for Android*.

## Send a test message

Check that someone can be reached, without sending a real alarm:

1. **Configure → Send a test message**.
2. Pick the person and how to send: **Everything they have**, **Home Assistant app only**, or **Messaging apps only**.
3. Select **Submit**. You'll see a ✅ or ❌ for each way HouseCall tried, with the reason if something failed.

Test messages aren't saved in the message history. The starter dashboard also has a **Test messaging apps** button.

## Use HouseCall in automations

In the automation editor, add the action **HouseCall: Send**. You only need three things: the message, who it's for, and how urgent it is.

```yaml
- action: housecall.send
  data:
    message: Water under the kitchen sink!
    to: everyone          # or a name: Jay, Grandma, or a list
    priority: critical    # info | normal | critical
```

### Examples

**Water leak: wake everyone**

```yaml
alias: Water leak
triggers:
  - trigger: state
    entity_id: binary_sensor.kitchen_leak
    to: "on"
actions:
  - action: housecall.send
    data:
      message: Water under the kitchen sink!
      priority: critical
```

**Laundry done: just me**

```yaml
alias: Dryer finished
triggers:
  - trigger: state
    entity_id: sensor.dryer_status
    to: complete
actions:
  - action: housecall.send
    data:
      message: Dryer finished
      to: Me
```

**Door left unlocked**

```yaml
alias: Entry door left unlocked
triggers:
  - trigger: state
    entity_id: lock.entry_door
    to: unlocked
    for: "00:10:00"
actions:
  - action: housecall.send
    data:
      message: The entry door has been unlocked for 10 minutes
      to: everyone
```

**Quiet board note**

```yaml
alias: Rain tonight
triggers:
  - trigger: time
    at: "16:00:00"
conditions:
  - condition: numeric_state
    entity_id: sensor.precipitation_probability
    above: 60
actions:
  - action: housecall.send
    data:
      message: Rain expected this evening
      priority: info
```

**Turn on the lights when an alarm is handled**

```yaml
alias: Leak handled
triggers:
  - trigger: event
    event_type: housecall_acknowledged
actions:
  - action: light.turn_on
    target:
      entity_id: light.kitchen
```

### All actions

| Action | What it does | Fields |
|---|---|---|
| `housecall.send` | Sends a message. | `message` (required), `to`, `priority`, `title` |
| `housecall.acknowledge` | Marks an alarm as handled and stops it. | `id` (required), `by` |
| `housecall.send_test` | Sends a test to one person and reports what worked. | `to` (required), `how`: `all`, `app` or `messaging` |
| `housecall.clear_history` | Removes every message. | none |

### Entity and events

| Name | What it is |
|---|---|
| `sensor.housecall` | How many alarms are waiting for an answer. |
| Event `housecall_acknowledged` | Fired when someone taps **I'm on it** (`id`, `by`). |
| Event `housecall_updated` | Fired whenever a message is sent, held, repeated or handled. |

## Card options

The card works with no settings. To change it, open the card's **⋮** menu and choose **Edit in YAML**.

```yaml
type: custom:housecall-card
title: Kitchen            # name at the top (default: HouseCall)
show_composer: false      # hide the message box, for a display-only screen
max_items: 20             # how many messages to show
```

## Troubleshooting

| Problem | What to do |
|---|---|
| A red **Configuration error** box instead of the card | Check **HouseCall** is listed under **Settings → Devices & services** (if not, do [Step 2](#step-2-add-housecall-to-home-assistant)). Then restart Home Assistant and hard-refresh the browser (**Ctrl + Shift + R**, or **Reset frontend cache** in the phone app). |
| The card looks old after an update | Restart Home Assistant and hard-refresh the browser. |
| A person shows **0 phones** | Pick their phone under **Configure → People from Home Assistant: show or hide**, or under **Settings → People → Track device**. |
| Alarms aren't loud on iPhone | Allow **Critical Alerts** for the Home Assistant app in iPhone **Settings → Notifications → Home Assistant**. |
| Alarms aren't loud on Android | In the Home Assistant app: **Settings → Companion app → Notification channels → alarm_stream**, and allow sound. |
| I can't find **I'm on it** on my phone | Press and hold the notification (iPhone) or swipe down on it (Android). |
| **I'm on it** on the card does nothing | Update HouseCall, restart Home Assistant, and hard-refresh the browser. |
| Tapping a notification opens the wrong page | Choose the page under **Configure → Phones, speakers, Glass Message Board and repeats**. |
| A Normal message didn't reach my phone | It's quiet hours. It shows on the board now and reaches phones in the morning. |
| Speakers don't read alarms | Pick both a speaker and a voice under **Configure → Phones, speakers, Glass Message Board and repeats**. |
| Nothing appears on Glass Message Board | Check Glass Message Board is installed, and that posting to it is on under **Configure**. |
| A messaging app isn't listed | Add that app's own integration first, then open **Configure → Messaging apps** again. |
| A test shows ❌ for a messaging app | Read the reason next to it. Common causes: Telegram – the person hasn't sent **/start** to your bot; Signal – the number is missing the country code; Messenger – they aren't a tester of your Facebook app yet. |
| An alarm says **Nobody answered** | Nobody tapped **I'm on it** before the last repeat, or Home Assistant restarted. |

Still stuck? Go to **Settings → System → Logs**, search for `housecall`, and include what you find when you [report a problem](https://github.com/Degederon/HouseCall/issues).

## Contributing

Bug reports and pull requests are welcome. When reporting a problem, please include your Home Assistant version, your phone type, and any relevant entries from the Home Assistant log.

## License

Released under the [MIT License](LICENSE).
