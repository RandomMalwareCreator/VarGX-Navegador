import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget,
    QToolBar, QAction, QLineEdit, QInputDialog, QDialog, QLabel,
    QPushButton, QLineEdit as QLEdit, QVBoxLayout
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile
from PyQt5.QtCore import QUrl

# ========================== ABA DE NAVEGAÇÃO ==========================

class AbaNavegador(QWidget):
    def __init__(self, url):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.browser = QWebEngineView()

        # Desabilitar o cache globalmente para este QWebEngineView
        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpCacheType(QWebEngineProfile.NoCache)  # Desabilita o cache

        self.browser.setUrl(QUrl(url))
        self.layout.addWidget(self.browser)
        self.setLayout(self.layout)

    def navegar(self, url):
        if not url.startswith("http"):
            url = "http://" + url
        self.browser.setUrl(QUrl(url))

    def url_atual(self):
        return self.browser.url().toString()

# ========================== JANELA DE CONFIGURAÇÕES ==========================

class JanelaConfiguracoes(QDialog):
    def __init__(self, navegador):
        super().__init__()
        self.setWindowTitle("⚙️ Configurações")
        self.setFixedSize(300, 200)
        self.navegador = navegador

        layout = QVBoxLayout()

        self.label_home = QLabel("Página Inicial:")
        self.input_home = QLEdit()
        self.input_home.setText(self.navegador.pagina_inicial)

        self.botao_salvar = QPushButton("Salvar Página Inicial")
        self.botao_salvar.clicked.connect(self.salvar_home)

        self.botao_tema_escuro = QPushButton("🌙 Tema Escuro")
        self.botao_tema_escuro.clicked.connect(self.navegador.modo_escuro)

        self.botao_tema_claro = QPushButton("☀️ Tema Claro")
        self.botao_tema_claro.clicked.connect(self.navegador.modo_claro)

        layout.addWidget(self.label_home)
        layout.addWidget(self.input_home)
        layout.addWidget(self.botao_salvar)
        layout.addWidget(self.botao_tema_escuro)
        layout.addWidget(self.botao_tema_claro)

        self.setLayout(layout)

    def salvar_home(self):
        nova_home = self.input_home.text()
        if nova_home:
            self.navegador.pagina_inicial = nova_home
            print("✅ Página inicial atualizada:", nova_home)

# ========================== NAVEGADOR PRINCIPAL ==========================

class Navegador(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VarGX Navegador")
        self.setGeometry(100, 100, 1200, 800)
        self.favoritos = []
        self.pagina_inicial = "https://www.google.com"

        self.barra = QToolBar()
        self.addToolBar(self.barra)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.ir_para_url)
        self.barra.addWidget(self.url_bar)

        self.barra.addAction("Nova Aba", self.nova_aba)
        self.barra.addAction("Favoritar ⭐", self.adicionar_favorito)
        self.barra.addAction("Favoritos 📚", self.mostrar_favoritos)
        self.barra.addAction("Configurações ⚙️", self.abrir_configuracoes)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.fechar_aba)
        self.setCentralWidget(self.tabs)

        self.nova_aba(self.pagina_inicial)

    def nova_aba(self, url=None):
        if not url:
            url = self.pagina_inicial
        nova = AbaNavegador(url)
        index = self.tabs.addTab(nova, "Nova Aba")
        self.tabs.setCurrentIndex(index)
        nova.browser.urlChanged.connect(lambda q: self.sync_url_bar(q, nova))

    def fechar_aba(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def sync_url_bar(self, qurl, aba):
        if aba == self.tabs.currentWidget():
            url = qurl.toString()
            self.url_bar.setText(url)
            self.tabs.setTabText(self.tabs.currentIndex(), url[:30])

    def ir_para_url(self):
        texto = self.url_bar.text()
        if '.' in texto or texto.startswith("http"):
            url = texto if texto.startswith("http") else f"http://{texto}"
        else:
            url = f"https://www.google.com/search?q={texto}"
        aba = self.tabs.currentWidget()
        aba.navegar(url)

    def adicionar_favorito(self):
        aba = self.tabs.currentWidget()
        url = aba.url_atual()
        self.favoritos.append(url)
        print("⭐ Adicionado aos favoritos:", url)

    def mostrar_favoritos(self):
        if not self.favoritos:
            print("📭 Nenhum favorito.")
            return
        url, ok = QInputDialog.getItem(self, "Favoritos", "Escolha um site:", self.favoritos, 0, False)
        if ok and url:
            self.nova_aba(url)

    def modo_escuro(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #2e2e2e; }
            QLineEdit { background-color: #444; color: white; border: none; padding: 5px; }
            QToolBar { background-color: #3c3c3c; color: white; }
            QTabBar::tab { background: #3c3c3c; color: white; padding: 5px; }
            QTabBar::tab:selected { background: #555; }
        """)

    def modo_claro(self):
        self.setStyleSheet("")

    def abrir_configuracoes(self):
        janela = JanelaConfiguracoes(self)
        janela.exec_()

# ========================== EXECUÇÃO ==========================

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        navegador = Navegador()
        navegador.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Erro crítico: {e}")
