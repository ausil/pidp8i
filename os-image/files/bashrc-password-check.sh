
# Force password change on first interactive login.
# Note: passwd -e is not used here because it causes PAM to block the
# linger-triggered systemd user session at boot, preventing the pidp8i
# simulator from autostarting. See os-image/README.md for details.
if [ -f "$HOME/.password-not-changed" ]; then
    echo "You must change your default password before continuing."
    passwd && rm -f "$HOME/.password-not-changed"
fi
