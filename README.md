# Getting Started with the PiDP-8/I Software

## Orientation

You will be reading this either:

*   …[online][tlrm], within [the Fossil project repository][home]; or
*   …as a text file within the [source packages][src]; or
*   …in the read-only [GitHub mirror][ghm].

The latter two are secondary outputs from the first, being the PiDP-8/I
software development project's home.

This is open source software: you are welcome to
[contribute to the project][ctrb].

[ctrb]: https://tangentsoft.com/pidp8i/doc/trunk/CONTRIBUTING.md
[ghm]:  https://github.com/tangentsoft/pidp8i
[home]: https://tangentsoft.com/pidp8i/
[src]:  https://tangentsoft.com/pidp8i/#src
[tlrm]: https://tangentsoft.com/pidp8i/doc/trunk/README.md


## Start Here <a id="start-here"></a>

Not sure where to begin? Pick the row that matches your situation:

| My situation | Where to go |
|---|---|
| **Brand new arm64 Pi — easiest path** | [Download our binary OS image][osimg] → flash to SD card → [OS image guide][osimg] |
| **Brand new arm64 Pi — stock Raspberry Pi OS** | [Preparing Your Pi](#preparing) → [Getting the Software](#unpacking) → [Build and install](#configuring) <br>Available as a quick start with the script found on the [Build Setup][buildsetup] wiki page |
| **Legacy Pi (ARMv6/v7)** — untested | Raspberry Pi OS Bookworm + build from source; see [Prerequisites](#prerequisites) and [`--no-lamp-simulator`][copts-nls] if single-core |
| **Existing Pi OS, adding PiDP-8/I software** | [Getting the Software onto Your Pi](#unpacking) |
| **Already installed, want to update** | [Taking Updates](#updates) |
| **Want bleeding-edge or to contribute** | [CONTRIBUTING.md][ctrb] → clone Fossil repo |
| **Just want the OS/8 disk images** (for SIMH elsewhere) | [OS/8 RK05 Media][os8media] on the project home page |
| **Hardware LEDs/switches not working** | [Testing Your PiDP-8/I Hardware](#testing) |
| **Something differs from Oscar's version** | [Major Differences][mdif] wiki page |

[upd]:        https://tangentsoft.com/pidp8i/#updating
[os8media]:   https://tangentsoft.com/pidp8i/#os8
[copts-nls]:  https://tangentsoft.com/pidp8i/doc/trunk/doc/configure-options.md#nls
[buildsetup]: https://tangentsoft.com/pidp8i/wiki?name=Build+Setup


## Who This Document Is For

This document serves users at several levels of involvement with the
PiDP-8/I software. Pick the level that matches how you want to engage:

| Level | You want to… | Where to look |
|-------|--------------|---------------|
| **1 — Just run it** | Turn it on and use the PDP-8 | [Using the Software](#using) |
| **2 — Take updates** | Get bug fixes and new features | [Taking Updates](#updates) |
| **3 — Runtime tailoring** | Adjust behavior without rebuilding | [Runtime Configuration](#runtime) |
| **4 — Build-time tailoring** | Change configure options, custom rebuild | [Build Configuration](#options) |
| **5 — Deep internals** | Understand OS/8 media, contribute | [OS/8 Media Reference](#os8di), [CONTRIBUTING.md][ctrb] |


## Using the Software <a id="using"></a>

For an in-depth tour of the software's capabilities — FOCAL-69, OS/8 on
DECtape, TSS/8 multi-user, Spacewar!, and more — see Oscar's
[How to use the PiDP-8/I][oght] documentation.
There are [significant differences][mdif] from that document,
particularly in how front panel switches work; see below.


### Front Panel Switch Operations <a id="switches"></a>

**The three white IF switches** (leftmost on the switch panel) select
what the PDP-8 boots into. Set them before power-up, or at any time
while running: set the switches, then use the activation sequence below.

| Octal | IF switches | Boots into |
|-------|-------------|------------|
| 0 | 000 | OS/8 on RK05 disk cartridge (default) |
| 1 | 001 | RIM Loader at 7756, paper tape/punch enabled |
| 2 | 010 | TSS/8 multi-user system |
| 3 | 011 | OS/8 on DECtape |
| 4 | 100 | Spacewar! |
| 5 | 101 | (empty slot) |
| 6 | 110 | ETOPS multi-user OS/8 clone |
| 7 | 111 | Same as slot 0 |

**The DF switches** select which virtual device to mount a USB image onto:

| Octal | DF switches | Device |
|-------|-------------|--------|
| 1 | 001 | PTR (paper tape reader) |
| 2 | 010 | PTP (paper tape punch) |
| 3 | 011 | DT0 (TU55 DECtape unit 0) |
| 4 | 100 | DT1 (TU55 DECtape unit 1) |
| 5 | 101 | RX0 (RX01/02 floppy unit 0) |
| 6 | 110 | RX1 (RX01/02 floppy unit 1) |
| 7 | 111 | RK1 (second RK05 unit) |

**Triggering switch actions** requires an ordered sequence — this changed
from Oscar's documentation due to [Cycle Accurate][mdif] mode, which
restores authentic PDP-8/I front panel behavior:

| Action | Sequence |
|--------|----------|
| Boot different OS or mount USB | Turn `Sing_Inst` on → hold `Cont` → toggle `Sing_Step` |
| Reboot the host Pi | Turn `Sing_Inst` on → hold `Start` → toggle `Sing_Step` |
| Shut down the host Pi | Turn `Sing_Inst` on → hold `Stop` → toggle `Sing_Step` |

After mounting USB media, turn `Sing_Step` and `Sing_Inst` back off, then
press `Cont` to resume. After rebooting to a different OS, pressing `Cont`
may not be necessary, but will be needed if you were slow releasing the
switches.

After setting IF to boot a different OS, reset IF back to 000 so as not
to disrupt any following front panel actions.

The boot options above correspond to the [OS/8 media images](#os8di)
described later in this document.


### Starting, Attaching, and Stopping

1.  To start the simulator running in the background:

        $ pidp8i start

    This will happen automatically on reboot unless you disable the
    service, such as in order to run one of the various [forks of Deeper
    Thought][dt2].

2.  To attach your terminal to the running simulator, run the same
    script without an argument:

        $ pidp8i

3.  To detach from the simulator's terminal interface while leaving the
    PiDP-8/I simulator running, type <kbd>Ctrl-A d</kbd>.  You can
    re-attach to it later with a `pidp8i` command.

4.  To shut the simulator down while attached to its terminal interface,
    type <kbd>Ctrl-E</kbd> to pause the simulator, then at the `simh>`
    prompt type `quit`.  Type `help` at that prompt to get some idea of
    what else you can do with the simulator command language, or read
    the [SIMH Users' Guide][sdoc].

5.  To shut the simulator down from the command line:

        $ pidp8i stop

    That then lets you run something like [Incandescent Thought][ith]
    without conflict.

You might also find our [Learning More](/#learning) links helpful.

[ith]: https://tangentsoft.com/pidp8i/wiki?name=Incandescent+Thought


### The Background Simulator Service <a id="systemd" name="unit"></a>

The PiDP-8/I software distribution uses [systemd] to run the background
PDP-8 simulator as a user-level service, so you needn't give `sudo` on
any command to interact with that service, as you did in older versions
of the software.

Although you can give verbose `systemctl` commands like this:

    $ systemctl --user start pidp8i

…we've provided a wrapper for such commands:

    $ pidp8i start
    $ pidp8i stop
    $ pidp8i restart
    $ pidp8i status -l

*All* arguments are passed to `systemctl`, not just the first, so you
can pass any flags that `systemctl` accepts, as in the last example.

[systemd]: https://www.freedesktop.org/wiki/Software/systemd/


## Taking Updates <a id="updates"></a>

### Binary OS Image Users

If you are running [our pre-built binary OS image][osimg], see the
[Updating the binary OS release][upd] instructions on the project home
page.

### Source Install Users

Before rebuilding on the PiDP-8/I hardware, stop the running simulator —
both the simulator and a build are CPU-intensive, and thermal throttling
can cause build timeouts:

    $ pidp8i stop

Then update your local clone and rebuild:

    $ cd ~/src/pidp8i/trunk
    $ fossil update && tools/mmake && sudo make install

You normally do not need to re-run `./configure` after an update, but if
automatic re-configuration fails, you can force it:

    $ make reconfig


## Source Installation <a id="source-install"></a>

This section covers installing the PiDP-8/I software onto a stock
Raspberry Pi OS. If you are using [our pre-built binary OS image][osimg],
this entire section does not apply — your Pi is already set up.

If you would rather run a script that handles the steps below
automatically, see the [Build Setup][buildsetup] wiki page.


### Prerequisites <a id="prerequisites"></a>

*   A **64-bit ARM (arm64)** Raspberry Pi with the 40-pin GPIO connector:
    the Pi 3 (all models), Pi 4, Pi 5, Pi Zero 2 W, or the rare Pi 2
    Model B v1.2 (BCM2837). The original Pi Zero, Pi Zero W, Pi 1, and
    Pi 2 v1.0/v1.1 are ARMv6/v7 and are not supported by our binary OS
    image; building from source on Raspberry Pi OS Bookworm may work but
    is untested.

*   An SD card imaged with Raspberry Pi OS [stock][rpios], or with
    [our pre-built binary OS image][osimg].

*   This software distribution, unpacked somewhere convenient within the
    filesystem on the Raspberry Pi. That's already done on [our
    pre-built binary OS images][osimg], in `~/pidp8i`. When adding it
    to the stock OS, we recommend that you unpack it in your `HOME`
    directory or somewhere else your user has read/write access.

*   While those with no Linux and Raspberry Pi knowledge may be able to
    follow our instructions blindly, we recommend that such persons look
    at [the official Raspberry Pi documentation][rpfd], particularly
    their [Linux][rpfl] and [Raspberry Pi OS][rpfr] guides. The book
    "[Linux for Makers][lfm]" by Aaron Newcomb is also well-reviewed.

*   Building the software requires several tools and libraries, some of
    which you may not already have.

    On Raspberry Pi OS, say:

        $ sudo apt update
        $ sudo apt install build-essential libraspberrypi-dev \
             libncurses-dev perl python3-pexpect python3-yaml \
             python3-pkg-resources

Under Homebrew, such as on macOS, say instead:

    $ brew install make perl python python-setuptools coreutils
    $ pip3 install --break-system-packages --user 'setuptools<70' pexpect pyyaml

See the [OS Compatibility][othos] page for explanation of these arguments and
guidance for other platforms.

[lfm]:   https://www.makershed.com/products/make-linux-for-makers
[othos]: https://tangentsoft.com/pidp8i/wiki?name=OS+Compatibility
[rpfd]:  https://www.raspberrypi.org/documentation/
[rpfl]:  https://www.raspberrypi.org/documentation/linux/
[rpfr]:  https://www.raspberrypi.com/documentation/computers/os.html
[rpios]: https://www.raspberrypi.org/software/


### Preparing Your Pi <a id="preparing"></a>

If you've just barely unpacked Raspberry Pi OS onto an SD card and are
now trying to get the PiDP-8/I software distribution working on it, stop
and go through the [Raspberry Pi documentation][rpd] first. At the
absolute minimum, run `raspi-config` and make sure the Localization
settings are correct. The defaults are for the United Kingdom, home of
the Raspberry Pi Foundation, so unless you live there, the defaults are
probably incorrect for *your* location.

[rpd]: https://www.raspberrypi.org/documentation/


### Getting the Software onto Your Pi <a id="unpacking"></a>

This section is for those reading this on [our project home site][home]
or via [its GitHub mirror][ghm]. If you are instead reading this as the
`README.md` file within an unpacked distribution of the PiDP-8/I
software, [skip to the next section](#configuring).


#### Transferring the Source Tarball to the Pi <a id="transferring"></a>

There are many ways to get the `*.tar.gz` file onto your Pi:

1.  **Copy the file to the SD card** you're using to boot the Pi.
    When inserted into a Mac or Windows PC, typically only the `/boot`
    partition mounts as a drive your OS can see.  (There's a much
    larger partition on the SD card, but most PCs cannot see it.)
    There should be enough free space left in this small partition to
    copy the tarball over.  When you boot the Pi up with that SD card,
    you will find it in `/boot`.

2.  **Pull the file down to the Pi** over the web, directly to the Pi:

        $ wget -O pidp8i.tar.gz https://goo.gl/JowPoC

    That will get you a file called `pidp8i.tar.gz` in the current
    working directory containing the latest *stable release.* To get the
    bleeding edge tip-of-trunk version instead, say:

        $ wget -O pidp8i.tar.gz https://tangentsoft.com/pidp8i/tarball

3.  **SCP the file over** to a running Pi from another machine.
    If your Pi has [OpenSSH installed and running](#sshd), you can use
    [WinSCP][wscp], [Cyberduck][cd], [FileZilla][fz] or another SCP
    or SFTP-compatible file transfer program to copy the file to the
    Pi over the network.

[cd]:   https://cyberduck.io/
[fz]:   https://filezilla-project.org/
[wscp]: https://winscp.net/eng/

4.  **Clone the Fossil repository** using the instructions in the
    [`CONTRIBUTING.md` file][ctrb]. (Best for experts or those who wish to
    become experts.)

Alternatively, switch to our pre-built binary OS images based on the
latest stable release (currently Debian Trixie, 64-bit ARM), with the
PiDP-8/I software already downloaded, configured, and installed.
See the [OS images documentation][osimg] for installation instructions.


#### Unpacking the Software on Your Pi

Having transferred the distribution file onto your Pi, unpack it with:

    $ tar xf pidp8i.tar.gz


### Configuring, Building and Installing <a id="configuring"></a>

#### Before you begin

If you are performing a build on the PiDP-8/I hardware, stop any currently
running pidp8i instance:

    $ pidp8i stop

Running the pidp8i software and performing a build are both very CPU
intensive activities. Thermal throttling has been observed to outstrip
timeout waits for completion of actions in the expect scripts that drive
the build.

Heat sinks for your Pi are HIGHLY RECOMMENDED.

#### The build proper

For a stock build, say:

    $ cd ~/pidp8i
    $ ./configure && tools/mmake && sudo make install

You may want to add options to the `configure` step; see
[Build Configuration](#options).

The "`mmake`" step above will take quite a while to run, especially on
the slower Pi boards. The longest single step is building the OS/8 disk
packs from source media. Be patient; the build process almost certainly
isn't frozen.

Only the `make install` step needs to be done via "`sudo`". No other
step requires root privileges.

After running "`sudo make install`" the first time, you will have to log
out and back in to get the installation's "bin" directory into your
`PATH`.


## Runtime Configuration <a id="runtime"></a>

The `pidp8i` command sources a Bourne shell script called `pidp8i.rc` —
normally installed in `/opt/pidp8i/etc` — which you may edit to override
certain details of the way that script runs. The intended purpose is to
give you a place to define local overrides for default variables:


### `SCREEN_MANAGER=screen` <a id="rc-screen-manager"></a>

By default, the PiDP-8/I software distribution installs and uses [GNU
`screen(1)`][gscr] to allow the simulator to run in the background yet be
reattached from a later terminal session, then possibly later to be
backgrounded once again. Without the intermediation of something like
`screen`, the simulator would either forever be in the background — so
we'd have to export the console [another way][scons] — or we'd have to
give up on background startup, requiring that users fire the simulator
up interactively any time they wanted to use it. Using a screen manager
lets us have it both ways.

The `SCREEN_MANAGER` setting is for use by those that want to use
one of the alternatives to GNU `screen`:

*   **screen**: The default, per above.

*   [**tmux**][tmux]: A popular alternative to `screen`, especially on
    on BSD platforms. Note that the "attention" character for `tmux`
    is <kbd>Ctrl-B</kbd> by default, not <kbd>Ctrl-A</kbd> as with
    `screen`.

*   **none**: This mode is for interactive use, allowing you to
    run the installed simulator with the installed media without any
    screen manager at all.

    In this mode, the `pidp8i` and `pidp8i start` commands do the
    same thing: run the simulator directly attached to your current
    interactive terminal. The `pidp8i stop` command becomes a no-op,
    since stopping the simulator is then done in the standard SIMH way:
    <kbd>Ctrl-E, quit</kbd>.

Note that the alternative screen managers are not installed by default.
If you set `SCREEN_MANAGER=tmux`, you must then ensure that `tmux` is in
fact installed before the `pidp8i` script goes to try and use it. From
the Pi's command line:

    $ sudo apt install tmux

Switching between configured screen managers must be done while the
simulator is stopped.

[gscr]:  https://www.gnu.org/software/screen/
[scons]: /wiki?name=Serial+or+Telnet+PDP-8+Console
[tmux]:  https://tmux.github.io/


### Simplifying Boot and Login <a id="auto-login"></a>

The setup and installation instructions above assume you will be using
the Raspberry Pi OS as a network server, offering SSH if nothing else.
Thus, we do not try to bypass any Linux security mechanisms, not wanting
to create an insecure island on your network.

However, if you want to run your system more as an appliance, you can
cast away some of this security to get auto-login and other convenient
behaviors:

*   [Serial or Telnet PDP-8 Console](https://tangentsoft.com/pidp8i/wiki?name=Serial+or+Telnet+PDP-8+Console)
*   [How to Run a Naked PiDP-8/i](https://tangentsoft.com/pidp8i/wiki?name=How+to+Run+a+Naked+PiDP-8/I)
*   [VNC for Remote GUI Access](https://www.raspberrypi.org/documentation/remote-access/vnc/)


## Build Configuration <a id="options"></a>

You can change many things about the way the software is built and
installed by giving options to the `configure` script.  The full
reference for all options is in [`doc/configure-options.md`][copts].

A brief summary:

| Option | Purpose |
|--------|---------|
| [`--prefix`][copts-prefix] | Change the installation directory (default: `/opt/pidp8i`) |
| [`--lowercase`][copts-lc] | Control how lowercase keyboard input is handled |
| [`--no-lamp-simulator`][copts-nls] | Required for single-core Pi hardware (Pi Zero 2 W, Pi 3A+); also useful on legacy ARMv6/v7 platforms |
| [`--serial-mod`][copts-sm] | Enable Oscar's serial mod GPIO wiring |
| [`--alt-serial-mod`][copts-asm] | Enable James L-W's alternative serial mod |
| [`--throttle`][copts-thr] | Limit simulator CPU speed |
| [`--enable-savestate`][copts-ss] | Persist simulator state across restarts |
| [`--disable-usb-automount`][copts-usb] | Disable automatic USB drive mounting |
| [`--disable-cc8-cross`][copts-cc8] | Skip building the CC8 C cross-compiler |
| [`--runtime`][copts-runtime] | Choice of runtime boot: Default is 'ock' OS/8 Combined Kit. Alternate is V3D |
| [`--disable-os8-*`][copts-dis] | Leave out default OS/8 disk image components |
| [`--enable-os8-*`][copts-ena] | Add optional OS/8 disk image components |
| [`--os8-minimal`][copts-min] | Strip OS/8 disk image to bare minimum |

[copts]:         https://tangentsoft.com/pidp8i/doc/trunk/doc/configure-options.md
[copts-prefix]:  https://tangentsoft.com/pidp8i/doc/trunk/doc/configure-options.md#prefix
[copts-lc]:      https://tangentsoft.com/pidp8i/doc/trunk/doc/configure-options.md#lowercase
[copts-nls]:     https://tangentsoft.com/pidp8i/doc/trunk/doc/configure-options.md#nls
[copts-sm]:      https://tangentsoft.com/pidp8i/doc/trunk/doc/configure-options.md#serial-mod
[copts-asm]:     https://tangentsoft.com/pidp8i/doc/trunk/doc/configure-options.md#alt-serial-mod
[copts-thr]:     https://tangentsoft.com/pidp8i/doc/trunk/doc/configure-options.md#throttle
[copts-ss]:      https://tangentsoft.com/pidp8i/doc/trunk/doc/configure-options.md#savestate
[copts-usb]:     https://tangentsoft.com/pidp8i/doc/trunk/doc/configure-options.md#dub
[copts-cc8]:     https://tangentsoft.com/pidp8i/doc/trunk/doc/configure-options.md#dcc8
[copts-runtime]: https://tangentsoft.com/pidp8i/doc/trunk/doc/configure-options.md#copts-runtime
[copts-dis]:     https://tangentsoft.com/pidp8i/doc/trunk/doc/configure-options.md#disable-os8
[copts-ena]:     https://tangentsoft.com/pidp8i/doc/trunk/doc/configure-options.md#enable-os8
[copts-min]:     https://tangentsoft.com/pidp8i/doc/trunk/doc/configure-options.md#os8-minimal


### Overwriting the Local Simulator Setup <a id="overwrite-setup"></a>

When you run the `sudo make install` step on a system that already has an
existing installation, it purposely does not overwrite two classes of
files:

1.  **The binary PDP-8 media files**, such as the RK05 disk image that
    holds the OS/8 image the simulator boots from by default. These media
    image files are considered "precious" because you may have modified
    the OS configuration or saved personal files to the disk the OS
    boots from. See [OS/8 Media Reference](#os8di) for details on these
    files.

2.  **The PDP-8 simulator configuration files**, installed as
    `$prefix/share/boot/*.script`, which may similarly have local
    changes, and thus be precious to you.

Sometimes this "protect the precious" behavior isn't what you want.
(Gollum!) One common reason this may be the case is that you've damaged
your local configuration and want to start over. Another common case is
that the newer software you're installing contains changes that you want
to reflect into your local configuration.

You have several options here:

1.  If you just want to reflect the prior PDP-8 simulator configuration
    file changes into your local versions, you can hand-edit the
    installed simulator configuration scripts to match the changes in
    the newly-generated `boot/*.script` files under the build directory.

2.  If the change is to the binary PDP-8 media image files — including
    the [generated OS/8 disk images](#os8di) — and you're unwilling to
    overwrite your existing ones wholesale, you'll have to mount both
    versions of the media image files under the PDP-8 simulator and copy
    the changes over by hand.

3.  If your previously installed binary OS media images — e.g. the
    [OS/8 RK05 disk image](#os8di) that the simulator boots from by
    default — are precious but the simulator configuration scripts
    aren't precious, you can just copy the generated `boot/*.script`
    files from the build directory into the installation directory,
    `$prefix/share/boot`.  (See the `--prefix` option above for the
    meaning of `$prefix`.)

4.  If neither your previously installed simulator configuration files
    nor the binary media images are precious, you can force the
    installation script to overwrite them both with a
    `sudo make mediainstall` command after `sudo make install`.

    Beware that this is potentially destructive! If you've made changes
    to your PDP-8 operating systems or have saved files to your OS
    system disks, this option will overwrite those changes!


## OS/8 Media Reference <a id="os8di"></a>

The media images included with this distribution — RK05 disk images and
TU56 tape images — are what the front panel [IF switch table](#switches)
boots into. This section describes how they are built and what they
contain.


### The OS/8 Disk Images

For the first several years of the PiDP-8/I project, the OS/8 RK05 disk
image included with the PiDP-8/I software (called `os8.rk05`) was based
on an image of a real RK05 disk pack that someone allegedly found in a
salvaged PDP-8 system.  Parts of the image were corrupt, and not all of
the pieces of software worked properly with the other parts.
It was also a reflection of the time it was created and used out in the
world, which was not always what we would wish to use today.

Starting in late 2017, [several of us][aut] built a series of tools to
generate OS/8 media images from pristine source files in a repeatable,
[testable][pkgtst] way, culminating in [Bill Cattey's `os8-run`][ori],
which backs other features like [the `--disable-os8-*` configuration
options](#disable-os8).

The resulting set of media images entirely replace the old ones and go
well beyond each besides.  All prior features are still available,
though some features present on the old images are disabled by default,
requiring either [`--enable-os8-*` configure options](#enable-os8) or
[package manager commands][os8pkg] to add features back in. Mostly,
though, the new media images are more functional than the old ones.

If you wish to know the full details of how these media images are
created, see the documentation for [`os8-run`][ori] and that for
[`class simh`][cs].

The remainder of this section describes some aspects of these media
images which are not clear from the descriptions of the `--*-os8-*`
configuration options above.

[aut]:    https://tangentsoft.com/pidp8i/doc/trunk/AUTHORS.md
[ori]:    https://tangentsoft.com/pidp8i/doc/trunk/doc/os8-run.md
[pkgtst]: https://tangentsoft.com/pidp8i/doc/trunk/doc/testing.md


#### Baseline

The baseline for the bootable OS/8 media images comes from a set of
DECtapes distributed by Digital Equipment Corporation which are now
included with the PiDP-8/I software; see the [`media/os8/*.tu56`
files][os8mf]. From these files and your configuration options, the
`os8-run` script creates the baseline bootable `v3d-dist.rk05` and
`ock-dist.rk05` disk images.

The default build creates a complete OS/8 V3D system including `BUILD`
support, FORTRAN IV, MACREL v2, and more, but you can switch to an
[OCK build at compile time](#ock) if you prefer.


#### Subtractions

It's pretty easy to run out of space on an OS/8 RK05 disk, not just
because of its [2 × 0.8 MWord limit][rk05td], but also because of an
OS/8 limitation in the number of files on an OS/8 filesystem. We leave
the archive of device drivers and the TD8E subsystem off the system
packs to avoid hitting this second limit. You can add them later from
[OS/8 Binary Distribution DECtape #2][bdt2], such as to create media
for a TD8E based PDP-8/e.

[rk05td]: https://en.wikipedia.org/wiki/RK05#Technical_details


#### Default Additions

The OS/8 RK05 disk image build process normally installs many software
and data file sets to the disk image.  See the option descriptions
above: the ["disable" option set](#disable-os8) effectively lists those
packages that are installed by default, and the following set of
["enable" option set](#enable-os8) lists those left out by default.


#### Console Enhancements

The default build enhances the console in a few ways:

1.  The SIMH PDP-8 simulator and a few select parts of OS/8 are adjusted
    to cope with lowercase input to [varying degrees](#lowercase).

2.  Rubout/backspace handling is set to assume a video terminal rather
    than a teletype by default.

You can read more about this [in the wiki][oce].

[oce]: https://tangentsoft.com/pidp8i/wiki?name=OS/8+Console+TTY+Setup


#### Patches

The `v3d-dist.rk05` disk image referenced above is considered a
read-only master. A copy is made called `v3d.rk05`. This is the
default OS/8 rk05 image assigned to the IF=0 and IF=7 boot options.

In keeping with the standards of good system management, this image
incorporates all mandatory patches, as well as optional patches
appropriate to proper operation of the system. For details on the
available patches, the selection criteria, and information about other
optional patches see the [OS/8 system patches][os8pat] document.

[bdt2]:  https://tangentsoft.com/pidp8i/file/media/os8/al-4712c-ba-os8-v3d-2.1978.tu56
[cl]:    https://tangentsoft.com/pidp8i/doc/trunk/ChangeLog.md
[cs]:    https://tangentsoft.com/pidp8i/doc/trunk/doc/class-simh.md
[os8mf]: https://tangentsoft.com/pidp8i/file/media/os8


### The OS/8 TU56 Tape Image <a id="os8ti"></a>

As with the [OS/8 disk image](#os8di), this distribution's build system
can create custom TU56 tape images from pristine source media.  This
replaces the old `os8.tu56` binary image previously distributed with
this software.

The build system actually creates four such tape images according to a
2×2 matrix of choices:

*   **--boot-tape-version** — The default value is "`v3f`", meaning
    that the boot tape is based on OS/8 V3F. Give "`v3d`" to boot from
    a OS/8 V3D tape instead. See the wiki article [OS/8 V3D vs
    V3F][os8ver] for the implications of this choice.

*   **--boot-tape-config** — The default value is "`tc08`". Give
    "`td12k`" to use a tape image configured with the TD12K DECtape
    controller driver built in. See the wiki article [TC08 vs
    TD12K][os8td] for the reason you're given a choice here.

[os8td]:  https://tangentsoft.com/pidp8i/wiki?name=TD8E+vs+TC08
[os8ver]: https://tangentsoft.com/pidp8i/wiki?name=OS/8+V3D+vs+V3F


## When Something Goes Wrong <a id="troubleshooting"></a>

### Testing Your PiDP-8/I Hardware <a id="testing"></a>

You can test your PiDP-8/I LED and switch functions with these commands:

    $ pidp8i stop
    $ pidp8i-test

You may have to log out and back in before the second command will work,
since the installation script modifies your normal user's `PATH` the
first time you install onto a given system.

It is important to stop the PiDP-8/I simulator before running the test
program, since both programs need exclusive access to the LEDs and
switches on the front panel.  After you are done testing, you can start
the PiDP-8/I simulator back up with:

    $ pidp8i start

See [its documentation][pitest] for more details.


## License

Copyright © 2016-2020 by Warren Young. This document is licensed under
the terms of [the SIMH license][sl].

<div id="this-space-intentionally-left-blank" style="min-height:50em"></div>


[osimg]:  https://tangentsoft.com/pidp8i/doc/trunk/doc/OS-images.md
[cprj]:   https://tangentsoft.com/pidp8i/
[sm2]:    https://groups.google.com/d/msg/pidp-8/-leCRMKqI1Q/Dy5RiELIFAAJ
[oght]:   https://obsolescence.dev/pidp-8-how-to-use.html
[ogk]:    https://obsolescence.dev/pdp8.html
[dt2]:    https://github.com/VentureKing/Deeper-Thought-2
[sdoc]:   https://tangentsoft.com/pidp8i/uv/doc/simh/main.pdf
[pitest]: https://tangentsoft.com/pidp8i/doc/trunk/doc/pidp8i-test.md
[thro]:   https://tangentsoft.com/pidp8i/doc/trunk/README-throttle.md
[mdif]:   https://tangentsoft.com/pidp8i/wiki?name=Major+Differences
[sl]:     https://tangentsoft.com/pidp8i/doc/trunk/SIMH-LICENSE.md
[ils]:    https://tangentsoft.com/pidp8i/wiki?name=Incandescent+Lamp+Simulator
