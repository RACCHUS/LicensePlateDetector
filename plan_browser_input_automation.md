## Native Host Script Status

The `native_host.py` script is set up for basic native messaging and echo testing. It will echo back any 'fill_plate' message received from the extension. No changes are needed for initial testing.

To integrate with your main app (e.g., to forward the plate, log, or trigger actions), you can extend this script as needed.
## Native Messaging Host Registration (Windows)

1. Edit `chrome_extension/native-messaging-host.json` and replace `__EXTENSION_ID__` with your Chrome extension's actual ID (found in chrome://extensions after loading unpacked extension).
2. Copy `native-messaging-host.json` to:
	`C:\Users\<your-username>\AppData\Local\Google\Chrome\User Data\NativeMessagingHosts\`
3. Register the host by running (in cmd):
	```
	mkdir "%LOCALAPPDATA%\Google\Chrome\User Data\NativeMessagingHosts"
	copy chrome_extension\native-messaging-host.json "%LOCALAPPDATA%\Google\Chrome\User Data\NativeMessagingHosts\com.licenseplatedetector.host.json"
	```
4. Ensure `native_host.py` is at the path specified in the manifest and is executable with Python.
5. Load the extension in Chrome and test communication.

For more details, see: https://developer.chrome.com/docs/apps/nativeMessaging/
## Inputting Logic

The current keystroke-based inputting logic will NOT be removed. It will remain as a backup in case the extension/native messaging fails or is not available.
## Chrome Extension Installation

During development or for personal use, you can load the extension as an "unpacked extension" in Chrome:
1. Go to chrome://extensions/
2. Enable "Developer mode" (top right)
3. Click "Load unpacked" and select the extension’s folder

For production or distribution, you can package the extension as a `.crx` file or publish it to the Chrome Web Store (optional).

You do not need to publish it to use it on your own machine or within your organization.
# Browser Input Automation Plan

## Goals
- Automate license plate input into a browser text field with minimal disruption to the user.
- Support a hotkey to start/stop automated input.
- Only show notifications when OCR confidence is low.


## Solution Selection

**Primary:**
### 1. Chrome Extension
- Build a Chrome browser extension that listens for messages from the desktop app and fills the field in the browser.
- Pros: Secure, robust, works in background, not affected by clipboard, does not require field focus, can be limited to specific sites, less likely to be blocked by sensitive sites, works in Chrome and most Chromium-based browsers.
- Cons: Requires extension install, some browser-specific code.

**Backup:**
### 2. Browser Automation (Selenium/Playwright)
- Use automation tools to set the value of the browser input field directly.
- Pros: Can target field by ID/name, works in background, robust.
- Cons: May be detected/blocked by sensitive sites, requires setup, may not work with all web apps (esp. with security restrictions).

### (Clipboard+Paste is not recommended for sensitive or background use.)

## Recommended Features
- Hotkey to start/stop automated input.
- Notification only on low OCR confidence.
- Option to choose between clipboard+paste, browser automation, or extension.

## Implementation Steps
1. Add hotkey support to start/stop input automation in the app.
2. Build a Chrome extension to receive plate data and fill the field in the browser. **[Done: Scaffold created]**
## Communication Method

We will use **Native Messaging** for secure, local communication between the desktop app and the Chrome extension.

- Chrome will launch a registered native host (your app or a helper script) and communicate via stdin/stdout.
- This is secure, works offline, and is recommended for sensitive or production use.
- Requires a native messaging host manifest and registration (see Chrome extension docs for details).

WebSocket is not used, as Native Messaging is more secure and robust for this use case.
3. (If extension is not possible) Add browser automation for direct field input (Selenium/Playwright).
4. Ensure notifications only appear on low-confidence OCR results.

## Next Steps
- Implement step 1 (hotkey support).
- Implement step 2 (native messaging integration between desktop app and Chrome extension).
- If extension is not possible, proceed to step 3 (browser automation).
