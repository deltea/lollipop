from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Static, ProgressBar
from textual.containers import Horizontal, Vertical, Grid

class Box(Static):
  def __init__(self, title: str = "", *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.border_title = title

class LollipopApp(App):
  CSS_PATH = "style.tcss"
  BINDINGS = []

  def on_mount(self) -> None:
    self.theme = "gruvbox"
    self.title = "Lollipop"

  def compose(self) -> ComposeResult:
    # yield Header()
    yield Footer()

    with Static(classes="main"):
      # Replace the Static widgets with Box widgets
      yield Box("[b]Sidebar[/b]", classes="box sidebar")
      yield Box("[b]Library[/b]", classes="box library")
      yield Box("[b]Now Playing[/b]", classes="box playing")

if __name__ == "__main__":
  app = LollipopApp()
  app.run()
