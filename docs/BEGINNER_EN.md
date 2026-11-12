# Your first Hytale texture pack — beginner guide

**For Texture Pack Manager 0.3.1 / API v1 and the [Starter repository](https://github.com/Vltja/texture-pack-manager-examples).** You do not need previous Java experience: change a few files and your own PNGs, then use the included builder. This guide is based on **Hytale 0.7.7** and does not promise compatibility with later versions.

**Goal:** Replace a stone texture, build your own `.jar` mod, install it on a Hytale server, and turn it on or off with `/texturepacks`.

> **Know the difference:** This is a **server-side Java mod**, not a ZIP resource pack you place in a client folder. Texture Pack Manager is installed **separately** on the server. One administrator-selected pack stack applies to all players; per-player pack selection is not currently available.

## 1. Prepare your tools

| You need | Why | How to check or obtain |
|---|---|---|
| **Starter source** | Your editable template | Open the [repository](https://github.com/Vltja/texture-pack-manager-examples), select **Code → Download ZIP**, then extract it. No Git account or command line required. |
| **Python 3.9+** | Runs the included build script | Windows: `py -3 --version`. Linux/macOS: `python3 --version`. |
| **JDK 25+** | Compiles the Java mod | Check `javac -version` and `jar --version`. Install a **JDK**, not only a Java runtime (JRE). |
| **HytaleServer.jar** | Compile-time dependency | Obtain from your own server setup or the [official server manual](https://support.hytale.com/hc/en-us/articles/45326769420827-Hytale-Server-Manual). |
| **Texture Pack Manager 0.3.1 JAR** | Another compile-time dependency and the runtime manager | Obtain separately from the [CurseForge project](https://www.curseforge.com/hytale/mods/texture-pack-manager), when the required release is available. |
| **PNG editor and test server** | Create images and verify results | Use an editor of your choice and a server on which you can install mods and manage permissions. |

You **do not** need Gradle, Maven, an IDE, GitHub Actions, or additional Python packages to build the mod. The two dependency JARs stay on **your machine** and must **not** be uploaded to a public repository or bundled into your pack JAR.

## 2. Download and open the project

1. Open [texture-pack-manager-examples](https://github.com/Vltja/texture-pack-manager-examples).
2. Click **Code → Download ZIP** for the latest source on `main`. Do **not** use the precompiled demo JAR when you want to customize the source.
3. Extract the ZIP, for example into `C:\TexturePacks\MyPack\`.
4. Open the folder that actually contains `build.py` and `README.md`.
5. Open `.java` and `.json` files in a text editor; open `.png` files in an image editor.

Relevant starter files:

~~~text
MyPack/
├── build.py
├── resources/
│   ├── manifest.json
│   └── Common/
│       └── BlockTextures/
│           ├── Rock_Stone.png
│           ├── Rock_Stone_2.png
│           └── Rock_Stone_3.png
└── src/
    └── Vitja/
        └── TexturePackStarter/
            ├── StarterPack.java
            └── StarterPlugin.java
~~~

`StarterPlugin.java` already registers the pack with the manager; leave it unchanged for your first test.

## 3. Replace the stone image

1. Open `resources/Common/BlockTextures/Rock_Stone.png`.
2. Draw your stone texture. **For the first attempt, preserve the original image dimensions, alpha and layout.**
3. Save it as a **PNG**, replacing `Rock_Stone.png` in the same directory with the same spelling and capitalization.
4. The example includes `Rock_Stone_2.png` and `Rock_Stone_3.png`. Replace those as well to cover the example's other stone variants. **Remove unwanted diagnostic images before publishing** or they will also be included.

The source file `resources/Common/BlockTextures/Rock_Stone.png` becomes the JAR resource `Common/BlockTextures/Rock_Stone.png`. Its API target is `BlockTextures/Rock_Stone.png` (**without `Common/`**).

**Want to replace a different texture?** First find its **real `Common/...png` path** in the game assets for the Hytale version you support. Recreate that exact path inside `resources/Common/`, including letter case, and remove demo images you do not want to ship. The build regenerates `resources/textures.list` automatically from **all PNGs** beneath that directory. Do **not** manually edit the list. The manager replaces existing registered image paths; it does not create new game objects from arbitrary filenames.

## 4. Give the pack a new name and ID

For your first local test you only need to edit **two text files**.

### A. Edit `resources/manifest.json`

Use your own values for `Group`, `Name`, `Description` and `Authors`:

~~~json
{
  "Group": "YourName",
  "Name": "BlueStone",
  "Version": "1.0.0",
  "Description": "My custom stone textures.",
  "Authors": [{"Name": "Your Name"}],
  "Main": "Vitja.TexturePackStarter.StarterPlugin",
  "ServerVersion": ">=0.7.0 <0.8.0",
  "Dependencies": {"Vitja:TexturePackManager": "*"},
  "IncludesAssetPack": false
}
~~~

`Group` and `Name` form the **Hytale mod identity**. Make them unique, using a simple name without spaces. **Keep `Main` unchanged for the first build**: it references the existing Java class, not the pack display name. Leave the manager dependency and `"IncludesAssetPack": false` as shown so the manager controls activation. Validate compatibility with the actual game and manager versions you deploy.

### B. Edit `src/Vitja/TexturePackStarter/StarterPack.java`

Find:

~~~java
public static final String ID = "vitja.starter.stone";
~~~

Change it to your own stable, unique ID, for example:

~~~java
public static final String ID = "yourname.bluestone";
~~~

A pack ID uses lowercase `a-z`, digits, `.`, `_` and `-`; it must start with a lowercase letter or digit. This is **not** the same thing as the manifest's `Group:Name` identity. Keep the ID stable when updating the same pack.

Also find:

~~~java
return new TexturePack(ID, "Texture Pack Starter", "1.0.0", "Vitja", entries);
~~~

Change it to:

~~~java
return new TexturePack(ID, "Blue Stone", "1.0.0", "Your Name", entries);
~~~

Leave imports, `create()` and `StarterPlugin.java` alone. All PNGs in `resources/Common/` will be indexed by the build.

## 5. Build the JAR

**On Windows:**

1. Open the project directory in File Explorer.
2. Click the Explorer address bar, type `powershell` and press **Enter** to open PowerShell in this directory.
3. Check `py -3 --version` and `javac -version` first.
4. Run this **single command**, replacing both sample paths with the exact JAR paths on your PC:

~~~powershell
py -3 build.py --server-jar "C:\Hytale\HytaleServer.jar" --manager-jar "C:\Hytale\mods\texture-pack-manager-0.3.1.jar"
~~~

**On Linux/macOS**, open a terminal in the project directory:

~~~sh
python3 build.py --server-jar "/path/to/HytaleServer.jar" --manager-jar "/path/to/texture-pack-manager-0.3.1.jar"
~~~

On success, find `build/texture-pack-starter-1.0.0.jar` and its `.jar.sha256` checksum. The builder intentionally keeps the output prefix `texture-pack-starter-` even after you change your pack's name; the **manifest** identifies the installed Hytale mod. If you change the manifest `Version`, the JAR file's version suffix changes.

The builder regenerates `textures.list`, compiles Java, packages resources and checks the resulting archive. **This output is your pack JAR, not the separate Manager JAR.**

## 6. Install, activate and test

1. **Stop the server** and back up your test configuration.
2. Place the built pack JAR **and** the separately obtained Manager JAR in the server's `mods/` directory. Keep only one installed version per manifest identity.
3. Restart the server. Check server logs for plugin startup or registration errors.
4. Give your administrator the permission `vitja.texturepacks.admin` through your server's permission system.
5. In-game, run `/texturepacks`, enable your pack, then press **Apply / Reload**.
6. Inspect normal stone and its variants. If you only replaced one file, other variants may still show their originals.
7. To revert, disable the pack and press **Apply / Reload** again. `/tpm reset` disables all registered packs and applies the previously captured baseline.

**A listed or registered pack is not proof of correct client rendering.** Test it in the game. Some textures require their original pixel dimensions or extra variants. The Starter artifact has build/registration evidence, not a separate full native gameplay acceptance test.

## 7. Quick troubleshooting

| Symptom | Check |
|---|---|
| `py` or `python3` not found | Install Python 3.9+, reopen the terminal; on some Windows systems `python` works instead of `py -3`. |
| `javac` or `jar` not found | Install **JDK 25+**, configure `JAVA_HOME`/`PATH`, reopen the terminal. |
| `Dependency not found` | Check that both **absolute** JAR paths exist and are quoted. |
| `Wrong dependency JAR` | You must supply the **server** and **manager** JARs, not your own freshly built pack. |
| Java compile error | Verify JDK 25+, Java syntax and dependency versions. |
| Pack missing from `/texturepacks` | Both JARs present? Restarted? Manifest valid? `Main` unchanged or correctly updated? Registration errors in server log? |
| Pack visible but textures unchanged | Enabled **and** Applied? Exact target path/capitalization? Another pack above yours? Missing stone variants? Registered target exists? |
| Wrong image or identity after update | Remove the old installed JAR, keep the same pack ID for an update, rebuild and restart. |
| Missing `textures.list` or empty pack | Run `build.py` and keep at least one PNG under `resources/Common/`. |

See the [developer API guide](API.md) for detailed troubleshooting, priorities, dimensions and registration rules.

## 8. Before publishing: rename the Java namespace

Keeping the original `Main` makes your first local test easier. **Before publishing**, give the project its own Java package so independent forks do not reuse the template namespace:

1. Move both Java files from `src/Vitja/TexturePackStarter/` to `src/YourName/BlueStone/`.
2. At the top of **both** Java files, change `package Vitja.TexturePackStarter;` to `package YourName.BlueStone;`.
3. Change the manifest entry to `"Main": "YourName.BlueStone.StarterPlugin"`.
4. Rebuild; ensure the Java `package`, source folders, class name and manifest `Main` match.
5. Keep the manifest version and `new TexturePack(...)` version string in sync when releasing an update.

On **CurseForge**, add the actual Texture Pack Manager project as a **Required Dependency** on every published pack file **in addition to** declaring it in your `manifest.json`. Publish only textures you made or have rights to redistribute. Test against your target server and Manager version.

## 9. Ask ChatGPT using your GitHub link

Copy the URL of the [Starter repository](https://github.com/Vltja/texture-pack-manager-examples) or your own public fork, paste it into ChatGPT and ask how to create your pack. You can copy this request:

~~~text
I am a beginner and want to make my own Hytale texture pack for Texture Pack
Manager. This is my GitHub repository:
https://github.com/YOUR-NAME/YOUR-REPOSITORY

Please read README.md, docs/BEGINNER_EN.md, docs/API.md,
resources/manifest.json, build.py, and the Java sources under src/ first.
Then tell me exactly what to edit to replace the stone textures, set a
unique mod name and pack ID, build the JAR, and test it in the game.
Use actual files and versions from this repository. Give copy-paste-ready
examples and the path of each file to edit. If you cannot read a file,
ask for it instead of guessing. Do not modify or push files without
my explicit authorization.
~~~

**Access is not automatic.** ChatGPT can generally read a **public** GitHub repository by URL when web access is available. A **private** repo requires an authorized integration or files you provide. Sharing a URL does **not** give ChatGPT access to your computer or write access to GitHub. A user-connected PC/GitHub integration can make those operations possible **only with the permissions actually granted**. **GitHub Actions/CI does not itself provide ChatGPT access**; it only runs configured jobs.

Never paste tokens, passwords or private keys into the chat, and do not upload proprietary dependency JARs to GitHub.

---

Next: Find another real `Common/...png` path, add its replacement, rebuild and test. For advanced pack stacks, mod patches and experimental native JSON definitions, consult the [API guide](API.md).
