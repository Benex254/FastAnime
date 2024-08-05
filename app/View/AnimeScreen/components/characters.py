from kivy.properties import ObjectProperty,ListProperty

from kivymd.uix.boxlayout import MDBoxLayout


class AnimeCharacter(MDBoxLayout):
    voice_actors = ObjectProperty({
        "name":"",
        "image":""
    })
    character = ObjectProperty({
        "name":"",
        "gender":"",
        "dateOfBirth":"",
        "image":"",
        "age":"",
        "description":""
    })


class AnimeCharacters(MDBoxLayout):
    container = ObjectProperty()
    characters = ListProperty()
    def on_characters(self,instance,characters):
        format_date = lambda date_:  f"{date_['day']}/{date_['month']}/{date_['year']}" if date_ else ""
        self.container.clear_widgets()
        for character_ in characters: # character (character,actor)
            character = character_[0]
            actors = character_[1]

            anime_character = AnimeCharacter()
            anime_character.character = {
                "name":character["name"]["full"],
                "gender":character["gender"],
                "dateOfBirth":format_date(character["dateOfBirth"]),
                "image":character["image"]["medium"],
                "age":character["age"],
                "description":character["description"]
            }
            anime_character.voice_actors = {
                "name":", ".join([actor["name"]["full"] for actor in actors])
            }

            # anime_character.voice_actor =
            self.container.add_widget(anime_character)

