# PiDP-8/I Software Release Process

This documents the process for producing release versions of the
software.


## *Can* You Release Yet?

Before release, you must:

*   Fix all Immediate, High, and Medium priority [Bugs](/bugs)
*   Implement all Immediate and High priority [Features](/features)

Or reclassify them, of course.

Most of the bug levels simply aid scheduling: Immediate priority bugs
should be fixed before High, etc. Low priority bugs are “someone should
fix this someday” type of problems; these are the only ones allowed to
move from release to release. Think of bugs at this level as analogous
to the `BUGS` section of a Unix man page: our “low” intent to fix these
problems means they may stay at this level indefinitely, acting only as
advisories to the software’s users.

The Features levels may be read as:

*   **Immediate**: ASAP, or sooner. :)
*   **High**: Features for the upcoming release.
*   **Medium**: Features we’ll look at lifting to High for the release
    after that.
*   **Low**: “Wouldn’t it be nice if...”


## Update SIMH

If `tools/simh-update` hasn’t been run recently, you might want to do
that and re-test before publishing a new version.


## Test

1.  Build the software on the version of Raspberry Pi OS we’ll use for
    the binary OS image, [below](#image). Fix any problems.

2.  Run `make test` on the build host. Fix any problems.

3.  Repeat above on [all other platforms previously known to work][oscomp].
    Update the article to list caveats and such, or fix the problems.

(See “[How the PiDP-8/i Software Is Tested](./testing.md)” for details
on the philosophy and methods behind this process.)

[oscomp]: https://tangentsoft.com/pidp8i/wiki?name=OS+Compatibility


## Publish OS/8 RK05s

Re-configure the software with default settings, remove `bin/*.rk05`,
rebuild, and run `tools/publish-os8` to send the “final” OS/8 disk
images for this version of the software up to tangentsoft.com as
unversioned assets.

Update the date stamp in the “OS/8 RK05 Media” section of the project
home page.


## Update ChangeLog.md

Trawl the Fossil timeline for user-visible changes since the last
release, and write them up in user-focused form into [the `ChangeLog.md`
file][cl]. If a regular user of the software cannot see a given change,
it shouldn’t go in the `ChangeLog.md`; let it be documented via the
timeline only.

Immediately prior to release, `/doc`, `/dir`, `/file` and similar links
should point to trunk, but immediately prior to release, re-point them
to the `release` branch, since this document describes prior releases.

[cl]: https://tangentsoft.com/pidp8i/doc/trunk/ChangeLog.md


## One-Time Setup: Release Branch Checkout

Before running `make release` for the first time, you must create a
sibling checkout of the `release` branch next to your `trunk` directory.
Following the checkout conventions in [CONTRIBUTING.md][ctrb], 
the commands to do this, run from the parent directory of `trunk`,
are:

    $ mkdir release
    $ cd release
    $ fossil open ~/museum/pidp8i.fossil
    $ ./configure
    $ fossil up release

(If your development build uses a non-standard configuration you will need
to add the options to the above `./configure` command.)

`./configure` is run before `fossil up release` because the release
branch may contain source files incompatible with the current tool
chain, preventing a successful configure. The resulting `Makefile`
should be sufficient to bootstrap the self-regenerating build system
when `make release` runs.

[ctrb]: https://tangentsoft.com/pidp8i/doc/trunk/CONTRIBUTING.md


## Update the Release Branch

Run `make release` to check the `ChangeLog.md` file changes in, merge
trunk to the `release` branch, and apply a tag of the form vYYYYMMDD to
that merge checkin.

It runs entirely automatically unless an error occurs, in which case it
stops immediately, so check its output for errors before continuing.

If `make release` fails partway through, run `make clean` in the
`release` directory before retrying. If the failure occurred during
the merge step in `mkrel`, also run `fossil undo` in the `release`
directory to roll back the incomplete merge. Then retry `make release`
from the `trunk` directory.

If the situation is more badly corrupted — for example after multiple
failed attempts have left false merge records in the release branch —
find the last legitimate release branch commit using:

    $ cd ../release
    $ fossil timeline -b release -n 20

Then force a fresh merge from that point using the `--baseline` flag,
which overrides Fossil's normal ancestor detection:

    $ fossil merge --baseline HASH trunk   # HASH from timeline output above
    $ fossil changes --conflict

If there are no conflicts, commit the merge manually:

    $ fossil ci -m "Manual merge of trunk into release to clean up failed mkrel attempt"

Note that during `fossil ci` you may see a warning about binary files.
Type `a` to commit all. Also note that you must be at the branch tip
before committing — if you see "Would fork", run `fossil up` to the
current tip first.

Then retry `make release` from the `trunk` directory.

## Update the Home Page Links

The zip and tarball links on the front page produce files named after
the date of the release. Those dates need to be updated immediately
after tagging the release, since they point at the “release” tag applied
by the previous step, so they begin shipping the new release immediately
after tagging it.


## <a id="image"></a>Produce the Binary OS Image

The binary OS image is built using [rpi-image-gen][rig] on a Raspberry
Pi 5 build host running the latest version of the Raspberry Pi OS.  This
replaces the [legacy `bosi` scheme](#legacy).

See the new [process docs][rig] for details.

[rig]: ../os-image/README.md


### Test the Image

1.  Flash the image to a microSD card and boot it on a suitable target.
2.  [Edit the WiFi config][wifi] before first boot.
3.  On first boot the system will reboot automatically after installing
    the simulator service. After the second boot, the front panel lights
    should begin blinking.
4.  Verify SSH works: `ssh pidp8i@pidp8i.local`, implicitly testing the
    applied local WiFi configuration.
5.  Verify password change is forced on first login.
6.  Run `pidp8i` and confirm OS/8 is running.

[wifi]: ./OS-images.md#wifi

### Package the Release

Once testing is complete, create the release zip on the Mac:

    $ cd ~/rpi-image-gen/work/deploy-<date>/
    $ RELEASE=pidp8i-YYYY.MM.DD
    $ mkdir $RELEASE
    $ cp pidp8i-trixie.img $RELEASE/$RELEASE.img
    $ cp ~/trunk/doc/OS-images.md $RELEASE/README.md
    $ sha256sum $RELEASE/$RELEASE.img > $RELEASE/MANIFEST.txt
    $ zip -r $RELEASE.zip $RELEASE/
    $ scp $RELEASE.zip tangentsoft.com:dl/

Update the download links and image size on the project home page.


## <a id="legacy"></a>ARMv6 Images

The legacy [`bosi`](../tools/bosi) tool can
produce images for the 32-bit ARMv6 Pi boards (BCM2835), including the
original Raspberry Pi, the Pi 2, and the Pi Zero. This
platform is no longer supported by `rpi-image-gen`. The last images
produced this way were based on Raspberry Pi OS Buster (v10) Lite.

See the legacy build instructions in the `bosi` script itself for
the full procedure.


## Publicizing

While the image uploads, compose the announcement message and modify the
front page to point to the new image. Update the approximate image size
reported on that page. Post the announcement message and new front page
once the upload completes.


----------------------

### License

Copyright © 2016-2026 by Warren Young, Bill Cattey. This document is
licensed under the terms of [the SIMH license][sl].

[sl]: https://tangentsoft.com/pidp8i/doc/trunk/SIMH-LICENSE.md
[rig]: https://github.com/raspberrypi/rpi-image-gen
