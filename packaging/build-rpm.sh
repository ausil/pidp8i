#!/usr/bin/bash
# SPDX-License-Identifier: BSD-2-Clause
#
# build-rpm.sh - build the RPMs from this tree.
#
#   packaging/build-rpm.sh [topdir]                    default topdir: ./dist-rpm
#   packaging/build-rpm.sh --worktree [topdir]         package the work tree
#   packaging/build-rpm.sh --srpm-only [topdir]        just the SRPM (for COPR)
#
# Same contract as pidp10's packaging/build-rpm.sh, kept line-for-line
# compatible where it can be: by default the source tarball is
# `git archive` of HEAD, so what ships is what is committed - the only
# version of the project reproducible from the repository alone. A dirty
# work tree is warned about, not silently packaged; --worktree says out
# loud that you want the uncommitted version, for testing before a
# commit and for nothing else.
#
# The spec, the three patches and the sysusers/tmpfiles/sudoers
# fragments are staged from the SAME revision as the tarball. Reading a
# work-tree spec against a HEAD tarball is how an uncommitted %files
# list meets an %install that puts things somewhere else.
#
# Source0 is the whole tree. Nothing prebuilt is packaged: SIMH, the
# panel drivers and even the OS/8 disk images are built by `make` (the
# images are assembled from OS/8 sources during the build), so there is
# no blob tarball, no second Source and no --with switch to opt into
# shipping someone's ELF.

set -euo pipefail

here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/.." && pwd)
cd "$root"

worktree=0
srpm_only=0
while [ "${1:-}" = "--worktree" ] || [ "${1:-}" = "--srpm-only" ]; do
	case "$1" in
	    --worktree)  worktree=1 ;;
	    --srpm-only) srpm_only=1 ;;
	esac
	shift
done
top=$(realpath -m "${1:-dist-rpm}")
dist=${DIST_DIR:-$root/dist}
mkdir -p "$top" "$dist"

# stage REPO-PATH DEST: copy a packaging input into _sourcedir from the
# same revision as the tarball - HEAD by default, the work tree with
# --worktree.
stage()
{
	if [ "$worktree" = 1 ]; then
		cp "$1" "$2"
	else
		git show "HEAD:$1" > "$2"
	fi
}
spec=$dist/pidp8i.spec
stage packaging/pidp8i.spec "$spec"
stage packaging/pidp8i.sysusers "$dist/pidp8i.sysusers"
stage packaging/pidp8i.tmpfiles "$dist/pidp8i.tmpfiles"
stage packaging/pidp8i.sudoers  "$dist/pidp8i.sudoers"
stage packaging/pidp8i.rules    "$dist/pidp8i.rules"
for p in packaging/patches/*.patch; do
	stage "$p" "$dist/$(basename "$p")"
done

name=pidp8i

if [ "$worktree" = 1 ]; then
	echo "build-rpm: packaging the WORK TREE (uncommitted changes included;"
	echo "build-rpm: nobody but you can rebuild this)" >&2
elif [ -n "$(git status --porcelain)" ]; then
	echo "build-rpm: WARNING: work tree is dirty; HEAD is being packaged and" >&2
	echo "build-rpm: your uncommitted work is NOT in it. --worktree to include it." >&2
	git status --short | head -20 >&2
fi

# make_tarball DEST PREFIX PATHSPEC...
#   The archive PREFIX is the directory %autosetup -n unpacks, so it is
#   taken apart from the tarball name rather than guessed (pidp10's
#   name-$version rule does not fit a project whose version carries
#   dots-and-dashes; the tarball name itself is the truth here).
make_tarball()
{
	local dest=$1 prefix=$2; shift 2

	if [ "$worktree" = 1 ]; then
		# git ls-files keeps .gitignore in force, so obj/, the
		# generated bin/ products and the scratch build dirs stay
		# out the same way they do for git. A tracked file deleted
		# in the work tree is still --cached; leave it out rather
		# than have tar fail on it. (tar has no --prefix;
		# --transform with the S flag rewrites file names *and*
		# symlink targets.)
		git ls-files -z --cached --others --exclude-standard -- "$@" |
		    while IFS= read -r -d '' f; do
			    { [ -e "$f" ] || [ -L "$f" ]; } && printf '%s\0' "$f"
		    done |
		    tar --format=gnu --null ${prefix:+--transform="s|^|$prefix/|S"} -cf - -T - |
		    gzip > "$dest"
	else
		git archive --format=tar ${prefix:+--prefix="$prefix/"} HEAD -- "$@" |
		    gzip > "$dest"
	fi
}

# Two directories: the sources go to dist/ (the _sourcedir), the
# products land flat in $top. No _topdir is set, so no SOURCES/BUILD/
# BUILDROOT tree appears in either - the rpmbuild scratch stays in
# ~/rpmbuild, where it belongs. _rpmfilename keeps the arch out of the
# path; the %% are load-bearing (see pidp10's copy of this script for
# why NAME has to be deferred to packaging time).
#
# Source0's name is read from the spec with rpmspec -P (with _sourcedir
# already holding the staged Sources) rather than invented here, so the
# two cannot drift and a bare rpmbuild -ba wants exactly what
# make_tarball produces.
tarball=$(rpmspec -P --define "_sourcedir $dist" "$spec" |
          sed -n 's/^Source0:[[:space:]]*//p' | head -1)
[ -n "$tarball" ] || { echo "build-rpm: cannot read Source0 from the spec" >&2; exit 1; }
make_tarball "$dist/$tarball" "${tarball%.tar.gz}" .

rpmbuild -b$([ "$srpm_only" = 1 ] && echo s || echo a) \
    --define "_sourcedir $dist" \
    --define "_rpmdir $top" --define "_srcrpmdir $top" \
    --define "_rpmfilename %%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm" \
    "$spec"

if [ "$srpm_only" = 1 ]; then
	ls -1 "$top"/*.src.rpm
else
	echo "RPMs: $top"
fi
