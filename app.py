from pathlib import Path
from typing import Iterable, List

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Static, ProgressBar, ListView, ListItem, Label
from textual.widget import Widget


# ---------- Widgets ----------
class FolderItem(ListItem):
  def __init__(self, path: Path, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.path = path


class FolderTree(ListView):
  def __init__(self, title: str = "", path: str = "", *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.border_title = title
    self.path = path

  def compose(self):
    for path in self.get_paths():
      yield FolderItem(path, Label(path.name))

  def get_paths(self) -> Iterable[Path]:
    return self.filter_paths(Path(self.path).iterdir())

  def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
    return [path for path in paths if path.is_dir() and not path.name.startswith(".")]

class Tracks(ListView):
  tracks: List[Path] = reactive([])

  def __init__(self, title: str = "", tracks: List[Path] = [], *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.border_title = title
    self.tracks = tracks

  def watch_tracks(self, tracks: List[Path]) -> None:
    self.clear()
    self.refresh()
    for i, path in enumerate(tracks, 1):
      self.append(ListItem(
        Label(path.name.removesuffix(path.suffix), classes="track-name"),
        classes="track"
      ))

class PlayBar(Static):
  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)

  def compose(self) -> ComposeResult:
    with Static(classes="playing-info"):
      yield Label("[b]Priestess[/b]")
    with Static(classes="playing-bar"):
      yield Label("1:10")
      yield ProgressBar(total=100, show_eta=False, show_percentage=False)
      yield Label("2:02")
    with Static(classes="playing-controls"):
      yield Label("shuffle")
      yield Label("repeat")


class NowPlaying(ListView):
  def __init__(self, title: str = "", *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.border_title = title


# ---------- Library Screen ----------

class LibraryScreen(Screen):
  BINDINGS = [
    Binding("left,j", "seek(-5)", "seek backwards", show=False),
    Binding("right,l", "seek(5)", "seek forwards", show=False),
    Binding("space,k", "toggle_pause", "toggle pause", show=False),

    Binding("a", "add_to_queue", "add to queue"),
    Binding("p", "play_next", "play next"),
  ]

  tracks: List[Path] = reactive([])

  def compose(self) -> ComposeResult:
    yield Footer()

    with Static(classes="main"):
      yield FolderTree("[b]directory[/b]", "/Users/leo/Music")
      yield Tracks("[b]tracks[/b]", self.tracks, classes="tracks")

      yield PlayBar()

  def update_tracks(self, path: str = "/Users/leo/Music/🌃 future funky city/"):
    self.tracks = list(Path(path).iterdir())
    self.query_one(Tracks).tracks = self.tracks
    print(self.tracks)

  def on_list_view_highlighted(self, message: ListView.Highlighted) -> None:
    if message.list_view is self.query_one(FolderTree):
      print(f"Highlighted: {message.item.path}")
      self.update_tracks(message.item.path)

  def action_seek(self, time: float):
    self.query_one(ProgressBar).advance(time)

  def action_toggle_pause(self):
    pass

  def action_add_to_queue(self):
    self.notify("added to end of queue")

  def action_play_next(self):
    self.notify("playing next")


# ---------- Now Playing Screen ----------

class NowPlayingScreen(Screen):
  def compose(self) -> ComposeResult:
    yield Footer()

    with Static(classes="now-playing"):
      with NowPlaying("[b]now playing[/b]", classes="box"):
        yield ListItem(Label("Priestess"))
        yield ListItem(Label("Aggressive Phonk"))
        yield ListItem(Label("2:02"))

      yield PlayBar()


# ---------- Main App ----------

class LollipopApp(App):
  CSS_PATH = "style.tcss"
  MODES = {
    "library": LibraryScreen,
    "now_playing": NowPlayingScreen,
  }
  BINDINGS = [
    Binding("1", "switch_mode('library')", "library", show=False),
    Binding("2", "switch_mode('now_playing')", "now playing", show=False),
  ]

  def on_mount(self) -> None:
    self.theme = "gruvbox"
    self.title = "lollipop"
    self.switch_mode("library")


if __name__ == "__main__":
  app = LollipopApp()
  app.run()
