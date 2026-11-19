#!/bin/sh
# Runtime USB gadget: NCM (ssh) plus ACM (serial). Boot still loads g_serial
# from cmdline; this replaces it. A failed bind restores g_serial.
set -eu
LOG=/var/log/starjar-usb-gadget.log
exec >>"$LOG" 2>&1
echo "start $(date -Is)"

G=/sys/kernel/config/usb_gadget/starjar
finish_net() {
  nmcli device set usb0 managed yes || true
  nmcli connection up starjar-usb || true
  ip addr show dev usb0 | grep -q '169.254.55.1/16' || ip addr add 169.254.55.1/16 dev usb0 || true
  sysctl -w net.ipv4.ip_forward=0 >/dev/null || true
}

if [ -d "$G" ] && [ -s "$G/UDC" ]; then
  echo "already bound"
  finish_net
  exit 0
fi

systemctl stop serial-getty@ttyGS0.service || true
sleep 0.2
if lsmod | grep -q '^g_serial'; then
  if ! modprobe -r g_serial; then
    echo "rmmod g_serial failed"
    systemctl start serial-getty@ttyGS0.service || true
    exit 1
  fi
fi
modprobe libcomposite
modprobe usb_f_ncm
modprobe usb_f_acm

if [ -d "$G" ]; then
  printf '' > "$G/UDC" || true
  find "$G/configs" -type l -delete || true
  rmdir "$G/configs/c.1/strings/0x409" 2>/dev/null || true
  rmdir "$G/configs/c.1" 2>/dev/null || true
  rmdir "$G/functions/ncm.usb0" 2>/dev/null || true
  rmdir "$G/functions/acm.gs0" 2>/dev/null || true
  rmdir "$G/strings/0x409" 2>/dev/null || true
  rmdir "$G" 2>/dev/null || true
fi

mkdir -p "$G/strings/0x409" "$G/functions/ncm.usb0" "$G/functions/acm.gs0" "$G/configs/c.1/strings/0x409"
echo 0x1d6b > "$G/idVendor"
echo 0x0104 > "$G/idProduct"
echo 0x0200 > "$G/bcdUSB"
echo 0x0100 > "$G/bcdDevice"
echo 0xEF > "$G/bDeviceClass"
echo 0x02 > "$G/bDeviceSubClass"
echo 0x01 > "$G/bDeviceProtocol"
printf '%s\n' starjar > "$G/strings/0x409/serialnumber"
printf '%s\n' StarJar > "$G/strings/0x409/manufacturer"
printf '%s\n' 'StarJar USB' > "$G/strings/0x409/product"
echo 250 > "$G/configs/c.1/MaxPower"
echo 0x80 > "$G/configs/c.1/bmAttributes"
printf '%s\n' ncm-acm > "$G/configs/c.1/strings/0x409/configuration"
ln -s "$G/functions/ncm.usb0" "$G/configs/c.1/"
ln -s "$G/functions/acm.gs0" "$G/configs/c.1/"
UDC=$(ls /sys/class/udc | head -n 1)
echo "binding $UDC"
if ! printf '%s' "$UDC" > "$G/UDC"; then
  echo "UDC bind failed, restoring g_serial"
  modprobe g_serial || true
  systemctl start serial-getty@ttyGS0.service || true
  exit 1
fi

i=0
while [ "$i" -lt 20 ]; do
  if ip link show usb0 >/dev/null 2>&1; then
    break
  fi
  i=$((i + 1))
  sleep 0.25
done
finish_net
ip -4 addr show usb0 || true
systemctl reset-failed serial-getty@ttyGS0.service || true
systemctl start serial-getty@ttyGS0.service || true
echo "done $(date -Is)"
