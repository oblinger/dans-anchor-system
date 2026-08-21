-- stage-email.applescript — create a Mail.app draft and open it. NEVER sends.
-- usage: osascript stage-email.applescript <to> <cc> <subject> <body-file> <from-address>
-- <cc> may be "" ; multiple addresses in <to>/<cc> are comma-separated.
-- There is deliberately no `send` verb anywhere in this file.

on splitAddrs(s)
	set AppleScript's text item delimiters to ","
	set parts to text items of s
	set AppleScript's text item delimiters to ""
	set out to {}
	repeat with p in parts
		set t to my trimWS(p as string)
		if t is not "" then set end of out to t
	end repeat
	return out
end splitAddrs

on trimWS(s)
	repeat while s starts with " "
		set s to text 2 thru -1 of s
	end repeat
	repeat while s ends with " "
		set s to text 1 thru -2 of s
	end repeat
	return s
end trimWS

on run argv
	set theTo to item 1 of argv
	set theCc to item 2 of argv
	set theSubject to item 3 of argv
	set bodyFile to item 4 of argv
	set fromAddr to item 5 of argv

	set theBody to (read (POSIX file bodyFile) as «class utf8»)

	with timeout of 60 seconds
		tell application "Mail"
			set senderAcct to missing value
			repeat with a in accounts
				if (email addresses of a as string) contains fromAddr then set senderAcct to a
			end repeat
			if senderAcct is missing value then error "no Mail account matches " & fromAddr

			set msg to make new outgoing message with properties {subject:theSubject, content:theBody, visible:true}
			tell msg
				set sender to fromAddr
				repeat with addr in my splitAddrs(theTo)
					make new to recipient at end of to recipients with properties {address:addr}
				end repeat
				repeat with addr in my splitAddrs(theCc)
					make new cc recipient at end of cc recipients with properties {address:addr}
				end repeat
			end tell
			activate
			return "staged: " & theSubject
		end tell
	end timeout
end run
