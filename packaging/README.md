# Packaging the PiDP-8/I

This repo is a git import of the upstream [PiDP-8/I fossil
repo](https://tangentsoft.com/pidp8i) (Warren Young). The packaging here
is the same machinery pidp10 and pidp11 use — `packaging/build-rpm.sh`,
one spec, COPR via `.copr/Makefile` — adapted to a project that is not
ours: the build system (autosetup), the service model and the program
behaviour are upstream's, and the packaging stays out of their way.

## The FHS layout, and how a /opt tree gets there

Upstream pidp8i is a single self-contained tree: `configure` bakes
`$PREFIX` (default `/opt/pidp8i`) into the generated scripts, into
`lib/pidp8i/dirs.py` (whose `build`/`media` anchors `install-target`
seds at install time), into the boot scripts, and into the systemd
unit templates; `pidp8i-sim` has the boot-script directory as a string
literal. The RPM builds that tree exactly the way upstream builds it —
at `/opt/pidp8i` — and then **relocates** it in `%install`: a move plus
a fixed sed table over the relocated text files. No compiled binary
embeds an install path except the one literal patch 0004 moves at
compile time, which is what makes the move safe.

| Path | Contents | Written at run time? |
|---|---|---|
| `/usr/bin/{pidp8i-sim,pdp8,...}`, `pidp8i`, `os8-run`, `os8-cp`, `os8pkg`, `palbart`, `d8tape`, `ptp2txt`, `txt2ptp`, `cc8`, `pidp8i-test`, `teco-pi-demo`, `usb-mount` | engines (NLS/ILS variants are hard links), assemblers, DECtape tools, console script | no |
| `/usr/libexec/pidp8i/scanswitch` | front-panel GPIO scanner | no |
| `/usr/share/pidp8i/lib/` | the private Python that drives the simulator (`simh.py`, `os8script.py`, `pidp8i/dirs.py`; `sys.path` rewritten) | no |
| `/usr/share/pidp8i/boot/` | boot scripts (attach media by absolute path into `/var/lib`) | no |
| `/usr/share/pidp8i/include/` | cc8 headers | no |
| `/usr/share/man/man1/palbart.1` | the one man page upstream ships | no |
| `/var/lib/pidp8i/media/` | OS/8 media (built, not downloaded) — **writable**: the guest writes to its RK05, `os8pkg` installs packages here | yes |
| `/var/lib/pidp8i/{run,save,obj}` | PID files, savestates, os8pkg staging — `%ghost`, created by tmpfiles | yes |
| `/etc/pidp8i/pidp8i.rc` | operator config (`noreplace`); the `pidp8i` script's path was rewritten here | yes, by you |
| `/etc/sudoers.d/pidp8i` | `pidp8i` group may `systemctl poweroff/reboot` (`noreplace`, 0440) | no |
| `/usr/lib/systemd/user/pidp8i.service` | generated user unit; `pidp8i install` copies it to `~/.local/share/systemd/user` | no |

The split that matters, same as pidp10: everything the simulator writes
lives under `/var/lib/pidp8i`, so `/usr` can stay read-only, an upgrade
cannot eat your OS/8 disk, and `ProtectSystem=strict` is possible. The
media images are package files inside the state tree: shipped
root:root with group-writable modes, assigned to `pidp8i:pidp8i` by a
tmpfiles `Z` line in `%post` and on every boot (deliberately — rpm
metadata stays free of the service account, so there is no bare
`group(pidp8i)` provide and no non-standard-uid noise); `dnf reinstall
pidp8i` restores corrupted images. Add operator accounts to the
`pidp8i` group to let them write the media and use the
poweroff/reboot sudoers rule.

## What the build does, and why it is slow

`make` builds SIMH, the panel code, the assemblers and the DECtape
tools — and then **boots the freshly built simulator** to assemble the
OS/8 system: `bin/*.rk05` and `bin/*.tu56` (the runtime disk, the
Combined Kit, the game packs) are produced during the build from the
OS/8 sources under `media/`. Nothing is downloaded; there is no blob
Source, and `media/os8/LICENSE.md` records DEC's permissive release.
Configure options (`doc/configure-options.md`) change what gets
assembled; the package builds upstream's defaults.

`%install` runs **`make install-target`**, never `install`: upstream's
`install` target additionally does `apt-get install screen`, `setcap
cap_sys_nice=eip`, `loginctl enable-linger`, `usermod`, and edits to
`~/.profile` and `/boot/cmdline.txt`. All of that is replaced by the
sysusers/tmpfiles/sudoers fragments and the units. `%install` also
fixes the generated `pidp8i` script's `install` subcommand, which bakes
in the build user's home as the unit destination, to use `$HOME`.

## The six patches

The tree expects a 2015 Raspbian: fossil, `pkg_resources`, and a K&R C
compiler. Fedora 45 has none of those, the FHS relocation needs one
literal moved, and the RPM needs its debuginfo the normal way.

1. `0001-tools-version-accept-PIDP8I_VERSION-override.patch` —
   `configure` runs `tools/version`, which wants a fossil checkout
   (the repo is git now). The patch lets the packager state the version
   (the spec passes `PIDP8I_VERSION`); upstream's `pkg:vUNKNOWN`
   fallback still covers plain tarball builds.
2. `0002-make-pkg_resources-optional.patch` — setuptools 83 dropped
   `pkg_resources`; it was `configure`'s gate and `lib/simh.py`'s way
   to ask "is pexpect ≥ 4". The patch drops the configure gate and
   falls back to `importlib.metadata`.
3. `0003-cc8-cross-build-with-gnu17.patch` — the cc8 cross-compiler is
   K&R C and GCC 15 builds C23 by default, which rejects old-style
   definitions. One flag: `-std=gnu17`.
4. `0004-boot-script-path-for-fhs-layout.patch` — `auto.def` defines
   `BOOTDIR` from the prefix, and `@BOOTDIR@` is substituted into
   `src/pidp8i/main.c.in` (the panel-switch boot-script fallback
   compiled into `pidp8i-sim`). The patch adds a `PIDP8I_BOOTDIR`
   configure-time override so the compiled-in path lands directly on
   `/usr/share/pidp8i/boot`; a sed cannot reach a compiled binary.
5. `0005-no-strip-on-install-for-rpm-debuginfo.patch` — `install-target`
   installs programs with `install -s`, which destroys the `-g` debug
   info before rpmbuild can split it (and makes the automatic
   debuginfo subpackage fail). Dropping that one flag lets brp-strip
   and find-debuginfo do the stripping, and `pidp8i-debuginfo` ships
   as usual. Packaging policy.
6. `0006-build-banner-no-host-identity.patch` — `auto.def` stamps
   `$USER@$(hostname)` and the build clock into the OS/8 boot banner
   (`media/os8/ock-init.tx.in`), which ships inside the RK05 images.
   In a build root that leaks the builder's identity and makes the
   image nondeterministic (in mock it printed `mockbuild@couldn't exec
   "hostname"`, since minimal build roots have no `hostname`). The
   patch adds `PIDP8I_BUILDUSER`/`PIDP8I_BUILDTS` configure-time
   overrides; the spec sets both (upstream's probe is unchanged
   otherwise, and the spec BuildRequires `hostname` so it works).
   Packaging policy.

1–3 are build-environment fixes worth proposing upstream; 4, 5 and 6
are packaging policy.

Upstream ships one man page (`palbart.1`). The rest of the user
entry points (`pdp8`, the `pidp8i-sim` family, `pidp8i`, `os8-run`,
`os8-cp`, `os8pkg`, `d8tape`, `ptp2txt`/`txt2ptp`, `cc8`, `usb-mount`,
`pidp8i-test`, `teco-pi-demo`) get distro-written pages under
`packaging/man/`, also candidates for upstreaming; the spec installs
them into `%{_mandir}/man1` beside upstream's. A separate upstream
bug: `install-target`'s module list omits `lib/pidp8i/util.py` (which
`os8script.py` imports), so the spec installs it directly — without
that line every installed OS/8 tool dies on import.

