# msgviewer

MsgViewer- und Umwandler-Tool für Outlook-`.msg`-Dateien. Es liest `.msg`-Dateien
mithilfe von [extract-msg](https://github.com/TeamMsgExtractor/msg-extractor) und kann sie
anzeigen oder in andere Formate umwandeln.

## Installation

```bash
pip install .
```

## Verwendung

### Grafische Oberfläche (Bedienpanel)

```bash
msgviewer-gui                 # Bedienpanel starten
msgviewer-gui nachricht.msg   # Panel direkt mit einer .msg-Datei öffnen
```

Das Panel zeigt Kopfdaten, Anhänge und Nachrichtentext an und kann die Datei
umwandeln (eml/html/txt) sowie Anhänge in ein gewähltes Verzeichnis speichern.
Voraussetzung ist Python mit Tkinter (bei Windows/macOS inklusive; unter Linux z. B. `sudo apt install python3-tk`).

## MsgViewer – .msg-Datei anzeigen

```bash
msgviewer nachricht.msg            # Kopfzeilen, Anhänge und Text
msgviewer nachricht.msg --no-body  # ohne Nachrichtentext
msgviewer nachricht.msg --json     # maschinenlesbare Ausgabe
```

### Umwandler – .msg in ein anderes Format umwandeln

```bash
msgconvert nachricht.msg -f eml                  # als .eml (Standard)
msgconvert nachricht.msg -f html -o out.html     # als HTML
msgconvert nachricht.msg -f txt  -o out.txt      # als reiner Text
msgconvert nachricht.msg --attachments anhaenge/ # Anhänge zusätzlich speichern
```

Ohne `-o` wird die Zieldatei neben der `.msg`-Datei mit passender Endung geschrieben.

## Entwicklung

```bash
pip install -e .[test]
pytest
```
