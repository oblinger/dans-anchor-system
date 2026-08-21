import importlib.util, json, sys, types, pathlib
sys.path.insert(0, str(pathlib.Path.home() / "ob/grove/warden/engine"))
import warden_fire as wf

W = pathlib.Path.home() / ".warden"
ir = json.load(open(W / "rules-ir.json"))
spec = importlib.util.spec_from_file_location("rules_all", W / "rules_all.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

V = "/Vol" + "umes"          # assembled so this fixture cannot trip the live guards
M = "__MAS" + "TERS__"
BASE = list(ir["base_traits"]) + ["anchor-base"]
ATTICUS = BASE + ["Container", "masterguard"]


def run(moment, traits, **ev):
    ctx = types.SimpleNamespace(
        anchor="test", moment=moment, traits=traits, git_aspect="", queries_text="",
        mode=None, facets=[], agent=None, ask_oracle=None, file_path=None, file=None,
        event=types.SimpleNamespace(tool=moment.split(":")[-1],
                                    target=ev.get("target"),
                                    input=ev.get("input") or {}))
    return wf.fire(ir, mod, moment, ctx, traits)


def backup_steers(steers):
    """Only R-backupguard's own denials — masterguard also fires on some cases."""
    return [s for s in steers if "sole custody" in s or "not a backup drive" in s]


CASES = [
    # must DENY
    ("cp onto BLACK",              "tool:pre:Bash",  BASE,    dict(input={"command": f"cp x.txt {V}/BLACK/inbox/"}), True),
    ("rsync onto 10T master",      "tool:pre:Bash",  BASE,    dict(input={"command": f"rsync -av ~/a/ {V}/10T/{M}/b/"}), True),
    ("rm on 8T",                   "tool:pre:Bash",  BASE,    dict(input={"command": f"rm -rf {V}/8T/scratch"}), True),
    ("redirect onto BEAST",        "tool:pre:Bash",  BASE,    dict(input={"command": f"echo hi >{V}/BEAST/note.txt"}), True),
    ("dd of= onto COPPER",         "tool:pre:Bash",  BASE,    dict(input={"command": f"dd if=/dev/zero of={V}/COPPER/z bs=1m"}), True),
    ("tar onto ULTRA BLUE",        "tool:pre:Bash",  BASE,    dict(input={"command": f"tar -czf '{V}/ULTRA BLUE/a.tgz' ~/a"}), True),
    ("diskutil eraseVolume",       "tool:pre:Bash",  BASE,    dict(input={"command": f"diskutil eraseVolume APFS New {V}/BLACK"}), True),
    ("bridge-nested rm",           "tool:pre:Bash",  BASE,    dict(input={"command": f"ssh haorui \"tmux send-keys -t w 'rm -rf {V}/10T/x' Enter\""}), True),
    ("unknown volume, fail closed","tool:pre:Bash",  BASE,    dict(input={"command": f"cp x {V}/SomeNewDrive/y"}), True),
    ("Write onto 10T master",      "tool:pre:Write", BASE,    dict(target=f"{V}/10T/{M}/notes.md"), True),
    ("Edit on BLACK",              "tool:pre:Edit",  BASE,    dict(target=f"{V}/BLACK/a/b.md"), True),

    # must PASS
    ("read cp FROM BLACK",         "tool:pre:Bash",  BASE,    dict(input={"command": f"cp {V}/BLACK/a.txt /tmp/"}), False),
    ("ls the drive",               "tool:pre:Bash",  BASE,    dict(input={"command": f"ls -la {V}/10T/{M}/"}), False),
    ("shasum on the drive",        "tool:pre:Bash",  BASE,    dict(input={"command": f"shasum -a 256 {V}/8T/x.jpg"}), False),
    ("diskutil info",              "tool:pre:Bash",  BASE,    dict(input={"command": f"diskutil info {V}/BLACK"}), False),
    ("diskutil apfs listCryptoUsers","tool:pre:Bash",BASE,    dict(input={"command": f"diskutil apfs listCryptoUsers {V}/10T"}), False),
    ("boot-volume symlink",        "tool:pre:Bash",  BASE,    dict(input={"command": f"touch {V}/∑/tmp/x"}), False),
    ("no volume at all",           "tool:pre:Bash",  BASE,    dict(input={"command": "rm -rf ~/scratch/x"}), False),
    ("Write inside the vault",     "tool:pre:Write", BASE,    dict(target="/Users/oblinger/ob/kmr/SYS/x.md"), False),

    # Atticus is exempt at every moment
    ("ATTICUS cp onto BLACK",      "tool:pre:Bash",  ATTICUS, dict(input={"command": f"cp x.txt {V}/BLACK/inbox/"}), False),
    ("ATTICUS Write onto 10T",     "tool:pre:Write", ATTICUS, dict(target=f"{V}/10T/{M}/notes.md"), False),
    ("ATTICUS Edit on BLACK",      "tool:pre:Edit",  ATTICUS, dict(target=f"{V}/BLACK/a/b.md"), False),
]

bad = 0
for label, moment, traits, kw, expect in CASES:
    steers = backup_steers(run(moment, traits, **kw))
    got = bool(steers)
    ok = (got == expect)
    bad += not ok
    print(("  ok   " if ok else "  FAIL ") + f"{'DENY' if expect else 'pass'}  {label}"
          + ("" if ok else f"   <- got {steers}"))
print()
print(f"{len(CASES) - bad}/{len(CASES)} red-checks passed" if not bad else f"{bad} FAILURE(S)")
sys.exit(1 if bad else 0)
