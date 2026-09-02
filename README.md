# Liquid OS

![Liquid OS desktop](docs/screenshots/desktop.png)

Liquid OS is a full desktop Linux distro built on Ubuntu 24.04 LTS, wrapped in
a glassmorphism "liquid glass" GNOME desktop: translucent windows and panels,
real-time background blur behind the top bar and overview, and a soft,
colorful, procedurally generated wallpaper that carries through into the boot
screen and GRUB menu. It's a real, installable OS — full `ubuntu-desktop`
plus Ubuntu's actual graphical installer — not a stripped-down demo.

Built end to end by a GitHub Actions workflow, and every screenshot below is a
framebuffer grab from the released ISO actually booted in QEMU — not a mockup.
The published release was reassembled from its split parts and checked against
its own SHA256 before those grabs were taken.

## Screenshots

![Activities overview](docs/screenshots/activities-overview.png)

The GNOME Activities overview, with Blur My Shell's rounded blur pipeline.

![Terminal](docs/screenshots/terminal.png)

A terminal over the wallpaper — `/etc/os-release` and the `liquid@liquidos`
prompt, from the live session.

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

- **Download the latest release:**
  [v1.0.1](https://github.com/codemastervy/liquid-os/releases/tag/v1.0.1).
  The ISO is ~2.4 GB and GitHub caps release assets at 2 GB, so it is
  published as split parts. Reassemble and verify with:

  ```sh
  cat Liquid-OS-*.iso.part-* > Liquid-OS.iso
  sha256sum -c Liquid-OS-*.iso.sha256
  ```
- **Build it yourself:** go to **Actions → Build Liquid OS ISO → Run
  workflow**, wait for it to finish (a full desktop build typically takes
  15–30 minutes), then grab the `liquid-os-iso` artifact from that run.

## Try it

- **Live session:** boot the ISO as-is — in a VM (UTM, VirtualBox, VMware) or
  from a USB stick (Balena Etcher, Rufus, `dd`) — to try the desktop without
  touching your disk. In UTM on Apple Silicon: create a new VM using
  "Emulate" (not "Virtualize" — that only supports arm64 guests, and this
  ISO is x86_64), pick Linux, attach the ISO as the boot drive, and give it
  **at least 4 GB of RAM** (see the note under known limitations — 2 GB is
  not enough for GNOME Shell on a software renderer).
- **Install it for real:** the live desktop has an "Install Liquid OS" icon
  that launches `ubiquity`, Ubuntu's normal graphical installer.

## Repo layout

```
.github/workflows/build-iso.yml   CI pipeline: installs live-build, generates
                                   the wallpaper, merges the overlay below
                                   into a live-build config, runs `lb build`.
scripts/generate-wallpaper.py     Procedural liquid-glass wallpaper generator.
livebuild-overlay/
  package-lists/                  Packages installed via apt during the
                                   build: full ubuntu-desktop, the ubiquity
                                   installer stack, GNOME extensions/tweaks.
  includes.chroot/                Files copied verbatim onto the live
                                   filesystem (os-release/issue branding,
                                   casper.conf, dconf defaults, grub
                                   background config, wallpaper output).
  includes.binary/                Files placed in the ISO root itself --
                                   /.disk/info, which brands the media.
  hooks/                          Scripts run inside the chroot after package
                                   installation: theme build, extension
                                   install, installer branding,
                                   Plymouth/initramfs update, dconf compile.
```

## Problems worth writing down

Most of the work here wasn't theming, it was getting a 2.4 GB image to boot at
all. Ubuntu's `live-build` is a fork of Debian's `3.0~a57` with its own
patches, and a lot of its documented behaviour no longer matches what it
actually does. The findings that cost the most time:

- **A one-character typo dropped the live session into a BusyBox shell.**
  `casper.conf` was setting `BUILDSYSTEM`, but casper reads `BUILD_SYSTEM`.
  With it unset, `casper-helpers` leaves `MP_QUIET=""`, and casper then runs
  `modprobe "${MP_QUIET}" -b overlay` — a quoted *empty* first argument, which
  fails. Casper panics with "cow format specified as 'overlay' and no support
  found" and drops to a rescue shell, which reads exactly like a missing
  kernel module. Found by booting the ISO and reading casper's own
  `/casper.log`. ([`57ca973`](../../commit/57ca973))

- **An extension was enabled with none of its code installed.** The
  Blur My Shell hook copied the cloned repo's *root* into the extension
  directory. But that project keeps `metadata.json`, `schemas/` and
  `resources/` at the root and all the actual code in `src/` — its Makefile
  packs the two together. The result passed every casual check (a valid
  `metadata.json` was right there) while shipping a directory containing
  `Makefile` and `README.md` and no `extension.js`. The build now assembles it
  the way `make build` does and hard-fails if the code or compiled schemas are
  missing, rather than shipping a feature that silently does nothing.
  ([`37ea787`](../../commit/37ea787))

- **A "broken" image was a starved VM.** A GNOME session that came up as
  "Oh no! Something has gone wrong." was diagnosed as a branding regression
  and the branding was reverted — wrongly. GNOME Shell 46 on llvmpipe doesn't
  fit in 2 GB; gnome-shell was being OOM-killed behind an otherwise clean
  boot. The same ISO boots straight to the desktop at 4 GB. Casper only reads
  `FLAVOUR` to decide whether `/.disk/info` may override the username, so it
  was never capable of breaking a session. The branding went back in and the
  real constraint got documented instead. ([`0bb4296`](../../commit/0bb4296))

- **Hooks that never ran, silently.** They were at
  `config/hooks/live/*.hook.chroot`, following current live-build docs. This
  version wants `config/hooks/*.chroot`. Nothing warns you — the build
  succeeds and simply skips every customisation.
  ([`d5d4e7a`](../../commit/d5d4e7a))

- **`lb build` had to be split apart.** Its bundled isolinux template assumes
  Debian's `live-boot` layout, but this image uses Ubuntu's `casper`, which
  puts the kernel in `binary/casper/` under a versioned filename that can't be
  known before the chroot is built. So the build runs `lb bootstrap` and
  `lb chroot`, reads the installed kernel version off disk, writes its own
  isolinux config, and only then runs `lb binary`.
  ([`ca190d1`](../../commit/ca190d1))

A related lesson in verification: `packages.ubuntu.com` returns HTTP 200 for
"No such package", so an early check for a package that didn't exist passed on
the status code alone. Checking response *content* replaced it.

## Notes / known limitations

- The ISO currently boots BIOS/legacy (isolinux) only — no UEFI boot yet.
  Most VMs and older/legacy-mode hardware are fine; a strict UEFI-only
  machine won't boot it directly yet.
- GitHub Release assets are capped at 2 GB per file; a full `ubuntu-desktop`
  ISO can exceed that, so the workflow splits it into `.part-*` files and
  publishes a `.sha256` next to them (see **Get it** above for reassembly).
  A plain Actions artifact is always uploaded too, as a fallback.
- **Give it at least 4 GB of RAM.** GNOME Shell 46 on a software renderer
  (llvmpipe — which is what you get in a VM without GPU passthrough) does not
  fit comfortably in 2 GB: gnome-shell gets OOM-killed during startup and
  `gnome-session` puts up "Oh no! Something has gone wrong." with an otherwise
  healthy boot behind it. 4 GB boots to the desktop reliably. If you see that
  screen, raise the VM's memory before assuming the image is broken.
