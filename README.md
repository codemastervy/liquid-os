# Liquid OS

A real, installable respin of **Ubuntu 24.04 LTS (noble)** with a glassmorphism
"liquid glass" GNOME desktop: translucent windows and panels, real-time
background blur, a procedurally generated liquid-glass wallpaper, and matching
Plymouth/GRUB branding — plus the actual Ubuntu installer (`ubiquity`), so you
can install it to a disk, not just try it live.

Everything is built by **GitHub Actions**. Nothing is installed or compiled on
anyone's machine to produce it — push to this repo, run the workflow, download
the ISO.

## Screenshots

The build pipeline boots its own finished ISO inside GitHub Actions (using
QEMU + KVM on the runner) and auto-captures screenshots, which get committed
to [`docs/screenshots/`](docs/screenshots) by the workflow itself. They'll
show up here once the first successful run completes:

<!-- LIQUID_OS_SCREENSHOTS_START -->
_No screenshots yet — run the workflow (see below) to generate them. The
`screenshot` job commits frames from the boot sequence and finished desktop
straight into this section of this file._
<!-- LIQUID_OS_SCREENSHOTS_END -->

## Build it

1. Go to **Actions → Build Liquid OS ISO → Run workflow** (or push a change
   under `livebuild-overlay/`, `scripts/`, or the workflow file to `main` —
   that triggers a build automatically).
2. The `build` job runs `lb build` to produce the ISO (a full desktop
   live-build typically takes 45–120 minutes on a hosted runner).
3. The `screenshot` job then boots that ISO headless in QEMU, waits for it to
   reach the live desktop, captures frames, and commits the best ones back
   into `docs/screenshots/` and this README.
4. Download the ISO from the run's **Artifacts** section
   (`liquid-os-iso`).
5. To get a permanent, shareable download instead of a 30-day artifact, push
   a tag like `v1.0.0` — the workflow also cuts a GitHub Release with the ISO
   attached.

## Try it

- **Live session:** boot the ISO as-is (USB stick via `dd`/Balena
  Etcher/Rufus, or in a VM — UTM, VirtualBox, VMware, or
  `qemu-system-x86_64 -m 4096 -cdrom Liquid-OS-*.iso -enable-kvm`, dropping
  `-enable-kvm` off Linux) to try the desktop without touching your disk.
- **Install it for real:** the live desktop has an "Install Liquid OS" icon
  that launches `ubiquity`, Ubuntu's normal graphical installer — partitioning,
  language/locale, user account, the works.

## What "Liquid Glass" actually is

- `livebuild-overlay/hooks/live/0100-liquidos-theme.hook.chroot` clones the
  stock Yaru GTK theme into `Yaru-Liquid` / `Yaru-Liquid-dark` and layers
  translucent, rounded-corner CSS onto windows, headerbars, popovers and
  buttons.
- `livebuild-overlay/hooks/live/0200-blur-my-shell.hook.chroot` makes sure the
  [Blur My Shell](https://github.com/aunetx/blur-my-shell) GNOME Shell
  extension is present and enabled (it's pulled in directly via apt in
  `package-lists/desktop.list.chroot`, with a from-source fallback in the
  hook if the archive package is ever unavailable) — this is what gives the
  top bar, overview, and dash real live background blur, not just a flat
  translucent color.
- `scripts/generate-wallpaper.py` procedurally paints a soft, blurred,
  multi-color-blob wallpaper (the actual "liquid glass" look) — regenerated
  on every build with Pillow. It's also reused as the GRUB background and
  swapped into the Plymouth boot theme.
- `livebuild-overlay/includes.chroot/etc/dconf/db/local.d/00-liquidos` sets
  the theme, wallpaper, and extension as defaults out of the box.
- `livebuild-overlay/includes.chroot/etc/os-release` (and `/etc/lsb-release`,
  `/etc/issue`) rebrand the distro as "Liquid OS" while keeping
  `ID_LIKE=ubuntu debian`, so apt/PPAs and anything checking `ID_LIKE` keep
  working normally.

## Repo layout

```
.github/workflows/build-iso.yml   CI pipeline:
                                     build   -> installs live-build, generates
                                                the wallpaper, merges the
                                                overlay below into a
                                                live-build config, runs
                                                `lb build`.
                                     screenshot -> boots the resulting ISO in
                                                QEMU/KVM, captures frames, and
                                                commits them into
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
  hooks/live/                     Scripts run inside the chroot after package
                                   installation: theme build, extension
                                   install, Plymouth/initramfs update, dconf
                                   compile.
docs/screenshots/                 Auto-captured desktop screenshots (written
                                   by CI, not hand-curated).
```

## Notes / known limitations

- This pipeline was authored without a local Linux/QEMU environment to
  test-boot against ahead of time (every package name referenced was
  cross-checked against the Ubuntu 24.04 archive first, but build-time
  ordering issues can still surface). If a run fails, check the `build-log`
  artifact from the failed job.
- The screenshot job is best-effort: it boots the live session headless and
  takes several timed screenshots. If GNOME hasn't finished loading by the
  last capture, you'll see a boot/login frame instead of the idle desktop —
  re-run the workflow or bump the wait time in the `screenshot` job if so.
- GitHub Release assets are capped at 2 GB per file; a full `ubuntu-desktop`
  ISO can exceed that. The workflow always uploads a plain Actions artifact
  regardless, as a fallback, and will report (not fail) if the release
  upload is skipped for being oversized.
