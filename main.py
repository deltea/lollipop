from pathlib import Path
from typing import Iterable

from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Static, ProgressBar, DirectoryTree, ListView, ListItem, Label

class Box(Static, can_focus=True):
  def __init__(self, title: str = "", *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.border_title = title

class FolderTree(ListView):
  path: str | Path

  def __init__(self, title: str = "", path: str = "", *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.border_title = title
    self.path = path

  def compose(self):
    for path in self.get_paths():
      yield ListItem(Label(path.name))

  def get_paths(self) -> Iterable[Path]:
    return self.filter_paths(Path(self.path).iterdir())

  def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
    return [path for path in paths if path.is_dir() and not path.name.startswith(".")]

class Tracks(ListView):
  def __init__(self, title: str = "", *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.border_title = title

class NowPlaying(Static):
  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)

class LollipopApp(App):
  CSS_PATH = "style.tcss"
  BINDINGS = [
    Binding("left,j", "seek(-5)", "Seek backwards", show=False),
    Binding("right,l", "seek(5)", "Seek forwards", show=False),
    Binding("space,k", "toggle_pause", "Toggle pause", show=False),
    Binding("a", "add_to_queue", "Add to queue"),
    Binding("s", "play_next", "Play next")
  ]

  tracks: Iterable[Path] = []

  def on_mount(self) -> None:
    self.theme = "gruvbox"
    self.title = "Lollipop"

  def compose(self) -> ComposeResult:
    self.tracks = self.update_tracks()

    # yield Header()
    yield Footer()

    with Static(classes="main"):
      # Replace the Static widgets with Box widgets
      # with Box("[b]Directory[/b]", classes="sidebar"):
      yield FolderTree("[b]Directory[/b]", "/Users/leo/Music", classes="sidebar")
      with Tracks("[b]Tracks[/b]", classes="tracks"):
        for path in self.tracks:
          yield ListItem(Label(path.name.removesuffix(path.suffix)))

      with NowPlaying(classes="playing"):
        with Static(classes="playing-info"):
          yield Label("[b]Priestess[/b]")
        with Static(classes="playing-bar"):
          yield Label("1:10")
          yield ProgressBar(total=100, show_eta=False, show_percentage=False)
          yield Label("2:02")
        with Static(classes="playing-controls"):
          yield Label("Shuffle")
          yield Label("Repeat")

  def update_tracks(self):
    return Path("/Users/leo/Music/😈 aggressive phonk/").iterdir()

  def action_seek(self, time: float):
    self.query_one(ProgressBar).advance(time)

  def action_toggle_pause(self):
    pass

  def action_add_to_queue(self):
    self.notify("Added to end of queue", )

  def action_play_next(self):
    self.notify("Playing next")

if __name__ == "__main__":
  app = LollipopApp()
  app.run()
