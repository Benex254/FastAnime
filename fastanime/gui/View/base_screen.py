from kivy.properties import ObjectProperty, StringProperty
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.navigationrail import MDNavigationRail, MDNavigationRailItem
from kivymd.uix.screen import MDScreen
from kivymd.uix.tooltip import MDTooltip

from ...Utility.observer import Observer


class NavRail(MDNavigationRail):
    screen = ObjectProperty()


class SearchBar(MDBoxLayout):
    screen = ObjectProperty()


class Tooltip(MDTooltip):
    pass


class TooltipMDIconButton(Tooltip, MDIconButton):
    tooltip_text = StringProperty()


class CommonNavigationRailItem(MDNavigationRailItem):
    icon = StringProperty()
    text = StringProperty()


class HeaderLabel(MDBoxLayout):
    text = StringProperty()
    halign = StringProperty("left")


class BaseScreenView(MDScreen, Observer):
    """
    A base class that implements a visual representation of the model data.
    The view class must be inherited from this class.
    """

    controller = ObjectProperty()
    """
    Controller object - :class:`~Controller.controller_screen.ClassScreenControler`.

    :attr:`controller` is an :class:`~kivy.properties.ObjectProperty`
    and defaults to `None`.
    """

    model = ObjectProperty()
    """
    Model object - :class:`~Model.model_screen.ClassScreenModel`.

    :attr:`model` is an :class:`~kivy.properties.ObjectProperty`
    and defaults to `None`.
    """

    manager_screens = ObjectProperty()
    """
    Screen manager object - :class:`~kivymd.uix.screenmanager.MDScreenManager`.

    :attr:`manager_screens` is an :class:`~kivy.properties.ObjectProperty`
    and defaults to `None`.
    """

    def __init__(self, **kw):
        super().__init__(**kw)
        # Often you need to get access to the application object from the view
        # class. You can do this using this attribute.
        from ...gui import FastAnime

        self.app: FastAnime = MDApp.get_running_app()  # type: ignore
        # Adding a view class as observer.
        self.model.add_observer(self)
