import os
import tempfile

import networkx as nx
import plotly.graph_objects as go
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPlainTextEdit, QPushButton, QLabel,
    QMessageBox, QTableWidget, QTableWidgetItem,
    QFileDialog
)
from PySide6.QtWebEngineWidgets import QWebEngineView

from graph_manager import GraphManager
class SongTransitionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Song Transition Graph")
        self.graph_manager = GraphManager()
        self.showing_longest = False
        self._build_ui()
        self.update_graph_view()
        self.refresh_table()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # ── Song Inputs Row ───────────────────────────────────
        form_layout = QHBoxLayout()
        # From Title
        self.ft_input = QLineEdit()
        ft_box = QVBoxLayout()
        ft_box.addWidget(QLabel("From Title"))
        ft_box.addWidget(self.ft_input)
        form_layout.addLayout(ft_box)
        # From Artist
        self.fa_input = QLineEdit()
        fa_box = QVBoxLayout()
        fa_box.addWidget(QLabel("From Artist"))
        fa_box.addWidget(self.fa_input)
        form_layout.addLayout(fa_box)
        # To Title
        self.tt_input = QLineEdit()
        tt_box = QVBoxLayout()
        tt_box.addWidget(QLabel("To Title"))
        tt_box.addWidget(self.tt_input)
        form_layout.addLayout(tt_box)
        # To Artist
        self.ta_input = QLineEdit()
        ta_box = QVBoxLayout()
        ta_box.addWidget(QLabel("To Artist"))
        ta_box.addWidget(self.ta_input)
        form_layout.addLayout(ta_box)
        layout.addLayout(form_layout)

        # ── Transition Note Row ───────────────────────────────
        note_box = QVBoxLayout()
        note_box.addWidget(QLabel("Transition Note"))
        self.note_input = QPlainTextEdit()
        self.note_input.setPlaceholderText("Enter your transition note here…")
        self.note_input.setFixedHeight(100)
        note_box.addWidget(self.note_input)
        layout.addLayout(note_box)

        # Add button (no label needed above)
        add_btn = QPushButton("Add Transition")
        add_btn.clicked.connect(self.on_add)
        btn_box = QVBoxLayout()
        btn_box.addSpacing(16)  # align with text fields
        btn_box.addWidget(add_btn)
        form_layout.addLayout(btn_box)
        # ── Toggle & Export Buttons ───────────────────────────
        btns = QHBoxLayout()
        self.longest_btn = QPushButton("Show Longest Path")
        self.longest_btn.setCheckable(True)
        self.longest_btn.clicked.connect(self.toggle_longest)
        export_btn = QPushButton("Export Longest Path…")
        export_btn.clicked.connect(self.export_longest_path)
        btns.addWidget(self.longest_btn)
        btns.addWidget(export_btn)
        layout.addLayout(btns)

        # ── Graph View ────────────────────────────────────────
        self.graph_view = QWebEngineView()
        layout.addWidget(self.graph_view, stretch=3)

        # ── Table of All Transitions ─────────────────────────
        layout.addWidget(QLabel("All Stored Transitions:"))
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "From Artist", "From Title",
            "To Artist", "To Title", "Note"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table, stretch=2)

    def on_add(self):
        # read all four song fields
        fa = self.fa_input.text().strip()
        ft = self.ft_input.text().strip()
        ta = self.ta_input.text().strip()
        tt = self.tt_input.text().strip()
        # QPlainTextEdit → use toPlainText()
        note = self.note_input.toPlainText().strip()

        if not (fa and ft and ta and tt):
            QMessageBox.warning(self, "Input Error",
                                "Artist and Title are required for both songs.")
            return

        # persist and update graph
        self.graph_manager.add_transition(fa, ft, ta, tt, note)

        # clear inputs
        self.fa_input.clear()
        self.ft_input.clear()
        self.ta_input.clear()
        self.tt_input.clear()
        self.note_input.clear()

        # refresh UI
        self.refresh_table()
        # if we're in longest-path view, toggle it off so new edge shows
        if self.showing_longest:
            self.longest_btn.setChecked(False)
            self.showing_longest = False
            self.longest_btn.setText("Show Longest Path")
        # redraw graph
        self.update_graph_view()


    def refresh_table(self):
        rows = self.graph_manager.db.get_all_transitions()
        self.table.setRowCount(len(rows))
        for i, (rid, fa, ft, ta, tt, note) in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(rid)))
            self.table.setItem(i, 1, QTableWidgetItem(fa))
            self.table.setItem(i, 2, QTableWidgetItem(ft))
            self.table.setItem(i, 3, QTableWidgetItem(ta))
            self.table.setItem(i, 4, QTableWidgetItem(tt))
            self.table.setItem(i, 5, QTableWidgetItem(note or ""))

    def toggle_longest(self):
        self.showing_longest = self.longest_btn.isChecked()
        self.longest_btn.setText(
            "Hide Longest Path" if self.showing_longest else "Show Longest Path"
        )
        self.update_graph_view()

    def export_longest_path(self):
        path = self.graph_manager.get_longest_path()
        if not path:
            QMessageBox.information(self, "Export Longest Path",
                                    "No path found to export.")
            return

        G = self.graph_manager.get_graph()
        lines = [" → ".join(path), "", "Notes:"]
        for u, v in zip(path, path[1:]):
            n = G.edges[u, v].get('note', '(no note)')
            lines.append(f"{u} → {v}: {n}")
        content = "\n".join(lines)

        fname, _ = QFileDialog.getSaveFileName(
            self, "Save Longest Path as TXT", "longest_path.txt",
            "Text Files (*.txt)"
        )
        if fname:
            try:
                with open(fname, "w", encoding="utf-8") as f:
                    f.write(content)
                QMessageBox.information(self, "Export Successful",
                                        f"Saved to:\n{fname}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", str(e))

    def update_graph_view(self):
        G_full = self.graph_manager.get_graph()
        if self.showing_longest:
            path = self.graph_manager.get_longest_path()
            G = nx.DiGraph()
            nx.add_path(G, path)
            for u, v in zip(path, path[1:]):
                G.edges[u, v]['note'] = G_full.edges[u, v].get('note', '')
        else:
            G = G_full

        pos = nx.spring_layout(G, seed=42)

        # Edge trace with hover notes
        ex, ey, ht = [], [], []
        for u, v, d in G.edges(data=True):
            x0,y0 = pos[u]; x1,y1 = pos[v]
            ex += [x0, x1, None]; ey += [y0, y1, None]
            ht.append(f"{u} → {v}<br>{d.get('note','')}")

        edge_trace = go.Scatter(
            x=ex, y=ey,
            line=dict(
                width=2 if self.showing_longest else 1,
                color='#42a1f5' if self.showing_longest else '#888'
            ),
            hoverinfo='text', mode='lines', text=ht
        )

        # Node trace with artist–title labels
        nx_, ny_, lbls = [], [], []
        for n in G.nodes():
            x,y = pos[n]
            nx_.append(x); ny_.append(y); lbls.append(n)

        node_trace = go.Scatter(
            x=nx_, y=ny_,
            mode='markers+text',
            text=lbls, textposition='top center',
            hoverinfo='text',
            marker=dict(
                size=12 if self.showing_longest else 10,
                color='lightgreen' if self.showing_longest else 'skyblue'
            ),
            textfont=dict(color='white', size=12)
        )

        fig = go.Figure([edge_trace, node_trace], layout=go.Layout(
            showlegend=False, hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False)
        ))

        # Dark template + transparent bg
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        tmp = os.path.join(tempfile.gettempdir(), "graph.html")
        fig.write_html(tmp)
        self.graph_view.load(f"file://{tmp}")
