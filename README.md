# NUSSU Publicity Bot

A simple Telegram bot running on Python3 to automate forwarding messages from one chat to another, specifically designed for NUSSU Publicity needs.

## Starting The Bot

Once you've set up your configuration (see below), simply run:

```shell
python -m forwarder
```

or with poetry (recommended)

```shell
poetry run forwarder
```

## Setting Up The Bot

### Requirements

NUSSU Publicity Bot supports Python 3.9 and higher.

### Configuration

There are two mandatory files for the bot to work: `.env` and `chat_list.json`.

#### `.env`

Template `.env` can be found in `sample.env`. Rename it to `.env` and fill in the following values:

- `BOT_TOKEN` - Telegram bot token. Obtain this from [@BotFather](https://t.me/BotFather).
- `OWNER_ID` - The integer representing your Telegram user ID.
- `REMOVE_TAG` - Set to `True` if you want to remove the "Forwarded from" tag in forwarded messages.

#### `chat_list.json`

Template `chat_list.json` can be found in `chat_list.sample.json`. Rename it to `chat_list.json`.

This file contains the list of chats for message forwarding. Below is an example configuration:

```json
[
  {
    "source": -10012345678,
    "destination": [-10011111111, "-10022222222#123456"]
  },
  {
    "source": "-10087654321#000000",
    "destination": ["-10033333333#654321"],
    "filters": ["word1", "word2"]
  },
  {
    "source": -10087654321,
    "destination": [-10033333333],
    "blacklist": ["word3", "word4"]
  },
  {
    "source": -10087654321,
    "destination": [-10033333333],
    "filters": ["word5"],
    "blacklist": ["word6"]
  }
]
```

- `source` - Chat ID to forward messages from. For Topic Groups, explicitly include the topic ID.
- `destination` - Array of destination chat IDs, supporting both groups and topic chats.
- `filters` (optional) - Messages containing any word in this array **will** be forwarded.
- `blacklist` (optional) - Messages containing any word in this array **will not** be forwarded.

### Python Dependencies

Install necessary dependencies using one of the following:

```shell
poetry install --only main
```

or with pip:

```shell
pip3 install -r requirements.txt
```

### Running in a Docker Container

#### Requirements

- Docker
- Docker Compose

Ensure `.env` and `chat_list.json` are correctly configured before starting the container.

To launch:

```shell
docker compose up -d
```

To view logs:

```shell
docker compose logs -f
```

## Using the Bot

### Publicity Message Workflow

1. Use the `/publicise` command to begin the process.
2. Send a photo (optional) or type `na` if no photo is required.
3. Type your publicity message. The bot will forward the message to the admin group for approval.

### Custom Formatting Syntax

Messages can include custom formatting using the following syntax:

- **Bold:** `(b)Text(/b)`
- *Italic:* `(i)Text(/i)`
- __Underline__: `(u)Text(/u)`
- ~~Strikethrough~~: `(s)Text(/s)`
- [Hyperlink](https://example.com): `[Text](https://example.com)`

The bot will convert this syntax to the correct format when sending messages.

### Admin Actions

- Admins can approve or reject a message by clicking the respective button.
- If rejecting, the admin can use the `/feedback` command followed by the reason for rejection. Example:
  ```text
  /feedback The message needs clearer details about the event.
  ```

## Credits

- Original inspiration: [AutoForwarder-TelegramBot](https://github.com/saksham2410/AutoForwarder-TelegramBot)
