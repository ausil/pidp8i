# SPDX-License-Identifier: BSD-2-Clause
#
# RPM spec for the PiDP-8/I.
#
# Upstream pidp8i is a single self-contained tree: configure bakes
# $PREFIX (default /opt/pidp8i) into the generated scripts, into
# lib/pidp8i/dirs.py (whose `build`/`media` anchors install-target
# seds at install time), into the boot scripts, into the systemd unit
# templates, and - via @BOOTDIR@ in src/pidp8i/main.c.in - into
# pidp8i-sim itself. This package builds that tree at upstream's own
# prefix (which is how upstream tests it), redirects the one compiled-in
# path at configure time (patch 0004's PIDP8I_BOOTDIR), and then
# RELOCATES everything else in %%install to the FHS locations pidp10
# and pidp11 use:
#
#   /opt/pidp8i/bin          -> /usr/bin
#   /opt/pidp8i/libexec      -> /usr/libexec/pidp8i
#   /opt/pidp8i/lib          -> /usr/share/pidp8i/lib        (pure Python)
#   /opt/pidp8i/share/boot   -> /usr/share/pidp8i/boot
#   /opt/pidp8i/share/include-> /usr/share/pidp8i/include
#   /opt/pidp8i/share/man    -> /usr/share/man
#   /opt/pidp8i/share/media  -> /var/lib/pidp8i/media        (writable)
#   /opt/pidp8i/share/save   -> /var/lib/pidp8i/save         (tmpfiles)
#   /opt/pidp8i/run          -> /var/lib/pidp8i/run          (tmpfiles)
#   /opt/pidp8i/etc/pidp8i.rc-> /etc/pidp8i/pidp8i.rc        (noreplace)
#
# The relocation is a move plus a fixed table of seds over the
# relocated text files (scripts, Python, boot scripts, unit files). It
# is safe because the boot-script directory is the only install path
# any compiled binary embeds. Doing the rest in the spec rather than
# across auto.def/Makefile.in keeps upstream patches to the six small
# ones without which the tree does not build on Fedora 45 at all, so a
# fossil/git re-import only replays those.
#
# Why media is the one payload under /var/lib: the OS/8 runtime RK05
# images are written by the running simulator (the guest creates files
# on its disk), and os8pkg installs packages into them. /usr must be
# read-only for an upgrade to be safe, so media goes to the state tree
# exactly like pidp10's systems directories. It ships root:root with
# group-writable modes and tmpfiles assigns it to the pidp8i service
# account, keeping the service account out of the rpm file metadata.
# Reinstalling media images after corruption: `dnf reinstall pidp8i`
# restores them.
#
# Other design notes:
#
#   * Everything is BUILT from source, including the SIMH PDP-8 engine,
#     the OS/8 tools and the OS/8 disk/tape images themselves: `make`
#     runs the freshly built simulator through lib/os8script.py to
#     assemble bin/*.rk05 and bin/*.tu56 from the OS/8 sources in
#     media/. Nothing is downloaded at build time and no blob tarball
#     is shipped (media/os8/LICENSE.md records DEC's release).
#   * %%install runs `make install-target`, never `install`. Upstream's
#     install-system target does apt-get, systemctl enable-linger,
#     setcap, usermod, and edits to ~/.profile and /boot/cmdline.txt.
#     The RPM takes the equivalent decisions as sysusers/tmpfiles/
#     sudoers fragments and units instead.
#   * No setuid/setcap. Upstream install-system does
#     setcap cap_sys_nice=eip on the simulators; not packaged. A
#     cabinet that needs real-time adds a unit drop-in like pidp10
#     (AmbientCapabilities=CAP_SYS_NICE, LimitRTPRIO=99).
#   * install-target strips (-s) the binaries as shipped; patch 0005
#     drops that -s, so the files reach the buildroot with their
#     -g/-flto debug info and rpmbuild's brp-strip/find-debuginfo split
#     the pidp8i-debuginfo subpackage the normal way.
#   * The service model is upstream's: a *user* unit driven by the
#     bin/pidp8i script (screen/tmux session + NotifyAccess). %%install
#     also corrects the script's `install` subcommand, which bakes in
#     the build user's home for the unit destination, to use $HOME.
#   * rpmlint filters live in packaging/rpmlint.toml, each with its
#     reason there.
#
# Build:
#   packaging/build-rpm.sh                # RPMs from HEAD into ./dist-rpm
#   packaging/build-rpm.sh --srpm-only    # SRPM only (what COPR runs)

