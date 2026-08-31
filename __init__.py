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

    @intent_handler("ConfuciusLive.intent")
    def handle_live(self, message):
        utterance = self.dialog_renderer.render("live", {})
        self.show_confucius(utterance)
        self.speak(utterance, wait=True)
        self.gui.release()

    @intent_handler("ConfuciusBirth.intent")
    def handle_birth(self, message):
        utterance = self.dialog_renderer.render("birth", {})
        self.show_confucius(utterance)
        self.speak(utterance, wait=True)
        self.gui.release()

    @intent_handler("ConfuciusDeath.intent")
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
