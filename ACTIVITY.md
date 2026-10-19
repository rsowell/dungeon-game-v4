# Background audio and a playable web link

Start with your previous game. Keep a backup. The enclosed main.py is the completed reference, with the same rooms, objects, commands, text files, and short sound effects as last time.

By the end, you should be able to explain how a repeating background track runs while the player types, and give someone a working public game link.

## 1. Run the completed example

Open a terminal in the folder containing main.py. Use your existing Python environment if pygame and pygbag already work. Otherwise install them:

```bash
python -m pip install pygame-ce
python -m pip install pygbag
```

Then, run the game:
```bash
python main.py
```

Click the window, press Enter to start audio, then type commands. The first Enter starts music; it does not submit a command. Press M with an empty command line to mute/unmute music; effects still play. Refresh the browser or rerun Python to restart after winning or losing.

The background clip should repeat while you can still type and move. Try:

```text
look
go north
attack wolf
attack goblin
take diamond
take coin
go west
take axe
go east
go east
attack dragon
go west
go east
take chalice
```

Notice: music continues across entrance, hall, and armory; it changes in the lair and changes back when you leave. Returning to the lair starts its track from the beginning. On winning or losing, background music stops and the ending effect plays.

## 2. Add one background track first

Copy `assets/ambient.ogg` into your game's assets folder, or use a short track your team can publish. This package uses OGG for compact, browser-friendly audio. Test the actual format in a browser.

After the mixer is initialized, these three calls are the basic idea:

```python
pygame.mixer.music.load(str(ASSET_DIR / "ambient.ogg"))
pygame.mixer.music.set_volume(0.25)
pygame.mixer.music.play(-1)
```

`load` selects the file; `set_volume` sets a level from 0.0 to 1.0; `play(-1)` repeats indefinitely. Playback runs in the background: it does not wait for the track to finish. Keep processing events and drawing as before. Do not put `play` in the drawing function or call it each frame: that keeps restarting it. Set volume after loading because loading resets music volume.

Keep the existing `pygame.mixer.Sound(...).play()` calls for short effects. Pygame has one music stream and separate sound channels, so a pickup effect can play over the background track. This example replaces one background track with another; it does not layer two background tracks.

For browser use, start music after player interaction. In the reference, inspect `start_music()` and the Enter branch in `main()`. The game waits for Enter before starting. Click any pygbag start prompt first, then click the game and press Enter. Browser audio policies differ; always test the public link.

**Checkpoint:** Add just one repeating track to your own game. Can a teammate hear the loop and still type commands? Is the music quiet enough for the effects?

## 3. Add room-specific music

Compare these changes in the completed main.py with your previous version:

1. `Room.__init__` accepts `music=None` and saves it as `self.music`. None means use the game's default background track.
2. `TextAdventure.__init__` initializes `default_music`, `current_music`, `music_started`, and `music_muted`. The lair supplies `music="lair_music.ogg"`; the other rooms use the default.
3. `update_music()` chooses `self.current_room.music or self.default_music`. If the chosen filename is already playing, it returns immediately. Otherwise it loads the new file, sets volume, starts the loop, and remembers the filename.
4. `go()` calls `update_music()` immediately after changing `self.current_room`. Entering another room with the same track does not restart it.
5. The win and loss branches call `pygame.mixer.music.stop()`. `toggle_music()` sets music volume to zero or restores it; it does not stop sound effects.

Discuss: Why do we remember the current filename? Why should the music update happen when we change rooms? Why does `play(-1)` not require a Python loop?

**Throughout the game option:** remove the lair's `music="lair_music.ogg"` argument. Every room now uses ambient.ogg. Keep the end-of-game stop calls if you want silence under the ending effect.

**Only in one room option:** in `update_music()`, choose `filename = self.current_room.music` instead. After the existing early return and before `load`, add:

```python
if filename is None:
    pygame.mixer.music.stop()
    self.current_music = None
    return
```

Now unmarked rooms are silent. Keep the lair's music argument.

## 4. Test the browser before publishing

From the folder containing main.py:

```bash
python -m pygbag .
```

Open the localhost URL printed in the terminal. Leave that terminal running. Click to start, press Enter, and repeat the test route. Check text, effects, repeated background audio, room transitions, mute, and ending behavior. Ctrl+C stops the local server. Opening main.py or a generated index.html directly in a browser is not this test.

# Deploy your Pygame game to GitHub Pages

Git saves snapshots locally. GitHub stores your repository online. pygbag builds a browser version. GitHub Actions runs the build, and GitHub Pages hosts the result. A local save or commit does not update the website; a push followed by a successful deployment does.

## 1. Find the project root

Extract the ZIP first. Open the actual web_text_adventure folder, containing main.py, assets/, text/, .gitignore, and .github/. In VS Code, open this folder with File → Open Folder, then Terminal → New Terminal. Hidden files may be invisible in your file manager.

In macOS/Linux or Windows Git Bash:

```bash
pwd
ls -a
```

