# app/ui/themes.py

def sith_dark_stylesheet():
    return """
    QMainWindow, QWidget {
        background-color: #181818;
        color: #fafafa;
    }
    QLabel, QTreeWidget, QTabWidget, QListWidget {
        color: #fafafa;
        background: transparent;
    }
    QFrame {
        background-color: #181818;
    }
    QPushButton {
        background: #222;
        color: #FF1744;
        border: 1px solid #FF1744;
        border-radius: 8px;
        padding: 5px 14px;
    }
    QPushButton:hover, QPushButton:checked {
        background: #FF1744;
        color: #fff;
    }
    QTabWidget::pane {
        border-top: 2px solid #FF1744;
    }
    QTabBar::tab:selected {
        background: #FF1744;
        color: #fff;
    }
    QTabBar::tab:!selected {
        background: #181818;
        color: #FF1744;
    }
    QTreeWidget {
        border: none;
    }
    QTreeWidget::item:selected {
        background: #330000;
        color: #FF1744;
    }
    QListWidget {
        border: none;
    }
    QListWidget::item:selected {
        background: #FF1744;
        color: #fff;
    }
    /* Topbar and drawer */
    QWidget#topbar, QWidget#drawer_topbar_widget {
        background: #111;
        color: #FF1744;
    }
    """
