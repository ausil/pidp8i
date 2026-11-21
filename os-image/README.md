# os-image

This directory contains the PiDP-8/I specific configuration for
[`rpi-image-gen`][RIG], the Raspberry Pi Foundation's modern image
generation tool, plus a few layered-on files for same to ensure that the
OS boots with a suitable starting configuration.  This lets us build the
PiDP-8/I OS images on a suitably powerful Raspberry Pi without the need
for manual SD card manipulation, as was required by the legacy `bosi`
tool, which was last used to build images based on Raspberry Pi OS
Buster Lite, long since obsolete.

[RIG]: https://github.com/raspberrypi/rpi-image-gen


## Concept Map

The `bosi` stages map to rpi-image-gen concepts as follows:

| bosi stage                        | rpi-image-gen equivalent               |
|-----------------------------------|----------------------------------------|
| `do_init` (package install)       | `mmdebstrap: packages:` in layer YAML  |
| `do_build` (fossil clone + build) | `customize-hooks:` in layer YAML       |
| `do_prepare` (sanitize)           | handled automatically by rpi-image-gen |
| `do_image` (capture SD card)      | `rpi-image-gen build` output           |

## Hardware Support

The original `bosi` tool worked on any Raspberry Pi that could run the
PiDP-8/I I/O board itself.  Because [`rpi-image-gen`][RIG] does not
support ARMv6, the minimum supported target is now the **Pi Zero 2 W**
(BCM2710, ARMv8 quad-core Cortex-A53). This also retires the NLS (No
Lamp Simulator) image variant, since the Zero 2 W is fast enough to run
the ILS.  This aligns with developer priorities, who want a sufficiently
fast build host that the OS/8 RK05 disk images are not painful to
rebuild.

Supported targets:

| Target      | Device layer override           |
|-------------|---------------------------------|
| Pi Zero 2 W | `IGconf_device_layer=rpizero2w` |
| Pi 3        | `IGconf_device_layer=rpi3`      |
| Pi 4        | `IGconf_device_layer=rpi4`      |
| Pi 5        | `IGconf_device_layer=rpi5`      |

The default device layer is `rpi-generic64-device`, a thin wrapper
around `rpi-generic64` that declares the `device` provider capability
per the recommended [`rpi-image-gen`][RIG] pattern. See
`layer/rpi-generic64-device.yaml` and upstream [issue #202][I202].

[I202]: https://github.com/raspberrypi/rpi-image-gen/issues/202

## Project Structure

```
os-image/
├── README.md                            this file
├── config/
│   └── pidp8i-trixie.yaml               main build config (Debian Trixie, arm64)
├── files/
│   ├── bashrc-password-check.sh         Force password change on first interactive login.
│   ├── pidp8i-firstboot-system.service  Configures wifi if wpa_supplicant-wlan0.conf present.
│   ├── pidp8i-firstboot-user .service   runs 'pidp8i install' on first boot, then reboots
│   └── wpa_supplicant-wlan0.conf        WiFi credentials template — copy to the
│                                        boot partition and fill in before first boot
└── layer/
    ├── pidp8i-common.yaml.in           main layer: packages, build, install, config
    |                                   processed by auto.def to pick current branch.
    └── rpi-generic64-device.yaml    device provider wrapper for rpi-generic64
```

### Prerequisites

*   A qualifying Raspberry Pi to use as a build host.  The recommended
    path is a Pi 4 or 5 running a 64-bit version of Raspberry Pi OS 12
    or higher.  The hardware can be as old as a Pi 2 or a Pi Zero 2 W,
    though this will make the build time painfully long.  This will not
    work on a 32-bit OS.

    Alternatively, `rpi-image-gen` supports QEMU and containerized
    builds, though these are not formally tested for PiDP-8/I images.

*   A clone of `rpi-image-gen`:

        $ cd ~
        $ git clone https://github.com/raspberrypi/rpi-image-gen

*   A clone of this project:

        $ cd ~
        $ sudo apt install fossil
        $ fossil clone https://tangentsoft.com/pidp8i

    Refinements on this are in our [contribution doc][sco].

*   Required packages installed on the build host:

        $ cd ~/rpi-image-gen
        $ sudo ./install_deps.sh ~/pidp8i/os-image/depends

is restricted to 64-bit ARM targets.  It is therefore known
to work with the latest Pi 5 down to the Pi Zero 2 W.

[sco]: ../CONTRIBUTING.md#sep-clone-open


## Building

On the Pi 4+ build host:

```bash
cd ~/rpi-image-gen
sudo ./rpi-image-gen build -c pidp8i-trixie.yaml \
    -S ~/pidp8i/os-image
```

To target a specific device:

```bash
sudo ./rpi-image-gen build \
  -S ~/pidp8i/os-image \
  -c pidp8i-trixie.yaml \
  -- IGconf_device_layer=rpizero2w
```

The output image is written to `~/rpi-image-gen/work/deploy-<date>/`.

If `/tmp` on your build box is a `tmpfs`, you may run out of scratch
space. You can fix it like so:

```bash
sudo mkdir -m 1777 /media/usb/tmp
sudo TMPDIR=/media/usb/tmp ./rpi-image-gen build …
```

When iterating on that build process, you may prefer to maintain a
parallel clone of the above on a more powerful development system,
then sync it up to the Pi to test before committing a change:

```bash
fossil patch push pi5:pidp8i
```

## Deploying

On the software deployment host:

```bash
r=$(date +%F)
s=pidp8i-trixie.img.zst
d=$(echo $s | sed -e s/-/-${r}-/ -e s/zst/xz/)
cd ~/src/tangentsoft.com/trunk
ssh pi5 "cat rpi-image-gen/work/deploy-${r}/${s}" | zstd -d | xz -9 > dl/${d}
make synch
```

## Notable Implementation Details

**User service installation:** `pidp8i install` requires a live systemd user session
bus and cannot run in the chroot. It is deferred to a one-shot systemd user service
(`pidp8i-firstboot.service`) that runs on first boot, installs the simulator service,
and reboots. From the second boot onwards the simulator starts automatically.

**GPIO permissions:** The `pdp8` binary accesses `/dev/gpiomem` directly with no
library dependencies. A udev rule sets `GROUP=gpio MODE=0660` on the device node.
The `pidp8i` user is added to the `gpio` group by the `rpi-user-credentials` layer.

**linger:** `loginctl enable-linger` cannot run in the chroot. The linger file is
created directly at `/var/lib/systemd/linger/pidp8i`.

**Password change on first login:** We use a sentinel file
(`~/.password-not-changed`) checked by `.bashrc` rather than `passwd -e`
to force a password change on first interactive login. The reason is that
`passwd -e` causes PAM to block the linger-triggered systemd user session
at boot, preventing the simulator from autostarting without any login.
Since `.bashrc` only runs for interactive shells, the sentinel file
approach is invisible to systemd and leaves linger unaffected.

**PATH:** The Makefile's PATH update uses `$SUDO_USER` which is unset in the chroot.
The layer adds `/opt/pidp8i/bin` and `/opt/pidp8i/share/man` to the pidp8i user's
`.profile` directly.

**WiFi:** The image ships with a `wpa_supplicant-wlan0.conf` template on the boot
partition (FAT32, visible on any OS). The user fills in their SSID and password before
first boot. The firstboot service moves it to `/etc/wpa_supplicant/` on first boot.
Alternatively, `sudo raspi-config` → System Options → Wireless LAN can be used after
connecting via ethernet.
