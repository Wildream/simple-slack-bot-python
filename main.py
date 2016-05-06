from bot import SlackBot


token = 'yourtoken'  # Slack token, obtainable via https://api.slack.com/tokens

if __name__ == '__main__':
    sb = SlackBot(token)
    sb.run()
