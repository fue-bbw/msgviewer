from __future__ import annotations

import argparse
import threading
from pathlib import Path
from typing import Callable, Optional, Sequence

from .converter import FORMATS, convert, save_attachments
from .message import MessageSummary

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
except ImportError:
    tk = None
    filedialog = messagebox = ttk = None


def _require_tk() -> None:
    if tk is None:
        raise RuntimeError(
            "Tkinter ist nicht verfügbar. Unter Linux bitte das Paket python3-tk installieren."
        )


class MsgViewerApp:
    def __init__(self) -> None:
        _require_tk()
        self.root = tk.Tk()
        self.root.title("MsgViewer")
        self.root.minsize(760, 620)
        self.summary: Optional[MessageSummary] = None
        self.path_var = tk.StringVar()
        self.subject_var = tk.StringVar()
        self.sender_var = tk.StringVar()
        self.to_var = tk.StringVar()
        self.cc_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Bitte .msg-Datei auswählen.")
        self.format_var = tk.StringVar(value=FORMATS[0])
        self._build_widgets()

    def _build_widgets(self) -> None:
        top = ttk.Frame(self.root, padding=8)
        top.pack(fill="x")
        ttk.Label(top, text="Datei:").pack(side="left")
        ttk.Entry(top, textvariable=self.path_var).pack(side="left", fill="x", expand=True, padx=4)
        ttk.Button(top, text="Durchsuchen…", command=self._browse_file).pack(side="left", padx=2)
        self.open_button = ttk.Button(top, text="Öffnen", command=self.load_message)
        self.open_button.pack(side="left", padx=2)

        info = ttk.LabelFrame(self.root, text="Kopfdaten", padding=8)
        info.pack(fill="x", padx=8, pady=4)
        rows = [
            ("Betreff:", self.subject_var),
            ("Von:", self.sender_var),
            ("An:", self.to_var),
            ("Cc:", self.cc_var),
            ("Datum:", self.date_var),
        ]
        for i, (label, var) in enumerate(rows):
            ttk.Label(info, text=label).grid(row=i, column=0, sticky="w")
            ttk.Label(info, textvariable=var).grid(row=i, column=1, sticky="w", padx=4)

        middle = ttk.Frame(self.root, padding=8)
        middle.pack(fill="both", expand=True, padx=8)
        att_frame = ttk.LabelFrame(middle, text="Anhänge", padding=4, width=280)
        att_frame.pack(side="left", fill="y", padx=(0, 6))
        att_frame.pack_propagate(False)
        self.att_list = tk.Listbox(att_frame)
        self.att_list.pack(fill="both", expand=True)
        self.att_button = ttk.Button(
            att_frame, text="Anhänge speichern…", command=self.save_attachments, state="disabled"
        )
        self.att_button.pack(fill="x", pady=4)

        body_frame = ttk.LabelFrame(middle, text="Nachrichtentext", padding=4)
        body_frame.pack(side="left", fill="both", expand=True)
        self.body_text = tk.Text(body_frame, wrap="word", state="disabled")
        scroll = ttk.Scrollbar(body_frame, command=self.body_text.yview)
        self.body_text.configure(yscrollcommand=scroll.set)
        self.body_text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        conv = ttk.LabelFrame(self.root, text="Umwandeln", padding=8)
        conv.pack(fill="x", padx=8, pady=4)
        ttk.Label(conv, text="Zielformat:").pack(side="left")
        ttk.Combobox(
            conv, textvariable=self.format_var, values=list(FORMATS), state="readonly", width=8
        ).pack(side="left", padx=4)
        self.convert_button = ttk.Button(
            conv, text="Umwandeln und speichern…", command=self.convert_message, state="disabled"
        )
        self.convert_button.pack(side="left", padx=4)

        ttk.Label(self.root, textvariable=self.status_var, anchor="w", padding=(8, 4)).pack(
            fill="x", side="bottom"
        )

    def _browse_file(self) -> None:
        path = filedialog.askopenfilename(
            filetypes=[("Outlook-Nachrichten", "*.msg"), ("Alle Dateien", "*.*")]
        )
        if path:
            self.path_var.set(path)

    def _set_busy(self, busy: bool) -> None:
        state = "disabled" if busy else "normal"
        self.open_button.configure(state=state)
        if self.summary is not None:
            self.att_button.configure(state=state)
            self.convert_button.configure(state=state)

    def _run_async(self, work: Callable[[], object], done: Callable[[object], None]) -> None:
        self._set_busy(True)

        def runner() -> None:
            try:
                result = work()
            except Exception as exc:
                self.root.after(0, lambda: self._on_error(exc))
            else:
                self.root.after(0, lambda: done(result))

        threading.Thread(target=runner, daemon=True).start()

    def _on_error(self, exc: Exception) -> None:
        self._set_busy(False)
        self.status_var.set(f"Fehler: {exc}")
        messagebox.showerror("Fehler", str(exc))

    def load_message(self) -> None:
        path = self.path_var.get().strip()
        if not path:
            self.status_var.set("Bitte zuerst eine .msg-Datei auswählen.")
            return
        self._run_async(lambda: MessageSummary.from_file(path), self._on_loaded)

    def _on_loaded(self, summary: MessageSummary) -> None:
        self.summary = summary
        self.subject_var.set(summary.subject)
        self.sender_var.set(summary.sender)
        self.to_var.set(summary.to)
        self.cc_var.set(summary.cc)
        self.date_var.set(str(summary.date) if summary.date else "")
        self.att_list.delete(0, "end")
        for att in summary.attachments:
            self.att_list.insert("end", f"{att.filename} – {att.size} Bytes ({att.mimetype})")
        self.body_text.configure(state="normal")
        self.body_text.delete("1.0", "end")
        self.body_text.insert("1.0", summary.body)
        self.body_text.configure(state="disabled")
        self.att_button.configure(state="normal")
        self.convert_button.configure(state="normal")
        self._set_busy(False)
        name = Path(self.path_var.get()).name
        self.status_var.set(f"Geladen: {name} ({len(summary.attachments)} Anhänge)")

    def save_attachments(self) -> None:
        if self.summary is None:
            return
        directory = filedialog.askdirectory(title="Verzeichnis für Anhänge wählen")
        if not directory:
            return
        summary = self.summary

        def done(written) -> None:
            self._set_busy(False)
            self.status_var.set(f"{len(written)} Anhang/Anhänge gespeichert nach {directory}")
            messagebox.showinfo("Anhänge gespeichert", f"{len(written)} Datei(en) gespeichert:\n{directory}")

        self._run_async(lambda: save_attachments(summary, directory), done)

    def convert_message(self) -> None:
        if self.summary is None:
            return
        fmt = self.format_var.get()
        default_name = Path(self.path_var.get()).stem + f".{fmt}"
        target = filedialog.asksaveasfilename(
            title="Zieldatei wählen",
            defaultextension=f".{fmt}",
            initialfile=default_name,
            filetypes=[(f"{fmt.upper()}-Datei", f"*.{fmt}"), ("Alle Dateien", "*.*")],
        )
        if not target:
            return
        summary = self.summary

        def work() -> Path:
            result = convert(summary, fmt)
            out = Path(target)
            if isinstance(result, bytes):
                out.write_bytes(result)
            else:
                out.write_text(result, encoding="utf-8")
            return out

        def done(out: Path) -> None:
            self._set_busy(False)
            self.status_var.set(f"Umgewandelt ({fmt}) nach: {out}")
            messagebox.showinfo("Umwandlung fertig", f"Gespeichert: {out}")

        self._run_async(work, done)

    def run(self) -> None:
        self.root.mainloop()


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="msgviewer-gui",
        description="Grafische Oberfläche für MsgViewer und Umwandler (.msg-Dateien).",
    )
    parser.add_argument(
        "msg", nargs="?", type=Path, default=None, help="Optional: .msg-Datei, die direkt geöffnet wird"
    )
    args = parser.parse_args(argv)
    app = MsgViewerApp()
    if args.msg is not None:
        app.path_var.set(str(args.msg))
        app.load_message()
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
