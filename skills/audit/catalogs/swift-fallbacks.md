# Silent Fallbacks — Swift

Swift-specific silent fallback patterns.

## Semgrep Patterns (mechanical)

- `try?` — discards the error, returns nil
- `catch { }` — empty catch block
- `catch { return }` — catch with silent return

## Agent Reasoning (Swift-specific)

**`try? ... ?? default` — swallows error and substitutes:**
```swift
let data = try? loadConfig() ?? Config()
```
The error from `loadConfig()` is lost. Was it a permission issue? Missing file? Corrupt data? All become `Config()`.

**`guard let x = ... else { return }` — silent guard return:**
```swift
guard let connection = database.connect() else { return }
```
The function silently does nothing if the database is down. The caller has no idea.

**Optional chaining depth:**
```swift
window?.contentView?.subviews.first?.frame
```
If any link is nil, the entire expression is nil. Which one failed? Add a check: if more than 3 `?.` in a chain, flag it.

**`as?` downcasting without else:**
```swift
if let view = sender as? NSButton {
    // handle button
}
// silently ignores if sender is not NSButton
```
Is it correct to ignore non-button senders, or is this masking a type error?

**Delegate methods with empty implementations:**
```swift
func tableView(_ tableView: NSTableView, didSelect row: Int) {
    // TODO: implement
}
```
Required protocol method with empty body — silently does nothing.

**`@objc` methods that swallow errors:**
```swift
@objc func handleNotification(_ notification: Notification) {
    guard let info = notification.userInfo else { return }
}
```
If userInfo is unexpectedly nil, the notification is silently dropped.