%global srcdate 20261120
# Same date, dotted, for the boot banner stamp (Patch0006); keep in
# sync with srcdate above (rpm 6 rejects the old colon substr syntax).
%global srcdatespec 2026.11.20
# The prefix configure bakes in, i.e. the tree %%install relocates from.
%global bldpfx /opt/%{name}
# Where it relocates to.
%global pkgdatadir %{_datadir}/%{name}
%global statedir   %{_sharedstatedir}/%{name}

Name:           pidp8i
Version:        2026.04.15
Release:        1.%{srcdate}%{?dist}
Summary:        PDP-8/I simulator with PiDP-8 front-panel emulation

# The tree mixes licenses (COPYING.md walks through them): the SIMH
# historical notice (SIMH proper, E8, much of the PiDP glue; Fedora tag
# HPND), MIT (the autosetup build system, assorted tools), BSD-2-Clause
# (d8tape, the packaging scripts), and CC-BY-NC-SA-4.0 for
# hardware/pidp8i - design files this package does not install. The
# OS/8 media ships under DEC's permissive source release
# (media/os8/LICENSE.md). FIXME: unreviewed; no per-file license scan
# exists in the tree, so read this as the union of what the sources
# claim.
License:        MIT AND HPND AND BSD-2-Clause
URL:            https://tangentsoft.com/pidp8i
Source0:        %{name}-%{version}-%{srcdate}.tar.gz
Source1:        %{name}.sysusers
Source2:        %{name}.tmpfiles
Source3:        %{name}.sudoers
# Staged by packaging/build-rpm.sh from the same revision as the
# tarball, like the Sources above.
Patch0001:      0001-tools-version-accept-PIDP8I_VERSION-override.patch
Patch0002:      0002-make-pkg_resources-optional.patch
Patch0003:      0003-cc8-cross-build-with-gnu17.patch
Patch0004:      0004-boot-script-path-for-fhs-layout.patch
Patch0005:      0005-no-strip-on-install-for-rpm-debuginfo.patch
Patch0006:      0006-build-banner-no-host-identity.patch

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  make
# autosetup's configure compiles a bootstrap jimsh0 from the bundled
# jimtcl sources when it finds no jimsh/tclsh on PATH - and that
# bootstrap is what wants a C++ compiler. Hand it the system jimsh
# instead: no host shell gets built during packaging, and gcc-c++ is
# not needed anywhere else in the tree.
BuildRequires:  jimtcl
BuildRequires:  tcsh
# configure tests `perl -e exit`; tools/version (banner version) uses
# only core modules, which perl-interpreter/perl-libs provide. The
# perl metapackage is not needed and pulls in the whole core.
BuildRequires:  perl-interpreter
BuildRequires:  python3
# configure imports pexpect and pyyaml (auto.def's module test; patch
# 0002 only dropped pkg_resources from it), and %%check runs os8-run,
# whose import of the private lib pulls pexpect in.
BuildRequires:  python3-pexpect
BuildRequires:  python3-pyyaml
BuildRequires:  ncurses-devel
# configure stamps the build hostname into the OS/8 boot banner
# (catch {exec hostname}); Patch0006 lets the spec override that stamp,
# but the probe itself wants the tool present.
BuildRequires:  hostname
BuildRequires:  systemd-rpm-macros