autosetup's configure compiles a bootstrap `jimsh0` (and probes for a
C++ compiler to do it) when no `jimsh`/`tclsh` is on `PATH`. The spec
`BuildRequires: jimtcl` so configure finds the system one; packaging
never builds a shell for the build host.

## Building the RPM

```sh
packaging/build-rpm.sh                 # RPMs + SRPM into ./dist-rpm (HEAD)
packaging/build-rpm.sh --worktree      # package the tree as it stands (testing)
packaging/build-rpm.sh --srpm-only     # SRPM only (what COPR runs)
rpmlint -c packaging/rpmlint.toml packaging/pidp8i.spec dist-rpm/*.rpm
```

`dist/` holds Source0–3 and the patches (all staged from the same
revision as the tarball), `dist-rpm/` holds only finished RPMs, and the
rpmbuild scratch stays in `~/rpmbuild` — same split as pidp10/pidp11.

## COPR

```sh
copr-cli create pdp8 --chroot fedora-45-aarch64 --chroot fedora-45-x86_64 \
    --scm-type git --scm-metadata https://github.com/<you>/pidp8i
copr-cli build pdp8 --nowait
dnf copr enable <you>/pdp8 && dnf install pidp8i
```

aarch64 and x86-64: the GPIO panel code compiles on both
(`auto.def` enables it on arm/aarch64 Linux; x86-64 gets the same
binaries minus panel hardware access), and the x86 chroot is what
catches architecture assumptions early.

## Verifying an install

```sh
pdp8                      # plain SIMH: sim> prompt;  q exits
pidp8i-sim                # panel engine; "No GPIO chips found" + exit 1 without a cabinet
pidp8i --help             # the console/session script
os8-run --help            # the OS/8 driver
palbart examples/add.pal  # the BARTGNO assembler
man palbart               # the relocated man page
grep -r /opt/pidp8i /usr/bin/pidp8i /usr/bin/os8-run /usr/share/pidp8i/lib /usr/share/pidp8i/boot  # nothing
ls -l /var/lib/pidp8i/media/os8/v3d.rk05   # group pidp8i, group-writable
```

A quick smoke of the writable path: `sudo -u pidp8i bash -c 'cd
/var/lib/pidp8i/media && os8-run <script>'` should be able to boot the
runtime disk without permission errors.

## Known gaps

- **os8pkg from-source package building** needs `pspec/` and
  `scripts/misc/`, which live in the source tree and are not installed
  (`dirs.src` points at an empty path and os8pkg fails cleanly).
  Installing prebuilt packages onto the RK05 images works.
- **License review.** The `License:` tag is the union of what the
  sources claim (SIMH/HPND, MIT, BSD-2), unreviewed, like pidp10's.
  The OS/8 media is DEC permissively released (`media/os8/LICENSE.md`)
  — fine for COPR, but a Fedora-review target wants the file-by-file
  pass first.
- **SELinux.** Executables run from a systemd *user* unit under the
  default targeted policy — untested under enforcing beyond smoke tests.
- No `debian/`, deliberately — same reasoning as pidp10's README.
