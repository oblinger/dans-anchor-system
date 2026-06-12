-- vox-process.applescript — Mail rule action for the SKA `vox` skill's email
-- mode (originally F093). Wraps the `vox-process` shell script with an Apple
-- Mail rule that catches "VOX"-subject messages, downloads any audio attachment,
-- and hands it off for transcription.
--
-- Install: compiled into ~/Library/Application Scripts/com.apple.mail/ob_process_email.scpt
--   osacompile -o "$HOME/Library/Application Scripts/com.apple.mail/ob_process_email.scpt" \
--             "$HOME/.claude/skills/vox/scripts/vox-process.applescript"
-- (The compiled name stays `ob_process_email.scpt` to match the existing
-- Mail rule action — that rule references the compiled file by its name in
-- the Application Scripts folder, not by path.)
--
-- Wire once in Mail ▸ Settings ▸ Rules:
--   Condition: Subject contains "VOX"
--   Action:    Run AppleScript ▸ ob_process_email
--
-- For each matching message it saves any audio attachment (mp3/m4a/wav/caf/…,
-- e.g. an Apple Voice Memo) to a staging dir and launches vox-process
-- (backgrounded, so a long transcription never blocks Mail). The shell script
-- dispatches on the subject to the right handler.
--
-- NOTE: the audio attachment must be DOWNLOADED locally for the save to work.
-- Set the account's "Download Attachments" to "All" (Mail ▸ Settings ▸ Accounts
-- ▸ <account> ▸ Account Information). The retry loop below also gives Mail a few
-- seconds to finish fetching an attachment that is still downloading when the
-- rule fires.

property procBin : "/Users/oblinger/.claude/skills/vox/scripts/vox-process"
property stagingDir : "/Users/oblinger/Library/Caches/ob_process_email/"
property audioExts : {"mp3", "m4a", "wav", "caf", "aac", "aiff", "aif", "mp4", "m4b"}

-- lowercase file extension of a name, or "" if none
on fileExt(fn)
	set AppleScript's text item delimiters to "."
	set parts to text items of fn
	set AppleScript's text item delimiters to ""
	if (count of parts) < 2 then return ""
	return last item of parts
end fileExt

using terms from application "Mail"
	on perform mail action with messages theMessages for rule theRule
		do shell script "mkdir -p " & quoted form of stagingDir
		-- prune staged audio older than a day so the cache can't grow unbounded
		do shell script "find " & quoted form of stagingDir & " -type f -mtime +1 -delete 2>/dev/null || true"
		set stamp to do shell script "date '+%Y%m%d-%H%M%S'"
		set idx to 0
		repeat with theMessage in theMessages
			set theSubject to ""
			try
				set theSubject to subject of theMessage
			end try
			-- first pass: save any .vtt caption file (the "as-sent" transcript)
			set vttPath to ""
			repeat with theAttachment in (mail attachments of theMessage)
				set attName to (name of theAttachment) as string
				if (my fileExt(attName)) is "vtt" then
					set tryPath to stagingDir & stamp & "-sub.vtt"
					try
						save theAttachment in (POSIX file tryPath)
						set vttPath to tryPath
					end try
				end if
			end repeat
			-- second pass: save audio attachment(s) and launch the processor
			repeat with theAttachment in (mail attachments of theMessage)
				set attName to (name of theAttachment) as string
				set ext to my fileExt(attName)
				-- AppleScript `contains` is case-insensitive, so "M4A" matches "m4a"
				if audioExts contains ext then
					set idx to idx + 1
					set savePath to stagingDir & stamp & "-" & idx & "." & ext
					-- the attachment may still be downloading when the rule fires;
					-- retry the save (~16s) to give Mail time to fetch the data
					set savedOK to false
					set lastErr to ""
					set tries to 0
					repeat until (savedOK or tries > 7)
						set tries to tries + 1
						try
							save theAttachment in (POSIX file savePath)
							set savedOK to true
						on error errMsg
							set lastErr to errMsg
							delay 2
						end try
					end repeat
					if savedOK then
						-- background the (possibly slow) processing; don't block Mail
						do shell script "nohup " & quoted form of procBin & " " & quoted form of savePath & " " & quoted form of theSubject & " " & quoted form of vttPath & " >/dev/null 2>&1 &"
					else
						do shell script "printf '%s  %s\\n' \"$(date '+%Y-%m-%d %H:%M:%S')\" " & quoted form of ("save failed after retries for " & attName & ": " & lastErr) & " >> " & quoted form of (stagingDir & "applescript-error.log")
					end if
				end if
			end repeat
		end repeat
	end perform mail action with messages
end using terms from
