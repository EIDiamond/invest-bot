# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## 2022-06-16

The Bot has been changed to send asynchronously telegram messages. 
The main reason was telegram api is working pretty long, sometimes more than a few seconds.
After all changes telegram messages don't block trade logic.

NOTE: Most of the trading API requests are using synchronous version. The main reason was divide trading and telegram,
without any changes in trade logic.      

### Major changes

- Trade logic and telegram api are working asynchronously. 
- Changed dependencies: 
  - Removed 'python-telegram-bot'
  - Added 'aiogram' 
