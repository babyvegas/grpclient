import sys

from PySide6 import QtCore, QtGui, QtWidgets


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("grpclient")
        self.resize(1440, 900)
        self.setMinimumSize(1100, 700)
        self._build_ui()
        self._apply_theme()

    def _build_ui(self):
        root = QtWidgets.QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)

        outer_layout = QtWidgets.QVBoxLayout(root)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        outer_layout.addWidget(self._build_header())

        workspace = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        workspace.setHandleWidth(1)
        workspace.addWidget(self._build_sidebar())
        workspace.addWidget(self._build_request_view())
        workspace.setSizes([270, 1170])
        outer_layout.addWidget(workspace, 1)

        status = QtWidgets.QLabel("  READY   |   localhost:50051   |   gRPC")
        status.setObjectName("statusBar")
        outer_layout.addWidget(status)

    def _build_header(self):
        header = QtWidgets.QFrame()
        header.setObjectName("header")
        layout = QtWidgets.QHBoxLayout(header)
        layout.setContentsMargins(20, 14, 20, 14)

        brand = QtWidgets.QLabel("grpclient")
        brand.setObjectName("brand")
        layout.addWidget(brand)
        workspace_label = QtWidgets.QLabel("WORKSPACE  /  DEFAULT")
        workspace_label.setObjectName("eyebrow")
        layout.addWidget(workspace_label)
        layout.addStretch()

        for label, icon in [("New request", "+"), ("Import", "down")]:
            button = QtWidgets.QPushButton(f"{icon}  {label}")
            button.setObjectName("headerButton")
            layout.addWidget(button)

        settings = QtWidgets.QToolButton()
        settings.setText("settings")
        settings.setToolTip("Settings")
        settings.setObjectName("iconButton")
        layout.addWidget(settings)
        return header

    def _build_sidebar(self):
        sidebar = QtWidgets.QFrame()
        sidebar.setObjectName("sidebar")
        layout = QtWidgets.QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 18, 12, 14)
        layout.setSpacing(12)

        collection_row = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("COLLECTIONS")
        title.setObjectName("sectionLabel")
        collection_row.addWidget(title)
        collection_row.addStretch()
        add_button = QtWidgets.QToolButton()
        add_button.setText("+")
        add_button.setToolTip("Add collection")
        add_button.setObjectName("smallIconButton")
        collection_row.addWidget(add_button)
        layout.addLayout(collection_row)

        search = QtWidgets.QLineEdit()
        search.setPlaceholderText("Filter requests")
        search.setClearButtonEnabled(True)
        search.setObjectName("searchBox")
        layout.addWidget(search)

        tree = QtWidgets.QTreeWidget()
        tree.setObjectName("requestTree")
        tree.setHeaderHidden(True)
        tree.setIndentation(16)
        collection = QtWidgets.QTreeWidgetItem(["down  Greeter service"])
        tree.addTopLevelItem(collection)
        for method, name in [("GET", "List services"), ("RPC", "SayHello")]:
            item = QtWidgets.QTreeWidgetItem([f"{method:<5} {name}"])
            item.setData(0, QtCore.Qt.ItemDataRole.UserRole, name)
            collection.addChild(item)
        collection.setExpanded(True)
        tree.setCurrentItem(collection.child(1))
        layout.addWidget(tree, 1)

        environment = QtWidgets.QFrame()
        environment.setObjectName("environment")
        environment_layout = QtWidgets.QVBoxLayout(environment)
        environment_layout.setContentsMargins(12, 12, 12, 12)
        environment_layout.addWidget(QtWidgets.QLabel("ACTIVE ENVIRONMENT"))
        env_value = QtWidgets.QLabel("Local development")
        env_value.setObjectName("environmentValue")
        environment_layout.addWidget(env_value)
        layout.addWidget(environment)
        return sidebar

    def _build_request_view(self):
        panel = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(28, 24, 28, 20)
        layout.setSpacing(16)

        heading = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("SayHello")
        title.setObjectName("pageTitle")
        heading.addWidget(title)
        badge = QtWidgets.QLabel("RPC")
        badge.setObjectName("rpcBadge")
        heading.addWidget(badge)
        heading.addStretch()
        save = QtWidgets.QPushButton("Save")
        save.setObjectName("subtleButton")
        heading.addWidget(save)
        layout.addLayout(heading)

        address = QtWidgets.QFrame()
        address.setObjectName("addressBar")
        address_layout = QtWidgets.QHBoxLayout(address)
        address_layout.setContentsMargins(10, 8, 8, 8)
        method = QtWidgets.QComboBox()
        method.addItem("RPC")
        method.setObjectName("methodSelect")
        address_layout.addWidget(method)
        endpoint = QtWidgets.QLineEdit("localhost:50051 / helloworld.Greeter / SayHello")
        endpoint.setObjectName("endpointInput")
        address_layout.addWidget(endpoint, 1)
        send = QtWidgets.QPushButton("Send  >")
        send.setObjectName("sendButton")
        send.clicked.connect(self._send_request)
        address_layout.addWidget(send)
        layout.addWidget(address)

        tabs = QtWidgets.QTabWidget()
        tabs.setObjectName("requestTabs")
        tabs.addTab(self._editor('{\n  "name": "Donovan"\n}'), "Request body")
        tabs.addTab(self._editor("# optional metadata\n# authorization: Bearer $TOKEN"), "Metadata")
        layout.addWidget(tabs, 1)

        response_header = QtWidgets.QHBoxLayout()
        response_label = QtWidgets.QLabel("RESPONSE")
        response_label.setObjectName("sectionLabel")
        response_header.addWidget(response_label)
        response_header.addStretch()
        self.response_status = QtWidgets.QLabel("NOT SENT")
        self.response_status.setObjectName("responseStatus")
        response_header.addWidget(self.response_status)
        layout.addLayout(response_header)

        self.response_editor = self._editor("Send the request to inspect the response.")
        self.response_editor.setReadOnly(True)
        self.response_editor.setMinimumHeight(180)
        layout.addWidget(self.response_editor, 1)
        return panel

    @staticmethod
    def _editor(text):
        editor = QtWidgets.QPlainTextEdit(text)
        editor.setObjectName("codeEditor")
        editor.setTabStopDistance(4 * QtGui.QFontMetrics(editor.font()).horizontalAdvance(" "))
        return editor

    def _send_request(self):
        self.response_status.setText("READY TO CONNECT")
        self.response_editor.setPlainText("Connection ready.\n\nThe gRPC transport layer will be connected here.")

    def _apply_theme(self):
        self.setStyleSheet("""
            QWidget { color: #d8e0e7; font-family: 'Bahnschrift'; font-size: 13px; }
            #root { background: #10161b; }
            #header { background: #172027; border-bottom: 1px solid #2b3942; }
            #brand { color: #f2f6f8; font-size: 22px; font-weight: 700; letter-spacing: 1px; }
            #eyebrow, #sectionLabel { color: #71818c; font-size: 10px; font-weight: 700; letter-spacing: 1.2px; }
            #headerButton, #subtleButton { background: transparent; border: 1px solid #33434d; color: #b9c6ce; padding: 8px 12px; border-radius: 4px; }
            #headerButton:hover, #subtleButton:hover { border-color: #5fbe9b; color: #e3fff4; }
            #iconButton, #smallIconButton { background: transparent; border: none; color: #8fa0aa; font-size: 14px; }
            #sidebar { background: #121a20; border-right: 1px solid #2b3942; }
            #searchBox, #endpointInput { background: #0d1317; border: 1px solid #2d3b44; border-radius: 4px; padding: 8px; color: #dce6eb; }
            #searchBox:focus, #endpointInput:focus { border-color: #5fbe9b; }
            #requestTree { background: transparent; border: none; outline: none; }
            #requestTree::item { padding: 8px 4px; border-radius: 3px; }
            #requestTree::item:selected { background: #263d3a; color: #b9f4d8; }
            #environment { background: #19252b; border: 1px solid #2d3d45; border-radius: 5px; color: #83949e; }
            #environmentValue { color: #d3e6df; }
            #pageTitle { color: #eff5f6; font-size: 24px; font-weight: 700; }
            #rpcBadge { background: #23483e; color: #85e0b8; padding: 4px 8px; border-radius: 3px; font-size: 10px; font-weight: 700; }
            #addressBar { background: #172027; border: 1px solid #2d3d45; border-radius: 5px; }
            #methodSelect { background: #20342f; border: none; color: #8fe0bb; font-weight: 700; padding: 8px; }
            #sendButton { background: #5fbe9b; border: none; color: #0b1714; font-weight: 700; padding: 9px 18px; border-radius: 4px; }
            #sendButton:hover { background: #7bd6b1; }
            #requestTabs::pane { border: 1px solid #2d3d45; border-radius: 4px; background: #0d1317; }
            #requestTabs::tab { background: transparent; color: #778892; padding: 9px 14px; border-bottom: 2px solid transparent; }
            #requestTabs::tab:selected { color: #b9f4d8; border-bottom-color: #5fbe9b; }
            #codeEditor { background: #0d1317; border: 1px solid #2d3d45; border-radius: 4px; color: #b9c8ce; font-family: 'Cascadia Code'; font-size: 13px; padding: 10px; }
            #responseStatus { color: #e5b66f; font-size: 10px; font-weight: 700; letter-spacing: 1px; }
            #statusBar { background: #0c1115; color: #60727d; font-size: 10px; padding: 7px; letter-spacing: 1px; }
            QScrollBar:vertical { background: #10161b; width: 8px; }
            QScrollBar::handle:vertical { background: #34454e; border-radius: 4px; }
        """)


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("grpclient")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()