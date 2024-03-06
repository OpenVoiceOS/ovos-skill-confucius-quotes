from os.path import join, dirname

from ovos_workshop.decorators import intent_handler
from ovos_workshop.intents import IntentBuilder
from ovos_workshop.skills import OVOSSkill


class ConfuciusQuotesSkill(OVOSSkill):

    def show_confucius(self, caption):
        self.gui.show_image(join(dirname(__file__), "ui", "confucius.jpg"),
                            caption=caption,
                            fill='PreserveAspectFit')

    @intent_handler(
        IntentBuilder("ConfuciusQuote").require('confucius').require('quote'))
    def handle_quote(self, message):
        utterance = self.dialog_renderer.render("quote", {})
        self.show_confucius(utterance)
        self.speak(utterance, wait=True)
        self.gui.release()

    @intent_handler(
        IntentBuilder("ConfuciusLive").require('confucius').require(
            'when').require('live'))
    def handle_live(self, message):
        utterance = self.dialog_renderer.render("live", {})
        self.show_confucius(utterance)
        self.speak(utterance, wait=True)
        self.gui.release()

    @intent_handler(
        IntentBuilder("ConfuciusBirth").require('confucius').require('birth'))
    def handle_birth(self, message):
        utterance = self.dialog_renderer.render("birth", {})
        self.show_confucius(utterance)
        self.speak(utterance, wait=True)
        self.gui.release()

    @intent_handler(
        IntentBuilder("ConfuciusDeath").require('confucius').require('death'))
    def handle_death(self, message):
        utterance = self.dialog_renderer.render("death", {})
        self.show_confucius(utterance)
        self.speak(utterance, wait=True)
        self.gui.release()

    @intent_handler("who.intent")
    def handle_who(self, message):
        utterance = self.dialog_renderer.render("confucius", {})
        self.show_confucius(utterance)
        self.speak(utterance, wait=True)
        self.gui.release()
