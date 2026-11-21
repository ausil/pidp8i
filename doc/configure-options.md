# PiDP-8/I Configure Script Options

This document describes the options you can pass to the `configure` script
when [building the PiDP-8/I software][readme] from source.  For a stock
build, no options are needed:

    $ ./configure && tools/mmake && sudo make install

The options below let you tailor the build to your hardware, preferences,
and available disk space.

[readme]: https://tangentsoft.com/pidp8i/doc/trunk/README.md


## Quick Reference

| Option | Purpose |
|--------|---------|
| [`--prefix`](#prefix) | Change the installation directory (default: `/opt/pidp8i`) |
| [`--lowercase`](#lowercase) | Control how lowercase keyboard input is handled |
| [`--no-lamp-simulator`](#nls) | Disable the incandescent lamp simulator (ILS) |
| [`--serial-mod`](#serial-mod) | Enable Oscar's serial mod GPIO wiring |
| [`--alt-serial-mod`](#alt-serial-mod) | Enable James L-W's alternative serial mod |
| [`--throttle`](#throttle) | Limit simulator CPU speed |
| [`--enable-savestate`](#savestate) | Persist simulator state across restarts |
| [`--disable-usb-automount`](#dub) | Disable automatic USB drive mounting |
| [`--disable-cc8-cross`](#dcc8) | Skip building the CC8 C cross-compiler |
| [`--runtime`](#copts-runtime) | Choice of runtime boot: Default is 'ock' OS/8 Combined Kit. Alternate is V3D |
| [`--disable-os8-*`](#disable-os8) | Leave out default OS/8 disk image components |
| [`--enable-os8-*`](#enable-os8) | Add optional OS/8 disk image components |
| [`--os8-minimal`](#os8-minimal) | Strip OS/8 disk image to bare minimum |
| [`--help`](#help) | Show all options |


## --prefix <a id="prefix"></a>

Perhaps the most widely useful `configure` script option is `--prefix`,
which lets you override the default installation directory, `/opt/pidp8i`.
There are many good reasons to change where the software gets installed,
but the default is also a good one, so unless you know for a fact that
you want to change this default, leave it alone.

For example, you might prefer that the installer put the built software
under your home directory.  This will do that:

    $ ./configure --prefix=$HOME/pidp8i && sudo make install

You might think that installing to a directory your user has complete
control over would remove the need for installing via `sudo`, but that
is not the case, since the installation script needs root privileges to
mark a few of the executables as having permission to run at high priority
levels, which improves the quality of the display, particularly with the
[incandescent lamp simulator][ils] feature enabled.


## --lowercase <a id="lowercase"></a>

The American Standards Association (predecessor to ANSI) delivered the
second major version of the ASCII character encoding standard the same
year the first PDP-8 came out, 1965. The big new addition? Lowercase.

That bit of history means that when the PDP-8 was new, lowercase was a
fancy new feature in the computing industry. That, plus the memory
savings you get from storing [stripped ASCII][sa] as two 6-bit
characters per 12-bit PDP-8 word means that most PDP-8 software did not
expect to receive lowercase ASCII text, particularly the older software.

The PDP-8 lived long enough to see lowercase ASCII input become common
in the computing industry.

As a result, PDP-8 software reacts in many strange and wonderful
ways when you give it lowercase input. Some software copes nicely,
other software crashes, and some software just sits there dumbly
waiting for you to type something!

This configuration option lets you control how you want your simulated
PDP-8/I to react to lowercase input:

*   **auto** — The default is for the software to attempt to "do the
    right thing." The simulator is configured to send lowercase input to
    the PDP-8 software running on it. Where we have the skill, will,
    need, and time for it, we have [patched][tty] some of the software
    we distribute that otherwise would not do the right thing with
    lowercase input to make it do so.

    This is *not* the option you want if you are a purist.

*   **pass** — This passes keyboard input through to the simulator
    unchanged, and no patches are applied to the PDP-8 software we
    distribute.

    This is the option for historical purists. If you run into trouble
    getting the software to work as you expect when built in this mode,
    try enabling CAPS LOCK.

*   **upper** — This option tells the PDP-8 simulator to turn lowercase
    input into upper case. This is the behavior we used for all versions
    of the PiDP-8/I software up through v2017.04.04.  Essentially, it
    tells the software that you want it to behave as through you've got
    it connected to an uppercase-only terminal like the Teletype Model 33 ASR.

    The advantage of this mode is that you will have no problems running
    PDP-8 software that does not understand lowercase ASCII text.

    The disadvantage is obvious: you won't be able to input lowercase
    ASCII text.

    The SIMH option we enable in this mode is bidirectional, so that if
    you run a program that does emit lowercase ASCII text — such as Rick
    Murphy's version of Adventure — it will be uppercased, just like an
    ASR-33 would do.

    Another trap here is that the C programming language requires
    lowercase text, so you will get a warning if you leave the default
    option **--enable-os8-cc8** set. Pass **--disable-os8-cc8** when
    enabling **upper** mode.

[sa]:  http://homepage.cs.uiowa.edu/~jones/pdp8/faqs/#charsets
[tty]: https://tangentsoft.com/pidp8i/wiki?name=OS/8+Console+TTY+Setup


## --no-lamp-simulator <a id="nls"></a>

The [incandescent lamp simulator][ils] (ILS) drives the front panel LEDs
in a way that mimics the glow and decay of the incandescent lamps in the
original PDP-8/I. It is CPU-intensive and requires a **multi-core** Pi to
run well. It is enabled automatically when building on multi-core hardware.

**Single-core Pi models** — including the Pi Zero 2 W and the Pi 3 Model
A+ — cannot run the ILS without consuming all available CPU. On these
boards, pass `--no-lamp-simulator` to use the original low-CPU-usage LED
driving method instead. The configure script detects single-core hardware
and sets this automatically, but you can set it explicitly if needed.

**Legacy ARMv6/v7 platforms** (original Pi Zero, Pi Zero W, Pi 1, Pi 2
v1.0/v1.1) are also single-core or close enough in CPU budget that NLS
is strongly recommended. Note that building from source on these platforms
is untested as of the current release; Raspberry Pi OS Bookworm is the
recommended base if you try.

Those on a multi-core host who want the low-CPU-usage LED driving method
for other reasons — such as running many background tasks, or when the CPU
is [heavily throttled][thro] — can also pass this option explicitly.


## --serial-mod <a id="serial-mod"></a>

If you have done [Oscar's serial mod][sm1] to your PiDP-8/I PCB and the
Raspberry Pi you have connected to it, add `--serial-mod` to the
`configure` command above.

If you do not give this flag at `configure` time with these hardware
modifications in place, the front panel will not work correctly, and
trying to run the software may even crash the Pi.

If you give this flag and your PCBs are *not* modified, most of the
hardware will work correctly, but several lights and switches will not
work correctly.


## --alt-serial-mod <a id="alt-serial-mod"></a>

This flag is for an [alternative serial mod by James L-W][sm2]. It
doesn't require mods to the Pi, and the mods to the PiDP-8/I board are
different from Oscar's.  This flag changes the GPIO code to work with
these modifications to the PiDP-8/I circuit design.

See the linked mailing list thread for details.

As with `--serial-mod`, you should only enable this flag if you have
actually done the mods as specified by James L-W.

This option is a pure alternative to [`--serial-mod`](#serial-mod): you
can leave both off, but you cannot pass both.


## --throttle <a id="throttle"></a>

See [`README-throttle.md`][thro] for the values this option takes.  If
you don't give this option, the simulator runs as fast as possible.


## --enable-savestate <a id="savestate"></a>

By default, the PiDP-8/I starts up with the core state undefined and
runs the boot script you've selected either with the IF switches or by
passing it on the command line to `pidp8i-sim` or `pdp8`.  This brings
the simulator up in a known state, with no persistence between restarts
other than what was written to the simulated storage devices before the
last shutdown.

On a real PDP-8 with core memory, however, the values in memory will
persist for weeks without power; core memory on a PDP-8 is not zeroed on
power-up, unlike RAM on a modern computer.  Since the CPU doesn't start
executing anything on power-up in a stock PDP-8 configuration, this
means the user can toggle in a program/OS restart address with the
switch register (SR), load it into the program counter (PC) with the
Load Addr switch, then START the CPU to restart their program without
having to reload it from tape or disk.

There were also several power fail and restart options designed and made
available for the PDP-8 series throughout its lifetime. One of these —
the KP8-I for the PDP-8/I — would detect a power fail condition, then in
the brief time window while the power supply's reservoir capacitors kept
the computer running, this option card would raise an interrupt, giving
a user-written routine up to 1 millisecond to save important registers
to core so they would persist through the power outage. Then on
power-up, it would start executing at core location 00000, where another
user routine would load those registers back from core to restart the
system where it left off before the power failed.

Giving this option gives roughly the same effect for all generated boot
scripts: any time the simulator is shut down gracefully, it saves all
key simulator state — registers, core, device assignments, etc. — to a
disk file. Then on restart, that script will reload that saved state if
it finds the saved state file.

This is not identical to a KP8-I in that it doesn't require any
user-written PDP-8 code to run, which is why it's optional: it's
ahistoric with respect to the way the included OSes normally ran.

In absence of a hardware option like the KP8-I, a more accurate
simulation would only save the core memory state to a host-side disk
file and reload it on simulator re-start. You can get that behavior atop
the current mechanism by adding commands like the following to each
bootscript you want to affect:

    EVAL HLT
    DEP L 0
    DEP AC 0
    DEP DF 0
    DEP IF 0
    DEP MQ 0
    DEP PC 0

That zeroes the key registers and prevents the CPU from running as it
normally would after giving the `RESTORE` command to SIMH.


## --disable-usb-automount <a id="dub"></a>

When you install the software on a [systemd]-based Linux
system, we normally configure the OS to automatically mount USB drives
when they are initially plugged in, which allows the `SING_STEP` + `DF`
media image auto-attach feature to work smoothly. That is, if you plug
in a USB memory stick holding a `*.pt` file containing a paper tape
image, you want the simulator to be able to find it if you have the DF
switches set to 1, telling the PiDP-8/I front panel code to look for
something to attach to the simulator's paper tape reader.

This feature may interfere with other uses of USB, such as when booting
your Pi from an external USB hard disk drive. Give this option to
disable the feature.

(Alternately, you could modify our `etc/udev.rules` and/or
`bin/usb-mount` scripts so that they work cooperatively with your local
USB setup rather than conflicting with it.)

[systemd]: https://www.freedesktop.org/wiki/Software/systemd/


## --disable-cc8-cross <a id="dcc8"></a>

Give this option if you do not want to build Ian Schofield's `cc8` C
cross-compiler on the host.

Because the cross-compiler is needed to build the CC8 native OS/8
compiler, disabling the cross-compiler also causes the native compiler
to be left off the bootable OS/8 RK05 disk image, as if you'd passed the
`--disable-os8-cc8` configuration option.


## --runtime <a id="copts-runtime"></a>

This option offers a choice of boot media used for the IF=0 and IF=7 cases.

Previously the default was an extended version of OS/8 V3D, as distributed
by DEC, plus some patches we applied. 

We now build the whole OS from source as offered in the 
[OS/8 Combined Kit][ock], which is the last complete release of OS/8
released by DEC. (See that link for details.)

To change back to v3d as the boot image:

    $ ./configure --runtime=v3d && sudo make install

Note that the Combined Kit was also considered v3d with 
extensions and updates so the startup banner will say,
"OS/8 V3D Combined Kit".

Whichever OS version gets booted up, it will include our extensions and
third party software as described below, and configurable by you.

[ock]: https://tangentsoft.com/pidp8i/dir?ci=tip&name=src/os8/ock


## --disable-os8-\* <a id="disable-os8"></a>

Several default components of the [OS/8 RK05 disk image][os8di] used by
boot options IF=0 and IF=7 can be left out to save space and build time:

*   **--disable-os8-advent** — Leave out the [Adventure][advent] game.

*   **--disable-os8-basic-games** - Leave out the BASIC games and demos which
    primarily come from DEC's book "101 BASIC Computer Games."

*   **--disable-os8-cc8** - Leave out Ian Schofield's native OS/8 CC8
    compiler and all of its ancillary files.

*   **--disable-os8-chekmo** — Leave out John Comeau's
    [CHECKMO-II chess implementation][chess].

*   **--disable-os8-crt** — Suppress the [console rubout behavior][tty]
    enabled while building the OS/8 binary RK05 disk image. You
    probably only want to do this if you have attached a real teletype
    to your PiDP-8/I, and thus do not want video terminal style rubout
    processing.

*   **--disable-os8-dcp** — Leave out the DCP disassembler.

*   **--disable-os8-e8** — Leave out [Bill Silver's E8][e8], an
    Emacs-like screen editor.

*   **--disable-os8-focal** - Do not install any version of FOCAL on the
    OS/8 system disk. This option sets `--disable-os8-uwfocal` and
    overrides `--enable-os8-focal69`, both discussed below.

*   **--disable-os8-fortran-ii** - Leaves out the FORTRAN II compiler,
    SABR, the linking loader (`LOADER`), the `LIBSET` tool, and the
    `*.RL` library files.  This option is ignored unless you also give
    `--disable-os8-cc8` because the OS/8 version of CC8 is built atop
    this subsystem.

*   **--disable-os8-fortran-iv** - Leave the FORTRAN IV compiler out.

*   **--disable-os8-init** - Do not install `RKB0:INIT.TX` or its "show
    on boot" script, `INIT.CM`.  Rather than disable the default on-boot
    init message, you may want to edit `media/os8/init.tx.in` to taste
    and rebuild.

*   **--disable-os8-kermit-12** - Leave out the Kermit-12 implementation
    normally installed to `RKA0:`

*   **--disable-os8-macrel** - Leave the MACREL v2 assembler and its
    associated FUTIL V8B tool out.

*   **--disable-os8-src** - Do not build the `v3d-src.rk05` disk
    image from the OS/8 source tapes.  This is not controlled by
    `--os8-minimal` because that only affects the bootable disk images.

*   **--disable-os8-uwfocal** - Leave out the U/W FOCAL V4E programming
    environment normally installed to `RKA0:`.

    Note that the default installation only installs `UWF16K.SV`, not
    the rest of the files on `media/os8/subsys/uwfocal*.tu56`. There is
    much more to explore here, but we cannot include it in the default
    installation set because that would overrun OS/8's limitation on the
    number of files on a volume.

You can later remove each of these after installation using
[our package manager][os8pkg].

[advent]: http://www.rickmurphy.net/advent
[chess]:  https://chessprogramming.wikispaces.com/CHEKMO-II
[e8]:     https://tangentsoft.com/e8/
[os8di]:  https://tangentsoft.com/pidp8i/doc/trunk/README.md#os8di
[os8pat]: https://tangentsoft.com/pidp8i/doc/trunk/doc/os8-patching.md
[os8pkg]: https://tangentsoft.com/pidp8i/doc/trunk/doc/os8pkg.md


## --enable-os8-\* <a id="enable-os8"></a>

There are a few file sets not normally installed to the [OS/8 RK05 disk
image][os8di] used by boot options IF=0 and IF=7. You can install them
with the following options:

*   **--enable-os8-music** — The `*.MU` music scores and Rich Wilson's
    associated compiler (`MUSIC.PA`) and player overlay (`PLAYOV.PA`)
    are not normally installed to the built OS/8 binary RK05 disk image
    because the Raspberry Pi reportedly does not emit sufficient RFI at
    AM radio frequencies when running these programs to cause audible
    music on a typical AM radio, the very point of these demos.  Until a
    way is found around this problem — what, low RFI is a *problem* now?
    — this option will default to "off".

*   **--enable-os8-vtedit** — This option installs a default-run macro
    pack called VTEDIT which causes the OS/8 version of TECO to run in
    full-screen mode and to react to [several special keyboard
    commands][uvte] not normally recognized by TECO.

    This feature is disabled by default because the VTEDIT macro pack
    changes the way TECO operates, and many people want TECO to behave
    like *TECO*. VTEDIT was first created during the PDP-8's commercial
    lifetime, so enabling this option is not an anachronism, but TECO is
    much older and had a much more wide-reaching impact in history, so
    we choose to provide unvarnished TECO by default.

    That having been said, people don't go to a ren fair and expect to
    experience the historical ubiquity of typhoid fever, so do not feel
    guilty if you choose to try this option.

*   **--enable-os8-focal69** — Because the default installation includes
    U/W FOCAL, we have chosen to leave [FOCAL,1969][f69] out by default
    to save space on the O/S 8 system disk. You can give this option to
    install this implementation alongside U/W FOCAL, or you can couple
    this option with `--disable-os8-uwfocal` to reverse our choice of
    which FOCAL implementation to install by default.

    You should know that the reason we made this choice is that the
    version of FOCAL,1969 we are currently shipping is fairly minimal: we
    believe we are shipping the original DEC version of FOCAL,1969 plus a
    few carefully-selected overlays. There are many more overlays and
    patches available on the Internet for FOCAL,1969, but we have not had
    time to sort through these and make choices of which ones to ship or
    how to manage which ones get installed. Thus our choice: we want to
    provide the most functional version of FOCAL by default, and within
    the limitations of the time we have chosen to spend on this, that is
    U/W FOCAL today.

    (See our [U/W FOCAL manual supplement][suppd] for a list of
    differences between these versions of FOCAL, which implicitly
    explains why we chose it.)

    It is possible that we will eventually add enough patches and
    overlays to FOCAL,1969 that it will become more powerful than U/W
    FOCAL, so we might then choose to switch the defaults, but that is
    just speculation at the time of this writing.

You can later add each of these after installation using
[our package manager][os8pkg].

[f69]:   https://tangentsoft.com/pidp8i/wiki?name=Running+FOCAL%2C1969
[suppd]: https://tangentsoft.com/pidp8i/doc/trunk/doc/uwfocal-manual-supp.md#diffs
[uvte]:  https://tangentsoft.com/pidp8i/wiki?name=Using+VTEDIT


## --os8-minimal <a id="os8-minimal"></a>

This sets all `--enable-os8-*` flags to false and all `--disable-os8-*`
flags to true. This mode overrides any `--enable-os8-*` flag, so if you
want a minimal install plus just one or two features, it's simplest to
give this flag and then use [our package manager][os8pkg] to add in the
elements you want rather than pass a bunch of `--disable-os8-*` options.

This option may not do some things you think it should:

1.  This flag's name is aspirational, not a promise of an ideal: our
    current "minimal" installation could be stripped down further. For
    example, we currently have no way to leave out OS/8's BASIC
    interpreter, even though no core OS services depend on it.

2.  This option does not affect [the `--lowercase` option](#lowercase)
    because that affects only OS/8's command interpreter and OS/8's BASIC
    implementation, so we deem it to be orthogonal to the purpose of the
    `--os8-minimal` flag, which only affects the optional post-`BUILD`
    features. You may therefore wish to give `--lowercase=none` along
    with `--os8-minimal`.

3.  This option does not affect `--disable-os8-src`, because it only
    suppresses optional features in the primary bootable OS/8 media.  If
    you want minimal OS/8 boot media without a separate source code
    data disk, give this option as well.

4.  Although this option disables *display* of the `INIT.TX` file on
    boot, the file is still generated, on purpose.  First, it acts as
    build documentation, recording what was built and when.  Second,
    you may wish to enable this welcome message later, and it's rather
    painful to go back through the build process to generate it after
    the fact.


## --help <a id="help"></a>

Run `./configure --help` for more information on your options here.


[ils]:  https://tangentsoft.com/pidp8i/wiki?name=Incandescent+Lamp+Simulator
[sm1]:  https://obsolescence.wixsite.com/obsolescence/pidp-8-details#i7g9qvpr
[sm2]:  https://groups.google.com/d/msg/pidp-8/-leCRMKqI1Q/Dy5RiELIFAAJ
[thro]: https://tangentsoft.com/pidp8i/doc/trunk/README-throttle.md
