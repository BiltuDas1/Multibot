from pyrogram import Client

def main():
    print("Telegram String Session Generator\n")
    APP_ID = int(input("Enter APP ID: "))
    API_HASH = input("Enter API HASH: ")
    print()

    with Client("Link-Bypasser", api_id=APP_ID, api_hash=API_HASH, in_memory=True) as app:
        session_str = app.export_session_string()

        if app.get_me().is_bot:
            user_name = input("Enter the username: ")
            app.send_message(user_name, "**Below is your String Session**")
            app.send_message(user_name, f'`{session_str}`')
        else:
            app.send_message("me", "**Below is your String Session**")
            app.send_message("me", f'`{session_str}`')

        print("\nDone. Please check your Telegram Saved Messages/user's PM for the String Session")


if __name__ == "__main__":
    main()