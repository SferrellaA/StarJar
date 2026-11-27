#!/bin/sh
# Install the tree in /opt/starjar and enable the boot service. Not cron.
# Usage, on the jar, as root: deploy/install.sh /tmp/starjar-build
set -eu

src=${1:-/tmp/starjar-build}
if [ ! -d "$src/starjar" ] || [ ! -d "$src/www" ] || [ ! -d "$src/challenge_tree" ]; then
  echo "install source is incomplete" >&2
  exit 1
fi

install -d -o star -g star -m 0755 /opt/starjar
rm -rf /opt/starjar/starjar /opt/starjar/www /opt/starjar/challenge_tree
cp -a "$src/starjar" "$src/www" "$src/challenge_tree" /opt/starjar/
cp -a "$src/trivia.example.toml" "$src/config.example.toml" /opt/starjar/
chown -R star:star /opt/starjar

install -d -o root -g star -m 0755 /etc/starjar
if [ ! -f /etc/starjar/config.toml ]; then
  cat > /etc/starjar/config.toml <<'EOF'
# Installed by scripts/starjar-build. Not an attempt secret.

[leds]
count = 50
pin = 18
order = "RGB"

[paths]
attempt = "/run/starjar"
trivia = "/var/lib/starjar/trivia.toml"
scoreboard = "/var/lib/starjar/scoreboard.json"
challenge_tree = "/opt/starjar/challenge_tree"
www = "/opt/starjar/www"

[web]
host = "0.0.0.0"
port = 8080
EOF
  chown root:star /etc/starjar/config.toml
  chmod 0644 /etc/starjar/config.toml
fi

install -d -o star -g star -m 0750 /var/lib/starjar /run/starjar
chown star:star /var/lib/starjar /run/starjar
chmod 0750 /var/lib/starjar /run/starjar
if [ ! -f /var/lib/starjar/trivia.toml ]; then
  cp /opt/starjar/trivia.example.toml /var/lib/starjar/trivia.toml
  chown star:star /var/lib/starjar/trivia.toml
  chmod 0640 /var/lib/starjar/trivia.toml
fi

install -d -o star -g star -m 0750 /run/starjar
install -m 0644 "$src/deploy/starjar.service" /etc/systemd/system/starjar.service
install -m 0644 "$src/deploy/starjar-leds.service" /etc/systemd/system/starjar-leds.service
install -m 0644 "$src/deploy/starjar.tmpfiles" /etc/tmpfiles.d/starjar.conf
systemd-tmpfiles --create /etc/tmpfiles.d/starjar.conf

cat > /usr/local/bin/jump <<'EOF'
#!/bin/sh
export PYTHONPATH=/opt/starjar
exec /usr/bin/python3 -m starjar.jump "$@"
EOF
chmod 0755 /usr/local/bin/jump
cat > /usr/local/sbin/starjar-radio <<'EOF'
#!/bin/sh
export PYTHONPATH=/opt/starjar
exec /usr/bin/python3 -m starjar.radio_main "$@"
EOF
chmod 0755 /usr/local/sbin/starjar-radio

# Boot is the systemd unit. Drop a leftover cron line if one was added by hand.
if crontab -u star -l >/tmp/starjar-cron 2>/dev/null; then
  if grep -q starjar /tmp/starjar-cron; then
    grep -v starjar /tmp/starjar-cron > /tmp/starjar-cron.new || true
    crontab -u star /tmp/starjar-cron.new || true
  fi
fi
rm -f /tmp/starjar-cron /tmp/starjar-cron.new /etc/cron.d/starjar

systemctl daemon-reload
systemctl enable starjar-leds.service starjar.service
systemctl restart starjar-leds.service
systemctl restart starjar.service
sleep 1
systemctl is-active --quiet starjar.service
systemctl is-active --quiet starjar-leds.service
echo "starjar.service enabled; it starts on boot"
rm -rf "$src"
