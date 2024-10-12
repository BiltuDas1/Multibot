## Description

A Telegram personal bot for sending text messages anonynmously, Saving Restricted Content, and Much more.

## Environments

- `BOT_TOKEN` The telegram bot Token.
- `OWNER_IDs` String with IDs which are owner of the bot, Seperated by spaces (e.g `10 11`, `1030 1110 2000`).
- `GROUP_ID` Group ID where the FORWARD bot will send user dm to a specific topic, make sure the Bot is Admin of the
  Group.
- `API_ID` Your Telegram account api_id, can be collected from my.telegram.org.
- `API_HASH` Your Telegram account api_hash, can be collected from my.telegram.org.
- `STRING_SESSION` Pyrogram String Session, if you don't have then use the `get_string_session.py` to generate one.
- `OWNER_USERNAME` Public username of the Owner, it will be shown to normal users.
- `MONGO_URI` MongoDB database URI, You can collect one from MongoDB Atlas.
- `DUMP_CHAT` Channel ID where the SRC Module copies all the data and then copy it to the User, Please Note: The Bot
  should have Post Permission and the Channel shouldn't restrict the content forwarding from the channel in order the
  bot to work.
- `CACHE` Set it to true/yes if you want the bot to quickly copy the items to the user that is already saved by the bot,
  otherwise set it to false/no, Default is false/no. The DUMP_CHAT Environment must be set otherwise it will throw an
  error.
- `SPAMWATCH_TOKEN` Set this token, if you want this bot to automatically ban those users who are already banned in
  SpamWatch(Applicable to new users only, old users are not affected). For more information,
  visit [docs.spamwat.ch](https://docs.spamwat.ch/).
- `ENABLE_COMBOT` Set it to true/yes if you want to enable [combot.org](https://combot.org/) protection (Applicable to
  new users only, old users are not affected). Otherwise set it to false/no. Default is true/yes.

## Deploy

### Docker Image (Recommended)

Use the [Docker image](https://hub.docker.com/r/biltudas1/multibot) to deploy into any kind of VPS

### Deploy from the Source Code

1. Clone this repo (or Fork it depends on the VPS)
2. Use `sh run.sh` to start the bot. (It should be the starting point of the bot)

```
Note: Don't run the main.py file directly, for handling the power off/restart signal the run.sh is required to be executed as the parent process of main.py. Also it handles all kind of locks to prevent race conditions.
```

## External References

- [Pyrofork](https://github.com/Mayuri-Chan/pyrofork): Used for interacting with the Telegram API.
- [Flask](https://github.com/pallets/flask): Used for exposing a specific port to work
- [Save Restricted Content Repo](https://github.com/bipinkrish/Save-Restricted-Bot): Used as the base repo for the SRC
  Module
- [httpx](https://github.com/encode/httpx): For interacting with External HTTP APIs (i.e Combot API, SpamWatch API)