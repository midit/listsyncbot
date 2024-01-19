
![Logo](https://i.imgur.com/PEpnelV.jpg)

# ListSync Telegram Bot

![](https://img.shields.io/github/repo-size/midit/listsyncbot)
![](https://img.shields.io/github/last-commit/midit/listsyncbot/main)
![](https://img.shields.io/github/issues/midit/listsyncbot)
![](https://img.shields.io/github/issues-closed/midit/listsyncbot)

Telegram bot designed to facilitate collaborative **shopping list** management among **multiple users**. The bot allows users to **create** and **join** sessions, where they can collectively **build** and **update** a list of products they intend to purchase.
## Features

- **Session Creation and Joining:** Users can initiate a new shopping session or join an existing one by using the `/create_session`, `\cs` or `/join_session`, `\js` commands respectively. The bot assigns a unique session code to each session for identification.
- **Product List Management:** Participants within a session can add products to the shared list by sending messages in a specific format (product name followed by quantity). They can also view the current list by using the `/list` command or mentioning keywords like "список" or "с" in their messages.
- **Product Removal:** Users can remove specific products from the list by sending a message with a list of indices (1-based) corresponding to the products they want to remove. The bot handles these requests and updates the list accordingly.
- **Session Closure:** The session creator or participants can close a session using the `/close_session` command. When the last participant leaves a session, the session is automatically closed and its associated product list is removed.
## Usage/Examples


1. Start the bot by using the `/start` command.
2. Create a new session using `/create_session` or `/cs` command. Share the provided session code with others.
3. Join an existing session with `/join_session` or `/js` followed by the session code.
4. Add products to the shared list by sending messages with product names and quantities.
5. Remove products from the list by sending a message with indices of products to be removed.
6. Use `/list` or mention keywords to view the current product list.
7. Close a session with `/close_session` or `/end` command.


## Authors

- [@delovebit](https://www.github.com/midit)

## License

[GNU General Public License v3.0](https://github.com/midit/SCR_DSHelper/blob/main/LICENSE)
