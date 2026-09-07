from ovos_workshop.decorators import intent_handler
from ovos_workshop.skills import OVOSSkill


class ConfuciusQuotesSkill(OVOSSkill):

    def show_confucius(self, caption):
        self.gui.show_image("confucius.jpg",
                            caption=caption,
                            override_idle=10,
                            override_animations=True,
                            fill='PreserveAspectFit')

    @intent_handler("ConfuciusQuote.intent")
    def handle_quote(self, message):
        utterance = self.dialog_renderer.render("quote", {})
        self.show_confucius(utterance)
        self.speak(utterance, wait=True)
        self.gui.release()

    @intent_handler("confucius_lifespan.intent")
    def handle_lifespan(self, message):
        utterance = self.dialog_renderer.render("lifespan", {})
        self.show_confucius(utterance)
        self.speak(utterance, wait=True)
        self.gui.release()

    @intent_handler("who.intent")
    def handle_who(self, message):
        utterance = self.dialog_renderer.render("confucius", {})
        self.show_confucius(utterance)
        self.speak(utterance, wait=True)
        self.gui.release()
