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
