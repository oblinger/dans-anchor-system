# Fix: Sudo Without Password

Configure sudo to not require a password for the admin group. Needed after OS reinstall or new machine setup.

## Runbook

### 1. Open visudo

```bash
export VISUAL=nano
sudo visudo
```

**You MUST use `visudo` — no other editor. It validates the file before saving.**

### 2. Find and change the admin line

Change:
```
%admin  ALL=(ALL) ALL
```

To:
```
%admin  ALL=(ALL) NOPASSWD:ALL
```

### 3. Save and exit

Press `^X`, then `Y`, then `Enter`.

### 4. Report

---

**>>> USER ACTION: Run `sudo visudo` in your terminal — this requires interactive editing <<<**

**>>> USER ACTION: Run `sudo visudo` in your terminal — this requires interactive editing <<<**

**>>> USER ACTION: Run `sudo visudo` in your terminal — this requires interactive editing <<<**

---

This cannot be done non-interactively because `visudo` validates the sudoers file and an error would lock out sudo entirely.