# os8-run/os8-cp/os8pkg are Python programs that drive the simulator
# through their private modules directory (pexpect, pyyaml).
Requires:       python3
Requires:       python3-pexpect
Requires:       python3-pyyaml
# The pidp8i script runs the console in a screen session by default
# (SCREEN_MANAGER in /etc/pidp8i/pidp8i.rc; tmux is the alternative).
Requires:       screen
# usb-mount@.service
Requires:       systemd
%{?systemd_requires}

%description
A PDP-8 simulator (Open SIMH) with the PiDP-8/I front panel:
blinkenlights and buttons driven over GPIO on a Raspberry Pi, with an
incandescent-lamp simulation for the bulbs. The package builds the
simulator, the PALGAIL/BARTGNO assemblers, the cc8 C compiler, the
DECtape tools, and the OS/8 system itself: the RK05 and TU56 images are
assembled from OS/8 source during the build, none are downloaded.

Without panel hardware everything runs in sim mode (simulated lamps,
no GPIO), so this installs usefully on a plain machine; on a PiDP-8/I
cabinet it is the whole software stack. Binaries are in /usr/bin, the
simulator's data in /usr/share/pidp8i, the writable OS/8 media in
/var/lib/pidp8i/media, and the operator configuration in
/etc/pidp8i.

%prep
# -N: unpack only. The patches are plain `diff -u` outputs (plus
# diff --git headers), and patch(1) without an explicit -p mis-resolves
# them ("No file to patch"), so apply them with the level stated.
%autosetup -n %{name}-%{version}-%{srcdate} -N
%patch -P 0001 -p1
%patch -P 0002 -p1
%patch -P 0003 -p1
%patch -P 0004 -p1
%patch -P 0005 -p1
%patch -P 0006 -p1

%build
%set_build_flags
# tools/version would otherwise ask fossil what this checkout is; the
# tarball has no fossil database, and this is what the built tools print
# in their banners (see Patch0001). PIDP8I_BOOTDIR redirects the
# boot-script directory compiled into pidp8i-sim (Patch0004) to its
# final FHS home; %%install seds the generated scripts to the same
# places.
export PIDP8I_VERSION="%{version}-snap%{srcdate}"
export PIDP8I_BOOTDIR="%{pkgdatadir}/boot"
# The OS/8 boot banner otherwise stamps "built by $USER@$(hostname) at
# $date" (Patch0006): inside a build root that is the builder's
# identity, and nondeterministic. State both from the package instead;
# hostname is also a BR so the unpatched path still works.
export PIDP8I_BUILDUSER="%{name} (Fedora)"
export PIDP8I_BUILDTS="%{srcdatespec}"
# --force-pidp8i: upstream builds the panel binaries (scanswitch,
# pidp8i-test) only when configure sees arm/aarch64 Linux, but the
# package ships them on every arch (without a cabinet they say "No GPIO
# chips found" and exit 1, which %%check accepts). A uniform tree also
# keeps %%files arch-independent and the x86-64 chroot useful.
./configure --prefix=%{bldpfx} --force-pidp8i
%make_build
# rpm auto-copies the %doc entries (doc, examples) from the build tree
# at packaging time, so the build directory configure baked into the
# generated examples/Makefile (cd @abs_top_builddir@; make ...) has to
# be stripped here, not in %%install. Keep the recipe, drop the path.
sed -i -e 's|cd %{_builddir}[^;]*; ||' examples/Makefile

%install
# install-target only - install-system (the default `install`) does
# apt-get, setcap, enable-linger and ~/.profile edits; see the header.
# The explicit util.py build covers the case where configure's
# make-template has not generated it yet.
make lib/pidp8i/util.py
make install-target DESTDIR=%{buildroot}

tree=%{buildroot}%{bldpfx}

