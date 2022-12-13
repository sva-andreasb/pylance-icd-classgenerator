## How To Use

### Umzug
Umgezogen nach [GitHub](https://github.com/sva-andreasb/pylance-icd-classgenerator), um den Code auch aus Kundenumgebungen zu erreichen. Die Klassen sind ebenfalls bei [GitHub](https://github.com/sva-andreasb/pylance-icd-classes) zu finden.

### VSCode Extension
Diese Klassendateien sind für die VSCode-Extension [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance) gedacht. Sie sollen die angezeigten Fehler reduzieren, wenn TPAE Klassen importiert werden. Aktuell enthalten die Klassen keinerlei Funktionen und sind nur leere Dateien, so dass lediglich die angezeigten Import-Fehler behoben werden. Ob eine Code-Completion möglich ist, werde ich in Zukunft eruieren.

#### Vorher
![Vorher](/media/before.png)
#### Nachher
![Nachher](/media/after.png)

#### Einbindung
Um die Klassen zu Nutzen, muss der \<RepositoryPfad\>/classes in den Einstellungen der Extension hinterlegt werden.

![Einbindung](/media/settings.png)

#### Generierung
Um die Klassen zu generieren, muss in der Datei "GenerateICDClasses.py" die Variable icdLocation auf den InstallationsPfad einer ICD-Instanz gesetzt werden und das Script als normales Python-Script ausgeführt werden.
