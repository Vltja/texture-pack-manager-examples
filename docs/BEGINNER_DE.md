# Dein erstes Hytale-Texture-Pack – Anleitung für Anfänger

**Für Texture Pack Manager 0.3.1 / API v1 und das [Starter-Projekt](https://github.com/Vltja/texture-pack-manager-examples).** Du brauchst keine Java-Erfahrung. Für den ersten Test änderst du Bilder und wenige Textstellen; das Starter-Projekt übernimmt die Registrierung. Die Anleitung ist für den Stand **Hytale 0.7.7** geschrieben und garantiert keine Kompatibilität mit anderen Versionen.

**Das Ziel:** Du ersetzt eine Steintextur, baust daraus eine `.jar`-Datei, installierst sie auf deinem Hytale-Server und schaltest sie über `/texturepacks` ein und aus.

> **Wichtig:** Das ist eine *Server-Mod*, kein gewöhnliches ZIP-Resource-Pack zum Ablegen auf deinem eigenen Client. Der **Texture Pack Manager** muss separat auf dem Server installiert sein. Der Administrator entscheidet für alle Spieler gemeinsam, welche Packs aktiv sind.

## 1. Was du brauchst

| Benötigt | Wofür? | Prüfen / beziehen |
|---|---|---|
| **Starter-Quellcode** | Deine Vorlage mit Java-Dateien und Beispieltexturen | Auf [GitHub](https://github.com/Vltja/texture-pack-manager-examples) **Code → Download ZIP** wählen und entpacken. Du brauchst dafür weder Git noch ein GitHub-Konto. |
| **Python 3.9 oder neuer** | Startet den mitgelieferten Build | In PowerShell `py -3 --version`, unter Linux/macOS `python3 --version` |
| **JDK 25 oder neuer** | Übersetzt die Java-Dateien in eine Mod | Im Terminal `javac -version` und `jar --version` ausführen. Das **JDK**, nicht nur eine Java-Laufzeitumgebung (JRE), installieren. |
| **HytaleServer.jar** | Kompilier-Abhängigkeit passend zu deinem Server | Aus deiner eigenen Hytale-/Serverinstallation bzw. über die [offizielle Server-Anleitung](https://support.hytale.com/hc/en-us/articles/45326769420827-Hytale-Server-Manual). |
| **Texture Pack Manager 0.3.1 JAR** | Weitere Kompilier-Abhängigkeit und Laufzeit-Mod | Separat vom [CurseForge-Projekt](https://www.curseforge.com/hytale/mods/texture-pack-manager), sofern die Version dort verfügbar ist. |
| **PNG-Bildeditor und Testserver** | Eigene Bilder malen und das Ergebnis kontrollieren | Z. B. ein Bildeditor deiner Wahl; nutze einen Server, auf dem du Mods und Berechtigungen verwalten darfst. |

**Nicht benötigt:** Gradle, Maven, eine IDE, ein GitHub-Actions-Workflow oder ein spezielles Programm zum Erstellen des Texture-Packs. Python verwendet für den Mod-Build nur die Standardbibliothek.

**Beide Abhängigkeits-JARs bleiben auf deinem eigenen Rechner.** Lade `HytaleServer.jar` und die Manager-JAR **nicht** in dein öffentliches GitHub-Repository hoch. Sie werden beim Bauen gelesen, nicht in dein Pack eingebettet.

## 2. Lade die Vorlage herunter und finde die Dateien

1. Öffne [texture-pack-manager-examples](https://github.com/Vltja/texture-pack-manager-examples).
2. Klicke **Code → Download ZIP** (aktuelle `main`-Version), nicht auf „Download demo JAR“.
3. Entpacke die ZIP-Datei, beispielsweise nach `C:\TexturePacks\MeinPack\`.
4. Öffne den **Ordner, in dem `build.py` und `README.md` liegen**. Falls du stattdessen nur einen weiteren Ordner siehst, öffne diesen zuerst.
5. Nutze einen Texteditor für `.java`- und `.json`-Dateien. Ein Bildeditor ist für `.png`-Dateien zuständig.

Wichtige Dateien:

~~~text
MeinPack/
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

`StarterPlugin.java` meldet das Pack beim Manager an. Für dein erstes Pack musst du diese Datei **nicht** ändern.

## 3. Ersetze eine Steintextur

1. Öffne `resources/Common/BlockTextures/Rock_Stone.png` in deinem Bildeditor.
2. Erstelle deine eigene Steintextur. **Behalte zuerst die Abmessungen, Transparenz und grundsätzliche Bildaufteilung des Originalbildes bei.**
3. Speichere als **PNG** mit genau demselben Dateinamen am selben Ort: `Rock_Stone.png`.
4. Die Vorlage enthält außerdem `Rock_Stone_2.png` und `Rock_Stone_3.png`. Ersetze auch diese, wenn alle Steinvarianten anders aussehen sollen. **Lösche die übrigen Demo-Bilder vor einer Veröffentlichung, wenn du sie nicht mitliefern willst.**

**Warum ist der Pfad so wichtig?** Der Manager überschreibt eine vorhandene Hytale-Textur über ihren *exakten* Pfad. Bei diesem Beispiel ist das Ziel `BlockTextures/Rock_Stone.png`. In deinem Projekt liegt die Datei unter `resources/Common/BlockTextures/Rock_Stone.png`. **`Common/` gehört zum Projekt-/JAR-Dateipfad, aber nicht zum API-Ziel.** Achte auf Groß-/Kleinschreibung.

**Eine andere Textur ändern?** Ermittle zunächst den wirklichen `Common/...png`-Pfad dieser Textur aus den Assets deiner unterstützten Hytale-Version. Lege ihn unter `resources/Common/` identisch nach und entferne nicht gewünschte Beispieltexturen. Die Build-Datei erzeugt die Liste `resources/textures.list` automatisch aus allen dort vorhandenen PNGs. Du musst diese Liste **nicht von Hand bearbeiten**. Die Ziel-Datei muss im Spiel bereits existieren; ein Fantasiedateiname erzeugt kein neues Objekt.

## 4. Name und eindeutige Kennung eintragen

Für den ersten lokalen Versuch musst du **nur zwei Textdateien** bearbeiten: `resources/manifest.json` und `src/Vitja/TexturePackStarter/StarterPack.java`.

### A. `resources/manifest.json` bearbeiten

Ändere die Werte von `Group`, `Name`, `Description` und `Authors`. Beispiel:

~~~json
{
  "Group": "DeinName",
  "Name": "BlauerStein",
  "Version": "1.0.0",
  "Description": "Meine selbst gestalteten Steintexturen.",
  "Authors": [{"Name": "Dein Name"}],
  "Main": "Vitja.TexturePackStarter.StarterPlugin",
  "ServerVersion": ">=0.7.0 <0.8.0",
  "Dependencies": {"Vitja:TexturePackManager": "*"},
  "IncludesAssetPack": false
}
~~~

Beachte:

- `Group` und `Name` bilden zusammen die **Identität der Hytale-Mod**. Wähle sie für dein eigenes Pack eindeutig und verwende bei `Name` am besten keine Leerzeichen.
- **Lass `Main` beim ersten Test unverändert**. Es benennt die tatsächliche Java-Klasse in der Vorlage. Wenn du den Text dort nur wegen des neuen Pack-Namens änderst, kann die Mod nicht starten.
- **Behalte** die Manager-Abhängigkeit und `"IncludesAssetPack": false` bei. Sonst umgehst du gegebenenfalls die Ein-/Ausschaltfunktion des Managers.
- Das Beispiel `ServerVersion` ist der im Starter deklarierte Bereich und kein Freibrief für andere Versionen. Teste auf deiner konkreten Version.

### B. `StarterPack.java` bearbeiten

Öffne `src/Vitja/TexturePackStarter/StarterPack.java`. Suche diese Zeile:

~~~java
public static final String ID = "vitja.starter.stone";
~~~

Ersetze sie z. B. durch:

~~~java
public static final String ID = "deinname.blauerstein";
~~~

**Diese Pack-ID muss eindeutig und dauerhaft gleich bleiben.** Sie ist etwas anderes als `Group:Name` aus der Manifest-Datei. Erlaubt sind nur Kleinbuchstaben, Ziffern, Punkt, Minus und Unterstrich; beginne mit einem Buchstaben oder einer Ziffer.

Suche in derselben Datei nach:

~~~java
return new TexturePack(ID, "Texture Pack Starter", "1.0.0", "Vitja", entries);
~~~

Ersetze sie durch:

~~~java
return new TexturePack(ID, "Blauer Stein", "1.0.0", "Dein Name", entries);
~~~

Du brauchst weder die `import`-Zeilen noch `StarterPlugin.java` oder die Methode `create()` anzupassen. Die Registrierung bleibt erhalten; die ersetzten PNGs werden beim Bauen automatisch aufgelistet.

## 5. JAR erstellen – exakte Befehle

**Windows (PowerShell):**

1. Öffne den Projektordner im Datei-Explorer.
2. Klicke in die Adressleiste, tippe `powershell` und drücke **Enter**. Das Terminal öffnet sich direkt im Projektordner.
3. Prüfe mit `py -3 --version` und `javac -version`, ob Python und JDK gefunden werden.
4. Führe **eine** Zeile aus und ersetze **beide Beispielpfade** mit den tatsächlichen Speicherorten auf deinem PC:

~~~powershell
py -3 build.py --server-jar "C:\Hytale\HytaleServer.jar" --manager-jar "C:\Hytale\mods\texture-pack-manager-0.3.1.jar"
~~~

**Linux/macOS (Terminal im Projektordner):**

~~~sh
python3 build.py --server-jar "/pfad/zu/HytaleServer.jar" --manager-jar "/pfad/zu/texture-pack-manager-0.3.1.jar"
~~~

**Erfolg:** Du findest `build/texture-pack-starter-1.0.0.jar` und eine `.jar.sha256`-Prüfsummendatei. Der Builder verwendet den festen Dateinamens-Präfix `texture-pack-starter-`, auch wenn du dem Pack im Manifest einen anderen Namen gibst; maßgeblich für die Mod-Identität ist das Manifest. Bei einer anderen `Version` ändert sich die Versionsnummer des Dateinamens.

Der Builder erzeugt `resources/textures.list` neu, kompiliert die Java-Dateien, nimmt alle Ressourcen in die JAR auf und prüft die fertige Datei. **Die eigene JAR ist nicht identisch mit der Manager-JAR; du brauchst beide.**

## 6. Im Spiel testen und rückgängig machen

1. **Server stoppen.** Sichere die bisherige Konfiguration deines Testservers.
2. Kopiere deine neu gebaute JAR **und** die passende Manager-JAR in den Serverordner `mods/`. Pro Mod-Identität darf nur eine Version installiert sein.
3. Server neu starten und im Server-Log nach Lade- oder Registrierungsfehlern suchen.
4. Stelle sicher, dass dein Administrator die Berechtigung `vitja.texturepacks.admin` besitzt.
5. Im Spiel `/texturepacks` eingeben, dein neues Pack **aktivieren** und **Apply / Reload** auswählen.
6. Einen normalen Steinblock und seine Varianten ansehen. Falls du nur `Rock_Stone.png` geändert hast, können andere Steinvarianten unverändert bleiben.
7. Zum Vergleichen das Pack **deaktivieren** und erneut **Apply / Reload** auswählen. `/tpm reset` deaktiviert alle registrierten Packs und stellt die zuvor erfasste Ausgangsauswahl wieder her.

**„Pack wird angezeigt“ bedeutet nicht automatisch „alle Texturen funktionieren“.** Prüfe die Grafik im Spiel. Manche Materialien verlangen bestimmte Bildabmessungen oder haben zusätzliche Varianten. Die Vorlage ist kompilier- und registrierungsgeprüft; ein eigenständiger vollständiger Gameplay-Abnahmetest des Starter-Artefakts ist nicht dokumentiert.

## 7. Häufige Probleme

| Problem | Das zuerst prüfen |
|---|---|
| `py` oder `python3` nicht gefunden | Python 3.9+ installieren und Terminal neu öffnen. Auf manchen Windows-Systemen funktioniert `python` statt `py -3`. |
| `javac` oder `jar` nicht gefunden | **JDK 25+** statt nur JRE installieren; `JAVA_HOME`/`PATH` prüfen; Terminal neu öffnen. |
| `Dependency not found` | Stimmt der **vollständige Pfad** zur jeweiligen JAR? Steht er in Anführungszeichen? |
| `Wrong dependency JAR` | Sind `HytaleServer.jar` und die **Manager 0.3.1 JAR** wirklich die richtigen Dateien? Nicht die selbst gebaute Pack-JAR als Manager-Abhängigkeit angeben. |
| Java-Kompilierungsfehler | Ist die JDK-Version mindestens 25? Hast du versehentlich Java-Syntax geändert? Passen die Abhängigkeitsversionen? |
| Pack taucht nicht in `/texturepacks` auf | Beide JARs installiert? Server neugestartet? `manifest.json` syntaktisch gültig? `Main` unverändert bzw. korrekt umbenannt? Registrierungsfehler im Log? |
| Pack sichtbar, Bild unverändert | Aktiviert **und** Apply gedrückt? Richtiger Pfad und Groß-/Kleinschreibung? Gibt es mehrere Varianten oder ein anderes Pack mit höherer Priorität? Originalziel im Spiel vorhanden? |
| Falsche Bilder oder IDs nach Update | Alte Pack-Version aus `mods/` entfernen, Pack-ID für dieselbe Mod beibehalten, neu bauen und Server neu starten. |
| Fehlendes `textures.list` | Den vorgesehenen `build.py` ausführen und mindestens eine PNG unter `resources/Common/` lassen. Keine leere Pack-Sammlung bauen. |

Mehr technische Details: [API-Leitfaden](API.md), besonders **Troubleshooting**, **Priority** und **Resolution**.

## 8. Für eine eigene veröffentlichte Mod: Java-Paket ebenfalls umbenennen

Für die ersten Tests bleibt `Main` absichtlich unverändert, damit weniger schiefgehen kann. **Bevor du dein Pack veröffentlichst**, ersetze zusätzlich den Beispiel-Namensraum, um Konflikte mit anderen Forks zu vermeiden:

1. Verschiebe **beide** Java-Dateien aus `src/Vitja/TexturePackStarter/` nach `src/DeinName/BlauerStein/`.
2. Ändere in **beiden** Dateien die erste Zeile von `package Vitja.TexturePackStarter;` zu `package DeinName.BlauerStein;`.
3. Setze im `manifest.json`: `"Main": "DeinName.BlauerStein.StarterPlugin"`.
4. Kontrolliere, ob Java-Klassennamen, Dateinamen, `package` und `Main` zusammenpassen, dann baue die JAR erneut.
5. Wenn du die Versionsnummer erhöhst, halte `manifest.json` und den sichtbaren Versionsstring in `StarterPack.java` zusammen aktuell.

Beim Hochladen auf **CurseForge** musst du zusätzlich zur Manifest-Abhängigkeit die **Texture-Pack-Manager-Mod als „Required Dependency“** für deine veröffentlichte Datei hinterlegen. Verwende nur Texturen, die du selbst erstellt hast oder verbreiten darfst. Versionsabhängigkeit und echte Darstellung auf deinem Zielserver testen.

## 9. Hilfe mit ChatGPT: GitHub-Link kopieren

Du kannst ChatGPT bitten, **dieses Starter-Repository zu lesen und dein eigenes Pack Schritt für Schritt daraus abzuleiten**. Kopiere dafür die URL der Vorlage oder deines eigenen öffentlich lesbaren Forks und sende sie mit deiner Frage an ChatGPT.

**Kopierbare Beispiel-Frage:**

~~~text
Ich möchte als Anfänger mein eigenes Hytale-Texture-Pack für den Texture Pack
Manager erstellen. Hier ist mein GitHub-Repository:
https://github.com/DEIN-NAME/DEIN-REPOSITORY

Bitte lies zuerst README.md, docs/BEGINNER_DE.md, docs/API.md,
resources/manifest.json, build.py und die Java-Dateien unter src/.
Erkläre mir auf Deutsch genau, welche Dateien ich bearbeiten muss,
um eine eigene Steintextur einzubauen, dem Pack einen eindeutigen Namen
und eine eigene ID zu geben, die JAR zu bauen und sie im Spiel zu testen.
Verwende die tatsächlich im Repository vorhandenen Dateinamen und API-Versionen.
Gib mir fertige Codebeispiele und sage dazu, wohin ich sie kopieren muss.
Wenn dir eine Datei oder Berechtigung fehlt, frage danach und erfinde nichts.
Ändere keine Dateien und pushe nichts, bevor ich das ausdrücklich erlaube.
~~~

**Ohne eigenen GitHub-Fork?** Ersetze die URL im Beispiel durch die [Starter-URL](https://github.com/Vltja/texture-pack-manager-examples).

**Wichtig zum Zugriff:** Ein **öffentliches** GitHub-Repository kann ChatGPT in der Regel über den Link lesen, sofern die Web-Funktionen verfügbar sind. **Private** Repositorys erfordern eine ausdrücklich eingerichtete, berechtigte Verbindung oder bereitgestellte Dateien. Nur weil du ChatGPT eine URL schickst, hat es **keinen automatischen Zugriff auf deinen PC**, private Dateien oder Schreibrechte auf GitHub. Ein verbundener PC bzw. eine GitHub-Verbindung kann solche Arbeiten ermöglichen, soweit der Nutzer Zugriff erteilt hat. **GitHub Actions/CI allein gibt ChatGPT keinen PC- oder GitHub-Zugriff**; CI führt lediglich die im Repository konfigurierten Automatisierungen aus.

Teile niemals GitHub-Tokens, Passwörter, private Schlüssel oder nicht zur Weitergabe bestimmte Abhängigkeits-JARs im Chat oder im Repository.

---

**Nächste Schritte:** Für weitere Ziele die Originalpfade ermitteln; mehrere PNGs hinzufügen; Vorher-/Nachher-Test machen; erst dann veröffentlichen. Für Prioritäten, Mod-Patches und experimentelle JSON-Definitionen nutze den [technischen API-Leitfaden](API.md).
