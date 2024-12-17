TEXTS = {
    "invalid_channel_id": (
        "<b>Invalid channel ID. Please provide a valid channel ID starting with '-100'.</b>"
    ),
    "permission_denied": (
        "<b>You don't have permission to post in this channel.</b>"
    ),
    "no_message_to_post": (
        "<b>Please provide a valid channel ID and reply to a message using /cpost <channel_id>.\n"
        "Use /chelp to know about formatting.\n"
        "If you don't know your Channel Id, just forward me any message from your channel and reply "
        "to that message with /id.</b>"
    ),
    "failed_to_post": "<b>Failed to post the message. Error: {error}</b>",
    "post_success": (
        "<b>Message posted to channel {channel_id} successfully!</b>"
    ),
    "unsupported_media": "<b>Unsupported media type to forward.</b>",
    "random_sticker": [
        "CAACAgIAAxkBAAItAmdbY-9IY20HNfLFeeboOOex74M0AAL9AQACFkJrCqSvYaKm6vLJHgQ",
        "CAACAgIAAxkBAAIs1GdbWBhGfsD2U3Z2pGiR-d64z08mAAJvAAPb234AAZlbUKh7k4B0HgQ",
        "CAACAgIAAxkBAAIsz2dbV_286mg26Vx67MOWmyG-WvK7AAJtAAPb234AAXUe7IXy-0SlHgQ",
        "CAACAgQAAxkBAAIs_mdbY-Zk1JR7yRLoWsi8NbJEMFerAALVGAACOqGIUIer-Up9iv5aHgQ",
        "CAACAgQAAxkBAAIs-mdbY96brNo0bbqiAT0h9aHmGjfZAAISDgACQln9BFRvgD6jmKybHgQ"
    ],
    "error_messages": {
        "UserNotParticipant": "Bot is not a member of the channel.",
        "PeerIdInvalid": (
            "The bot's access to the channel is invalid. Please add the bot to the group again. "
            "If the bot is already in the group, try removing and re-adding it."
        ),
        "ChatAdminRequired": (
            "The bot needs to be an admin in the group & channel to perform this action."
        ),
    #},
    "HELP_TEXT":( """
<b>Telegram Markdown & Formatting Guide:</b>

<i>You can use these formatting methods in your messages:</i>

<b>1. Bold:</b>
<code>*Your Text*</code> → <b>Your Text</b>

<b>2. Italic:</b>
<code>_Your Text_</code> → <i>Your Text</i>

<b>3. Underline:</b>
<code>__Your Text__</code> → <u>Your Text</u>

<b>4. Strikethrough:</b>
<code>~Your Text~</code> → <s>Your Text</s>

<b>5. Monospace:</b>
<code>`Your Text`</code> → <code>Your Text</code>

<b>6. Preformatted Block:</b>
<code>```Your Text```</code> → 
<pre>Your Text</pre>

<b>7. Spoiler:</b>
<code>||Your Text||</code> → <tg-spoiler>Your Text</tg-spoiler>

<b>8. Quote:</b>
Simply type <code>&gt;</code> at the beginning of a line:
<code>&gt; Your Text</code> → 
<blockquote>Your Text</blockquote>

<b>9. Inline Link:</b>
<code>[Text](https://example.com)</code> → [Text](https://example.com)

<b>10. Custom Inline Code:</b>
<code>```
<code>Custom text or programming code</code>
```</code> → Displays a block of code.

<b>11. Inline Buttons:</b>
<code>{BUTTON TEXT}-{URL}</code>
<i>Note:</i> Don't Use <b>Wrong URL</b> &amp; Don't Add <b>Extra Spaces</b> 
<b> Use Command 
<b> /cpost to post in channel & </b>
<b> /ppost to post private post (that can't be forwarded) </b>
<b> Join @Filmykeedha For More Updates.</b>
    """,
    "STICKER_ID": "CAACAgIAAxkBAAIMU2dBzBWjzGCg_x2tFumZ76z5l5JiAAJiAANOXNIpTqLDGEjEK3EeBA"
        ),
    "AVAILABLE_TEXT_METHODS": (""" 
**Using HTML Methods in Telegram**

Telegram supports HTML formatting in messages. Below are some commonly used methods and advanced techniques:

1. **Basic Formatting**:
   - **Bold**: `<b>Bold Text</b>` → **Bold Text**
   - **Italic**: `<i>Italic Text</i>` → *Italic Text*
   - **Underline**: `<u>Underlined Text</u>` → __Underlined Text__
   - **Strikethrough**: `<s>Strikethrough Text</s>` → ~~Strikethrough Text~~

2. **Links**:
   - Hyperlink: `<a href="https://example.com">Click Here</a>` → [Click Here](https://example.com)
   - Mention a User: `<a href="tg://user?id=123456789">Username</a>` → [Username](tg://user?id=123456789)

3. **Monospace Text**:
   - Single-line code: `<code>Inline Code</code>` → `Inline Code`
   - Block code: `<pre>Block Code</pre>` → 
     ```
     Block Code
     ```

4. **Nested Formatting**:
   - Combine styles: `<b><i>Bold and Italic</i></b>` → ***Bold and Italic***

5. **Advanced Methods**:
   - **Spoiler**: Use `<span class="tg-spoiler">Spoiler Text</span>` → Hidden text revealed upon clicking.
   - **Custom Emojis**: `<tg-emoji emoji-id="1234567890123456789">🙂</tg-emoji>` → Custom emoji for premium users.

6. **Media Captions**:
   - You can use all the above methods in media captions as well:  
     `<b>Bold Caption</b> <i>with Italics</i>`.

---

**Example**:

```html
<b>Welcome!</b> Here is an <a href="https://telegram.org">example</a> of Telegram HTML formatting.
Click the <span class="tg-spoiler">spoiler</span> to reveal hidden text.
<code>Inline Code</code> or a block of code:
<pre>def hello_world():
    print("Hello, world!")</pre>
    
    """
                              )}
