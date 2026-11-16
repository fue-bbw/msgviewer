# msgviewer

MsgViewer- und Umwandler-Tool für Outlook-`.msg`-Dateien. Es liest `.msg`-Dateien
mithilfe von [extract-msg](https://github.com/TeamMsgExtractor/msg-extractor) und kann sie
anzeigen oder in andere Formate umwandeln.

## Installation

```bash
pip install .
```

## Verwendung

### MsgViewer – .msg-Datei anzeigen

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
