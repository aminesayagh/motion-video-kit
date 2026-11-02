# System requirements

Ubuntu 22.04+ or WSL2 Ubuntu. Install with apt unless noted.

| Need | Install | Used by |
| --- | --- | --- |
| ffmpeg / ffprobe 6+ | `sudo apt install ffmpeg` | every audio step, the gates, assembly |
| Node 18+ | `sudo apt install nodejs` (or nvm) | storyboard SVGs (`build.py`), `node --check` |
| Google Chrome | the `.deb` from google.com/chrome | headless PDF of the storyboard and storybook, SVG screenshots for review |
| uv (optional) | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | creating the Python venvs |
| NVIDIA driver + CUDA (WSL: the Windows driver) | see `nvidia-smi` | Qwen3-TTS on GPU |
| EffectCraft, SoundCraft (ArtCraft suite, native Linux) | the vendor's Linux packages; they install `/usr/bin/effectcraft-cli`, `/usr/bin/soundcraft-cli` | scene builds and renders, scene masters |
| Fonts: Poppins, JetBrains Mono | see below | the kit, the storyboard |

Not needed: Duckling, Docker, any cloud account.

## Fonts

Both are free (SIL Open Font License). Download Poppins (Google Fonts) and JetBrains Mono (jetbrains.com/lp/mono), then:

```bash
mkdir -p ~/.local/share/fonts/video
cp Poppins-{Regular,Medium,SemiBold,Bold}.ttf JetBrainsMono-{Regular,Medium,Bold}.ttf ~/.local/share/fonts/video/
fc-cache -f
fc-list : postscriptname | grep -E "Poppins|JetBrainsMono"   # the kit uses these exact PostScript names
```

Keep a copy in a `fonts/` folder of your project too: the storyboard tools read the `.ttf` files directly.

## Model downloads

The first run downloads the weights to `~/.cache/huggingface` (Qwen3-TTS 0.6B Base about 2.5 GB, Whisper medium.en about 1.5 GB). After that everything works offline.

## Memory (WSL)

Give WSL a fixed budget so a runaway job cannot freeze Windows, in `%UserProfile%\.wslconfig`:

```ini
[wsl2]
memory=12GB
swap=8GB
processors=8
```

Then `wsl --shutdown` and reopen. See docs/05-orchestration.md for the one-heavy-process rule.
