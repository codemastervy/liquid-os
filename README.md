# Liquid OS

Liquid OS is a full desktop Linux distro built on Ubuntu 24.04 LTS, wrapped in
a glassmorphism "liquid glass" GNOME desktop: translucent windows and panels,
real-time background blur behind the top bar and overview, and a soft,
colorful, procedurally generated wallpaper that carries through into the boot
screen and GRUB menu. It's a real, installable OS — full `ubuntu-desktop`
plus Ubuntu's actual graphical installer — not a stripped-down demo.

## Screenshots

<!-- LIQUID_OS_SCREENSHOTS_START -->
_No screenshots yet — run the workflow (see below) to generate them. (The
previous set was captured against a build that didn't boot correctly; the
next successful run will replace this placeholder with real ones.)_
<!-- LIQUID_OS_SCREENSHOTS_END -->

## The look

Liquid OS starts from stock Ubuntu and reworks the desktop into a frosted,
translucent look:

- **Yaru-Liquid**, a translucent variant of Ubuntu's own Yaru theme — windows,
  headerbars, popovers, and buttons get soft rgba backgrounds, rounded
  corners, and subtle highlight borders instead of flat opaque panels.
- **Real live blur**, via the [Blur My Shell](https://github.com/aunetx/blur-my-shell)
  GNOME Shell extension, enabled by default — the top bar, overview, and dash
  blur whatever's behind them in real time, not just a tinted overlay.
- **A liquid-glass wallpaper**, painted procedurally (soft blurred color
  blobs over a deep gradient) rather than a static image, so it's regenerated
  fresh on every build. The same artwork carries over into the GRUB
  background and the Plymouth boot splash, so the look is consistent from
  power-on to desktop.

## What's inside

- Ubuntu 24.04 LTS (noble) as the base — full `ubuntu-desktop`, not a minimal
  spin, so LibreOffice, Firefox, and the usual GNOME app set are there from
  first boot.
- Ubuntu's real installer (`ubiquity`) with an "Install Liquid OS" desktop
  icon — partitioning, locale, user account, the works. This is a live image
  you can install to a disk, not just a demo you boot and discard.
- The Liquid Glass theme, wallpaper, and extension set up as the defaults out
  of the box — no manual setup after install.

## Get it

Liquid OS is built by a GitHub Actions workflow in this repo (see
[`.github/workflows/build-iso.yml`](.github/workflows/build-iso.yml)) — no
local build environment needed on your end.

- **Download a release:** check this repo's
  [Releases](https://github.com/codemastervy/liquid-os/releases) for a
  ready-made ISO.
- **Build it yourself:** go to **Actions → Build Liquid OS ISO → Run
  workflow**, wait for it to finish (a full desktop build typically takes
  15–30 minutes), then grab the `liquid-os-iso` artifact from that run.

## Try it

- **Live session:** boot the ISO as-is (USB stick via `dd`, Balena Etcher, or
  Rufus, or in a VM — UTM, VirtualBox, VMware, or
  `qemu-system-x86_64 -m 4096 -cdrom Liquid-OS-*.iso -enable-kvm`, dropping
  `-enable-kvm` off Linux) to try the desktop without touching your disk.
- **Install it for real:** the live desktop has an "Install Liquid OS" icon
  that launches `ubiquity`, Ubuntu's normal graphical installer.

## Repo layout

```
.github/workflows/build-iso.yml   CI pipeline:
                                     build      -> installs live-build,
                                                   generates the wallpaper,
                                                   merges the overlay below
                                                   into a live-build config,
                                                   runs `lb build`.
                                     screenshot -> boots the resulting ISO in
                                                   QEMU/KVM, captures frames,
                                                   and commits them into
                                                   docs/screenshots/ + this
                                                   README.
scripts/generate-wallpaper.py     Procedural liquid-glass wallpaper generator.
livebuild-overlay/
  package-lists/                  Packages installed via apt during the
                                   build: full ubuntu-desktop, the ubiquity
                                   installer stack, GNOME extensions/tweaks.
  includes.chroot/                Files copied verbatim onto the live
                                   filesystem (branding, dconf defaults, grub
                                   background config, install-desktop
                                   shortcut, wallpaper output).
  hooks/                          Scripts run inside the chroot after package
                                   installation: theme build, extension
                                   install, Plymouth/initramfs update, dconf
                                   compile.
docs/screenshots/                 Auto-captured desktop screenshots (written
                                   by CI, not hand-curated).
```

## Notes / known limitations

- The ISO currently boots BIOS/legacy (isolinux) only — no UEFI boot yet.
  Most VMs (including the QEMU setup above and the screenshot job's own
  boot-test) and older/legacy-mode hardware are fine; a strict UEFI-only
  machine won't boot it directly yet.
- The screenshot job is best-effort: it boots the live session headless and
  takes several timed screenshots. If GNOME hasn't finished loading by the
  last capture, you'll see a boot/login frame instead of the idle desktop —
  re-run the workflow or bump the wait time in the `screenshot` job if so.
- GitHub Release assets are capped at 2 GB per file; a full `ubuntu-desktop`
  ISO can exceed that. The workflow always uploads a plain Actions artifact
  regardless, as a fallback, and will report (not fail) if the release
  upload is skipped for being oversized.
