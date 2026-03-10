import os

from ovos_workshop.decorators import intent_handler
from ovos_workshop.intents import IntentBuilder
from ovos_workshop.skills import OVOSSkill


class ConfuciusQuotesSkill(OVOSSkill):

    def show_confucius(self, caption):
        img = os.path.join(self.root_dir, "gui", "all", "confucius.jpg")
        self.gui.show_image(img,
                            caption=caption,
                            override_idle=10,
                            override_animations=True,
                            fill='PreserveAspectFit')

    def _speak_and_show(self, dialog):
        utterance = self.dialog_renderer.render(dialog, {})
        self.show_confucius(utterance)
        self.speak(utterance, wait=True,
                   meta={"dialog": dialog, "data": {}, "skill": self.skill_id})
        self.gui.release()

    @intent_handler(IntentBuilder("ConfuciusQuote").require('confucius').require('quote'))
    def handle_quote(self, message):
        self._speak_and_show("quote")

    @intent_handler(IntentBuilder("ConfuciusLive").require('confucius').require('when').require('live'))
    def handle_live(self, message):
        self._speak_and_show("live")

    @intent_handler(IntentBuilder("ConfuciusBirth").require('confucius').require('birth'))
    def handle_birth(self, message):
        self._speak_and_show("birth")

    @intent_handler(IntentBuilder("ConfuciusDeath").require('confucius').require('death'))
    def handle_death(self, message):
        self._speak_and_show("death")

    @intent_handler("who.intent")
    def handle_who(self, message):
        self._speak_and_show("confucius")