In PowerShell use `Get-Location` and `Get-ChildItem -Force`.

**Checkpoint:** main.py and .github are together at this level. The workflow must be `.github/workflows/pages.yml` at the repository root. Do not initialize Git in the outer folder containing web_text_adventure. 

## 2. Check Git and identity

```bash
git --version
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Use your own name and a GitHub-associated email or GitHub no-reply email. These settings label commits; they do not log you in. Install Git if needed from https://git-scm.com/install and restart the terminal. On macOS, Apple's Command Line Tools also supply Git.

If your team already has a repository, run `git status` and `git remote -v`. If these show the intended repository, keep it and skip the new-repository commands in steps 3–4. Pull teammates' changes before editing. Ensure this package's .github/workflows/pages.yml and .gitignore are present in the appropriate places. 

## 3. Create an empty public GitHub repository

Sign in at https://github.com (create and verify an account if needed). Choose **+ → New repository**. Use a name such as `dungeon-game`, select **Public**, and leave initialization options for README, .gitignore, and license unchecked. Click **Create repository**. Public repositories support Pages on GitHub Free. Copy the HTTPS repository URL.

## 4. Upload the first snapshot

In the project root, run these one at a time. Replace the example URL with the one you copied:

```bash
git init
git branch -M main
git status
git add .
git status
git commit -m "Add game with background audio"
git remote add origin https://github.com/YOUR-USERNAME/dungeon-game.git
git push -u origin main
```

`status` shows changes; `add` stages them; `commit` records a local snapshot; `push` uploads it. The first push's `-u` remembers the destination. Review staged files before committing: include assets, text, main.py, requirements.txt, .gitignore, and .github; exclude .venv and build output.

If prompted, complete the Git credential manager's browser sign-in. Your GitHub account password will not work as an HTTPS Git password. If browser sign-in is unavailable, ask the instructor to help configure GitHub CLI or a personal access token; do not put credentials in source files or repository URLs.

**Checkpoint:** refresh GitHub's Code tab. main.py must be at the top level. Open `.github/workflows/pages.yml` and confirm it is there. If origin already exists, inspect `git remote -v` and use the intended existing remote; do not repeat initialization or change a shared repository's remote blindly.

## 5. Enable Pages

On the repository, open **Settings → Pages**. Under **Build and deployment**, set **Source** to **GitHub Actions**. Use the supplied workflow; you do not need to choose a Jekyll template or publish from a branch.

Open **Actions → Build and publish dungeon game**. The initial push may already have triggered a run. If it failed because Pages was not enabled, use **Re-run all jobs**, or select **Run workflow** on main after enabling Pages. GitHub may first ask you to enable Actions.

## 6. Read the run

Open the newest run. The build job installs pygbag, packages the root folder, and uploads build/web. The deploy job publishes that artifact. Wait for both jobs to succeed; this can take several minutes. A green build job alone is not a completed deployment.

**Checkpoint:** open **Settings → Pages → Visit site**, or the deployment URL shown in the Actions run. Expect a URL resembling `https://YOUR-USERNAME.github.io/dungeon-game/`. Use the URL GitHub supplies; the repository's github.com URL is source code, not the game.

## 7. Play the public game

Open the link in a separate tab. Click the start prompt/game and press Enter. Test commands, sound effects, at least two full background loops, entering/leaving the lair, mute, and the ending. Have another teammate open the link on a different computer. Initial loading needs an internet connection and can take time.

## 8. Prove the next update works

Change a sentence in text/hall.txt and save it. From the same project folder:

```bash
git status
git add text/hall.txt
git commit -m "Revise hall description"
git push
```

Watch the new Actions run until deployment succeeds. Reload the public game, travel to the hall, and type `look`. Try a hard refresh if you see the old text. For future updates, stage the actual files you changed, including new audio assets and main.py.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| No workflow in Actions | `.github/workflows/pages.yml` must be committed at the repository root on main. Hidden .github folders can be missed when copying. |
| Red Actions run | Open the failed job and expand the failed step; read the error before changing code. |
| Pages deployment fails | Set Pages source to GitHub Actions; verify repository permissions and rerun. |
| Site returns 404 | Wait for deploy, check the full repository path in the URL, and use Visit site. |
| Blank game or Python error | Compare with local pygbag; inspect browser developer console. Check committed assets/text and exact capitalization. |
| Silent audio | Click the start prompt and game, press Enter, check tab/system volume and M mute; verify audio files were committed. |
| Old version | Check the newest deployment succeeded, then hard refresh. |
| Push rejected | Check the remote URL and access. For teammates' updates, commit your work, pull as appropriate, resolve conflicts, then push; do not force-push. |
| File too large | Keep audio short/compressed. GitHub rejects ordinary Git files over 100 MiB. If already committed, deleting it in a later commit does not remove it from history; ask for help. |


## References

- Pygame music: https://www.pygame.org/docs/ref/music.html
- pygbag: https://github.com/pygame-web/pygbag
- GitHub Pages publishing source: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