# --- relocate the self-contained tree to FHS locations ---------------
mkdir -p %{buildroot}%{_bindir} \
       %{buildroot}%{_libexecdir}/%{name} \
       %{buildroot}%{pkgdatadir}/lib \
       %{buildroot}%{_mandir}/man1 \
       %{buildroot}%{statedir}/media \
       %{buildroot}%{_sysconfdir}/%{name}

mv $tree/bin/*  %{buildroot}%{_bindir}/
# os8-run and os8-cp are generated with the build user's 0775 umask;
# executables should not be group/world-writable.
chmod 0755 %{buildroot}%{_bindir}/os8-run %{buildroot}%{_bindir}/os8-cp
mv $tree/libexec/scanswitch %{buildroot}%{_libexecdir}/%{name}/
mv $tree/lib/*  %{buildroot}%{pkgdatadir}/lib/     # *.py and pidp8i/
# install-target's module list ships __init__, dirs, ips, os8opts,
# os8script, os8util and simh - but not util.py, which os8script.py
# imports at the top (upstream bug: only the os8-run/os8-cp install
# lists name it, and the loop silently skips what it does not list).
# Without this, every installed OS/8 tool dies on `from pidp8i import
# dirs, util`.
install -m 0644 lib/pidp8i/util.py %{buildroot}%{pkgdatadir}/lib/pidp8i/util.py
mv $tree/share/boot    %{buildroot}%{pkgdatadir}/boot
mv $tree/share/include %{buildroot}%{pkgdatadir}/include
mv $tree/share/media/* %{buildroot}%{statedir}/media/
mv $tree/share/man/man1/palbart.1 %{buildroot}%{_mandir}/man1/
# Distro-written pages for the entry points upstream never documented
# (packaging/man/, candidates for upstreaming).
install -m 0644 packaging/man/*.1 %{buildroot}%{_mandir}/man1/
# The tree's etc/ holds nothing after install-target (the rc file and
# unit are install-system's job), so both come from the source build
# dir instead; the whole-tree rm below only has the empty skeleton left.
install -m 0644 etc/pidp8i.rc %{buildroot}%{_sysconfdir}/%{name}/pidp8i.rc
# run/ and share/save are pure state: dropped here, created by tmpfiles.
rm -rf $tree
rmdir -p %{buildroot}%{bldpfx} 2>/dev/null || true

# install-target chowns the tree to whoever ran configure (the build
# user) because upstream wants group-writable media. When %%install runs
# as root - mock, COPR, the supported way - normalize to root so no
# "mockbuild" name reaches the header; otherwise rpmbuild records
# build-user-owned files as root anyway. The %%attr below is what
# actually decides ownership at install time on the target.
if [ "$(id -u)" = 0 ]; then
    chown -R root:root %{buildroot}
fi

# Rewrite the baked-in /opt/pidp8i paths in everything that is text:
# the console/session script, the OS/8 Python drivers, the boot scripts
# (which attach media by absolute path) and the generated units. Order
# matters: specific first, the whole-tree catch-all last. $prefix/...
# rules cover the variables the scripts expand at runtime.
sed_targets=(%{buildroot}%{_bindir}/{pidp8i,os8-run,os8-cp,os8pkg,teco-pi-demo,usb-mount}
             %{buildroot}%{pkgdatadir}/lib/*.py
             %{buildroot}%{pkgdatadir}/lib/pidp8i/*.py
             %{buildroot}%{pkgdatadir}/boot/*.script)
sed -i \
    -e 's|\$prefix/share/media|/var/lib/pidp8i/media|g' \
    -e 's|\$prefix/bin|/usr/bin|g' \
    -e 's|\$prefix/libexec|/usr/libexec/pidp8i|g' \
    -e 's|\$prefix/etc/pidp8i\.rc|/etc/pidp8i/pidp8i.rc|g' \
    -e 's|\$prefix/etc/pidp8i\.service|/usr/lib/systemd/user/pidp8i.service|g' \
    -e 's|unitdir=~[^/]*|unitdir=$HOME|' \
    -e 's|session owned by [^ .]*\.|session owned by you.|' \
    -e '\|%{_builddir}/|d' \
    -e 's|must be done as [^.]*\.|must be done by the invoking user.|' \
    -e 's|%{bldpfx}/share/media|%{statedir}/media|g' \
    -e 's|%{bldpfx}/share/save|%{statedir}/save|g' \
    -e 's|%{bldpfx}/share/boot|%{pkgdatadir}/boot|g' \
    -e 's|%{bldpfx}/share/include|%{pkgdatadir}/include|g' \
    -e 's|%{bldpfx}/share/man|%{_mandir}|g' \
    -e 's|%{bldpfx}/bin|%{_bindir}|g' \
    -e 's|%{bldpfx}/libexec|%{_libexecdir}/%{name}|g' \
    -e 's|%{bldpfx}/lib|%{pkgdatadir}/lib|g' \
    -e 's|%{bldpfx}/run|%{statedir}/run|g' \
    -e 's|%{bldpfx}/obj|%{statedir}/obj|g' \
    -e 's|%{bldpfx}/etc|%{_sysconfdir}/%{name}|g' \
    -e 's|sys\.path\.insert(0, os\.path\.dirname(__file__) + "/\.\./lib")|sys.path.insert(0, "%{pkgdatadir}/lib")|' \
    -e 's|%{bldpfx}|%{pkgdatadir}|g' \
    "${sed_targets[@]}"

# dirs.py anchors are os.path.join(build, ...) so the /opt catch-all
# above cannot reach them: media and obj must name the state tree (the
# simulator writes to the RK05 images; os8pkg stages under obj/), and
# src points at a tree this package does not ship (os8pkg's from-source
# package builder; it fails cleanly without it).
sed -i \
    -e 's|^media = os.path.join (build, "share/media/")|media = "%{statedir}/media/"|' \
    -e 's|^obj = os.path.join(build, "obj/")|obj = "%{statedir}/obj/"|' \
    -e 's|^src   = .*|src   = "%{pkgdatadir}/src/"|' \
    %{buildroot}%{pkgdatadir}/lib/pidp8i/dirs.py

# simh.py spawns the engine and the paper-tape helpers as
# os.path.join(basedir/bdir, "bin", ...), with basedir from dirs.build
# (the data tree). Binaries moved to /usr/bin regardless, so point
# those joins there directly.
sed -i \
    -e 's|os\.path\.join(basedir, "bin", sim)|os.path.join("%{_bindir}", sim)|' \
    -e 's|os\.path\.join(bdir, "bin", "txt2ptp")|os.path.join("%{_bindir}", "txt2ptp")|' \
    -e 's|os\.path\.join(bdir, "bin", "ptp2txt")|os.path.join("%{_bindir}", "ptp2txt")|' \
    %{buildroot}%{pkgdatadir}/lib/simh.py

# Generated units: same rewrite (ExecStart, WorkingDirectory).
install -D -m 0644 etc/pidp8i.service \
    %{buildroot}%{_userunitdir}/%{name}.service
install -D -m 0644 etc/usb-mount@.service \
    %{buildroot}%{_unitdir}/usb-mount@.service
sed -i -e 's|%{bldpfx}/bin|%{_bindir}|g' \
       -e 's|%{bldpfx}/share/media|%{statedir}/media|g' \
       %{buildroot}%{_userunitdir}/%{name}.service \
       %{buildroot}%{_unitdir}/usb-mount@.service

install -D -m 0644 etc/udev.rules \
    %{buildroot}%{_udevrulesdir}/68-usb-mount.rules
install -D -m 0440 %{SOURCE3} %{buildroot}%{_sysconfdir}/sudoers.d/%{name}
install -D -m 0644 %{SOURCE1} %{buildroot}%{_sysusersdir}/%{name}.conf
install -D -m 0644 %{SOURCE2} %{buildroot}%{_tmpfilesdir}/%{name}.conf

find %{buildroot} -name __pycache__ -type d -exec rm -rf {} +

# Docs and licenses: upstream installs none of them, and rpm only
# auto-copies %%doc entries it finds in the buildroot.
install -d -m 0755 %{buildroot}%{_docdir}/%{name}
install -m 0644 README.md ChangeLog.md AUTHORS.md README-throttle.md \
    %{buildroot}%{_docdir}/%{name}/
cp -a doc examples %{buildroot}%{_docdir}/%{name}/
# (the examples/Makefile build-dir stamp is stripped in %%build, where
# rpm's %%doc collection will find it; sed here is too late)
install -d -m 0755 %{buildroot}%{_licensedir}/%{name}
install -m 0644 COPYING.md SIMH-LICENSE.md \
    %{buildroot}%{_licensedir}/%{name}/

# The OS/8 media is the package's writable payload: the simulator
# writes to the runtime RK05 (the guest creates files on its disk) and
# os8pkg installs packages into it. It ships root:root (so rpm metadata
# carries no reference to the service account and rpm emits no bare
# group(pidp8i) provide); the tmpfiles Z line assigns it to
# pidp8i:pidp8i in %%post and on every boot, and the %%defattr below
# carries the group-writable modes.

%check
export TERM=${TERM:-dumb}
# Patch0006 must have taken: the banner that gets assembled into the
# media images carries the stamped values, never the builder's name or
# host (inside a build root that would read "mockbuild@...").
grep -q 'Built from source by %{name} (Fedora) on %{srcdatespec}' media/os8/ock-init.tx
# configure bakes the build directory into the examples Makefile
# (cd @abs_top_builddir@; make ...); the %%build strip must have run.
grep -q 'make \$@' examples/Makefile
! grep -q '%{_builddir}' examples/Makefile
# The plain engine boots and exits. Without panel hardware the engine
# refuses to start: it says "No GPIO chips found" and exits 1, which is
# the expected build-machine result (0 would mean a cabinet is actually
# attached here); anything else, including 124 (timeout), is a failure.
echo q | timeout 60 ./bin/pdp8 >/dev/null
sim_rc=0
echo q | timeout 60 ./bin/pidp8i-sim >/dev/null 2>&1 || sim_rc=$?
if [ "$sim_rc" -gt 1 ]; then
    echo "%check: pidp8i-sim exited $sim_rc" >&2
    exit 1
fi
# The assembler, the paper-tape reader, the OS/8 driver and the panel
# script all run to completion (they are also the point of the package).
./bin/palbart examples/add.pal >/dev/null
./bin/ptp2txt bin/add-pal.pt >/dev/null
./bin/os8-run --help >/dev/null
./bin/pidp8i --help >/dev/null
# The checks above run from the build tree, where the pre-relocation
# paths still line up. These run against the installed layout (via
# buildroot absolute paths) and catch relocation mistakes - a wrong
# sys.path or bin/ anchor fails right here.
export PYTHONPATH=%{buildroot}%{pkgdatadir}/lib
export PYTHONDONTWRITEBYTECODE=1   # the __pycache__ sweep is %install's, already run
python3 -c 'import pidp8i, pidp8i.dirs, pidp8i.util, pidp8i.ips, pidp8i.os8opts, os8script, os8util, simh'
%{buildroot}%{_bindir}/os8-run --help >/dev/null
%{buildroot}%{_bindir}/os8pkg --help >/dev/null

%pre
%sysusers_create_package %{name} %{SOURCE1}

%post
%tmpfiles_create_package %{name} %{SOURCE2}
%systemd_post usb-mount@.service

%preun
%systemd_preun usb-mount@.service

%postun
%systemd_postun_with_restart usb-mount@.service

%files
%license COPYING.md
%license SIMH-LICENSE.md
%doc README.md ChangeLog.md AUTHORS.md README-throttle.md
%doc doc examples
# Engines (pdp8 and txt2ptp are install-target's hard links to
# pidp8i-sim/ptp2txt), assemblers, DECtape tools, generated scripts.
%{_bindir}/pidp8i
%{_bindir}/pidp8i-sim
%{_bindir}/pidp8i-sim-nls
%{_bindir}/pidp8i-sim-ils
%{_bindir}/pidp8i-test
%{_bindir}/pdp8
%{_bindir}/os8-run
%{_bindir}/os8-cp
%{_bindir}/os8pkg
%{_bindir}/palbart
%{_bindir}/d8tape
%{_bindir}/ptp2txt
%{_bindir}/txt2ptp
%{_bindir}/cc8
%{_bindir}/teco-pi-demo
%{_bindir}/usb-mount
%{_libexecdir}/%{name}/scanswitch
# Read-only simulator data. lib/ is the private Python the OS/8 tools
# import (sys.path was rewritten to this location).
%dir %{pkgdatadir}
%{pkgdatadir}/lib
%{pkgdatadir}/boot
%{pkgdatadir}/include
%{_mandir}/man1/*.1*
# The OS/8 media: package data that the running simulator and os8pkg
# write to. It ships root:root with group-writable modes; the tmpfiles
# Z line hands it to pidp8i:pidp8i in %%post and on every boot, so the
# rpm metadata never references the service account (and rpm emits no
# bare group(pidp8i) provide beside the versioned one from sysusers).
# One directory entry owns the whole subtree; defattr's fourth field
# sets the mode for the directories in it, the first for the files. dnf
# reinstall restores the images; tmpfiles re-assigns them.
%defattr(0664,root,root,0775)
%{statedir}/media
%defattr(-,root,root,-)
# State the package does not ship: tmpfiles creates these (as pidp8i)
# and owns them on the target; the modes here are the metadata rpm
# verifies against, with ownership left at root:root for the same
# reason as the media subtree.
%ghost %dir %attr(0755,root,root) %{statedir}
%ghost %dir %attr(0755,root,root) %{statedir}/run
%ghost %dir %attr(0775,root,root) %{statedir}/save
%ghost %dir %attr(0775,root,root) %{statedir}/obj
# Operator files.
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/pidp8i.rc
%config(noreplace) %attr(0440,root,root) %{_sysconfdir}/sudoers.d/%{name}
%{_udevrulesdir}/68-usb-mount.rules
%{_unitdir}/usb-mount@.service
%{_userunitdir}/%{name}.service
%{_sysusersdir}/%{name}.conf
%{_tmpfilesdir}/%{name}.conf

%changelog
* Fri Nov 20 2026 Dennis Gilmore <dennis@ausil.us> - 2026.04.15-1.20261120
- First packaged form: snapshot of the fossil-to-git import (trunk past
  the upstream 2026.04.15 release). Built at upstream's own prefix and
  relocated in %%install to FHS locations: /usr/bin, /usr/libexec/pidp8i,
  /usr/share/pidp8i, /etc/pidp8i, and the writable OS/8 media under
  /var/lib/pidp8i (group pidp8i). sysusers/tmpfiles/sudoers fragments
  for the service account.
- Six patches: four build fixes for the Fedora 45 environment
  (PIDP8I_VERSION override so configure does not require fossil,
  optional pkg_resources (removed in setuptools 83; simh.py falls back
  to importlib.metadata), -std=gnu17 for the K&R cc8 cross-compiler,
  and a PIDP8I_BOOTDIR override for the boot-script directory compiled
  into pidp8i-sim) plus two packaging-policy ones (no install -s so
  find-debuginfo can split debuginfo, and PIDP8I_BUILDUSER/BUILDTS
  overrides so the OS/8 boot banner carries no build-host identity).
- Only `make install-target` runs: upstream's install target does
  apt-get, setcap, enable-linger and ~/.profile edits, none of which a
  package may do.
