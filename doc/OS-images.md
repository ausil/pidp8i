# Using Our Binary OS Images

## Imaging the SD Card

The PiDP-8/I OS images available for download from the [PiDP-8/I
development site](/) are built on Debian Trixie (Debian 13) for 64-bit
ARMv8 hosts.  You will need a **4 GB or larger** microSD card.

We recommend using [Raspberry Pi Imager][RPI] to flash the image, as it
can decompress our `.xz.img` files on the fly, saving you from
ballooning our quarter-gig compressed distribution file into the
four-gig sparse form needed on the card.  [Etcher] also knows this
trick.  Other schemes involving the likes of `dd` can also work, but
you’re on your own there.

After downloading and unzipping the image file, open Raspberry Pi
Imager, click "Choose OS", scroll to the bottom of the list and select
"Use custom", then select the `pidp8i-*.img` file. Select your SD card
and click "Write".

The download contains:

| File Name | Description |
|---|---|
| `README.md` | this file |
| `pidp8i-*.img` | the OS image, based on Debian Trixie Lite |
| `MANIFEST.txt` | SHA-256 hash and file size for the OS image file |

[Etcher]: https://balena-io.github.io/etcher/
[RPI]:    https://www.raspberrypi.com/software/

## enable\_ssh

To prevent your PiDP-8/i from becoming a launchpad for botnets, we ship
the image with the SSH service disabled.  The risk otherwise is that
anyone who flashed a card, booted it up on a network, and then never
logged in via the console or SSH would never get the prompt to change
this well-known password, making takeover trivial.

We make it really easy to turn SSH service on if you want it.

After flashing the SD card, its boot partition might appear as a small
drive on your Mac, Windows, or Linux machine.  (If not, it is because
the writing program ejected the card.  Pull the card out and slip it
back in to force a remount.)

Create a file named `enable_ssh` there.  For instance, on a Mac:

```
touch /Volumes/BOOT/enable_ssh
```

The OS images we ship include a boot-time service that enables SSH
service when that file is present, overriding the default-disabled
security stance.  This allows you to change your mind afterward:

```
sudo rm /boot/firmware/enable_ssh
```

Reboot, and SSH will be down.


## <a id="wifi"></a>WiFi Setup (Optional)

If you intend to run your PiDP-8/I headless over WiFi, you can
pre-configure your network credentials before first boot.  On the same
`BOOT` partition as in the `enable_ssh` scheme above, you will find a
file named `wpa_supplicant-wlan0.conf`.  Open it in a text editor and
fill in your network name and password:

```
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US

network={
    ssid="YourNetworkName"
    psk="YourPassword"
    key_mgmt=WPA-PSK
}
```

Be sure to change `country=` to your [two-letter country code][ISOcc] if
you are not in the US.  Not only might your clients fail to connect,
your Pi might violate the local radio regulations.

Save the file, eject the SD card, and insert it into your Pi.  On first
boot, the WiFi credentials will be installed automatically.

Note that the Raspberry Pi 3B and Pi Zero 2 W support **2.4 GHz WiFi
only**.  If your router broadcasts separate 2.4 GHz and 5 GHz networks,
make sure you use the proper SSID.  These are often distinguished by a
`_2G` or `_2.4G` suffix, or conversely a `_5G` suffix on the faster
network.

If you prefer to configure WiFi after first boot, connect via Ethernet,
then run:

```
$ sudo raspi-config
```

Select "System Options" → "Wireless LAN" and follow the prompts.

[ISOcc]: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2


## First Boot

Insert the SD card into your Pi and apply power. **The first boot takes longer
than usual** — the PiDP-8/I service is being installed and the system will reboot
automatically once complete. After the reboot, the front panel lights will begin
blinking, indicating the simulator is running.


## Logging In

The default login credentials are:

- **username:** `pidp8i`
- **password:** `edsonDeCastro1968!`

You will be required to change the password on first login.  Remember,
[the S in IoT stands for Security][SIoT].  Those who wish to cast away
this secure-by-default stance should see our [How to Run a Naked
PiDP-8/I][naked] guide.

You can log in directly with a keyboard and monitor, or via SSH once the Pi is
on your network:

```
$ ssh pidp8i@pidp8i.local
```

[naked]: /wiki?name=How+to+Run+a+Naked+PiDP-8/I
[SIoT]:  https://www.theregister.com/2024/03/09/opinion_column_security_sjvn/


## Using the Simulator

The PiDP-8/I simulator starts automatically at boot. To connect to its console:

```
$ pidp8i
```

You will find yourself at the OS/8 prompt. To detach from the console and return
to the Linux shell without stopping the simulator, type `Ctrl-A d`. To stop and
restart the simulator:

```
$ pidp8i stop
$ pidp8i start
```

To test the front panel hardware (do this only after stopping the simulator first):

```
$ pidp8i stop
$ pidp8i-test
```
