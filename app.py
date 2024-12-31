from pathlib import Path
from typing import Iterable, List
import vlc
import utils

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Static, ProgressBar, ListView, ListItem, Label

# ---------- Widgets ----------
class FolderItem(ListItem):
  '''Widget for a folder in the library.'''
  def __init__(self, path: Path, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.path = path

class FolderTree(ListView):
  '''Widget for the folder tree in the library.'''
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
  '''Widget for the list of tracks in the library.'''
  tracks: List[Path] = reactive([])

  def __init__(self, title: str = "", tracks: List[Path] = [], *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.border_title = title
    self.tracks = tracks

  def watch_tracks(self, tracks: List[Path]) -> None:
    self.clear()
    self.refresh()
    for i, path in enumerate(tracks, 1):
      self.append(Track(path))

  def on_list_view_selected(self, message: ListView.Selected) -> None:
    message.item.play()

class Track(ListItem):
  '''Widget for a track in the library.'''
  def __init__(self, path: Path, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.path = path

  def play(self) -> None:
    print(f"Playing: {self.path.name}")
    self.app.play_song(self.path)

  def compose(self) -> ComposeResult:
    yield Label(self.path.name.removesuffix(self.path.suffix))

class PlayBar(Static):
  '''Widget for the play bar at the bottom of the screen.'''
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
  '''Screen for the library view.'''
  BINDINGS = [
    Binding("a", "add_to_queue", "add to queue"),
    Binding("p", "play_next", "play next"),
  ]

  tracks: List[Path] = reactive([])

  def compose(self) -> ComposeResult:
    yield Footer()

    with Static(classes="main"):
      yield FolderTree("[b]directory[/b]", "/Users/leo/Music")
      yield Tracks("[b]tracks[/b]", self.tracks)

    yield PlayBar()

  def update_tracks(self, path: str = "/Users/leo/Music/🌃 future funky city/"):
    '''Update the tracks list with the files in the given path.'''
    self.tracks = list(Path(path).iterdir())
    self.query_one(Tracks).tracks = self.tracks

  def on_list_view_highlighted(self, message: ListView.Highlighted) -> None:
    if message.list_view is self.query_one(FolderTree):
      print(f"Highlighted: {message.item.path}")
      self.update_tracks(message.item.path)

  def action_add_to_queue(self):
    '''Add the selected song to the end of the queue.'''
    self.notify("added to end of queue")

  def action_play_next(self):
    '''Play the selected song next.'''
    self.notify("playing next")


# ---------- Now Playing Screen ----------

class NowPlayingScreen(Screen):
  '''Screen for the now playing view.'''

  def compose(self) -> ComposeResult:
    yield Footer()

    with Static(classes="main"):
      with NowPlaying("[b]now playing[/b]", classes="box"):
        yield ListItem(Label("Priestess"))
        yield ListItem(Label("Aggressive Phonk"))
        yield ListItem(Label("2:02"))

    yield PlayBar()


# ---------- Main App ----------

class LollipopApp(App):
  '''Main application class for Lollipop.'''

  CSS_PATH = "style.tcss"
  MODES = {
    "library": LibraryScreen,
    "now_playing": NowPlayingScreen,
  }
  BINDINGS = [
    Binding("1", "switch_mode('library')", "library", show=False),
    Binding("2", "switch_mode('now_playing')", "now playing", show=False),

    Binding("left,j", "seek(-5)", "seek backwards", show=False),
    Binding("right,l", "seek(5)", "seek forwards", show=False),
    Binding("space,k", "toggle_pause", "toggle pause", show=False),
  ]

  def on_mount(self) -> None:
    self.theme = "gruvbox"
    self.title = "lollipop"
    self.switch_mode("library")

    self.player = vlc.MediaPlayer()
    self.player.audio_set_volume(50)

  def play_song(self, path: Path):
    '''Play a song from a given path.'''
    self.player.stop()
    media = vlc.Media(path)
    self.player.set_media(media)
    self.player.play()

  def action_seek(self, time: float):
    '''Seek forwards or backwards by a given time.'''
    self.query_one(ProgressBar).advance(time)
    current_time = self.player.get_time()
    self.player.set_time(utils.clamp(current_time + time * 1000, 0, self.player.get_length()))

  def action_toggle_pause(self):
    '''Toggle between play and pause.'''
    if self.player.is_playing():
      self.player.pause()
    else:
      self.player.play()


if __name__ == "__main__":
  app = LollipopApp()
  app.run()
