# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import uuid

# (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.
import octoprint.plugin

userId = str(uuid.uuid1())[:8]


class MQTTControlPlugin(
    octoprint.plugin.EventHandlerPlugin,
    octoprint.plugin.SimpleApiPlugin,
    octoprint.plugin.StartupPlugin):
    baseTopic = None
    topicPrefix = "plugin/mqtt_control"

    def __init__(self):
        self.mqtt_publish = lambda *args, **kwargs: None
        self.mqtt_subscribe = lambda *args, **kwargs: None
        self.mqtt_unsubscribe = lambda *args, **kwargs: None
 

    def on_after_startup(self):

        helpers = self._plugin_manager.get_helpers("mqtt", "mqtt_publish", "mqtt_subscribe", "mqtt_unsubscribe")
        if helpers:
            if 'mqtt_publish' in helpers:
                self.mqtt_publish = helpers['mqtt_publish']
            if 'mqtt_subscribe' in helpers:
                self.mqtt_subscribe = helpers['mqtt_subscribe']
            if 'mqtt_unsubscribe' in helpers:
                self.mqtt_unsubscribe = helpers['mqtt_unsubscribe']

            if 'mqtt' in self._plugin_manager.enabled_plugins:
                mqttPlugin = self._plugin_manager.plugins['mqtt'].implementation
                if mqttPlugin:
                    self.baseTopic = mqttPlugin._settings.get(['publish', 'baseTopic'])

        if self.baseTopic:
            self._logger.info('Enable MQTT')
            self.mqtt_subscribe('%s%s' % (self.baseTopic, '%s/#' % self.topicPrefix), self.on_mqtt_sub)
 
    def on_mqtt_sub(self, topic, message, retain=None, qos=None, *args, **kwargs):
        self._logger.debug("Receive mqtt message %s" % (topic))
        if self.baseTopic is None:
            return

        # if topic == '%s%s%s' % (self.baseTopic, self.baseTopic, 'env'):
        #     payload = json.loads(message)
      


    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://github.com/foosel/OctoPrint/wiki/Plugin:-Software-Update
        # for details.
        return dict(
            mqtt_control=dict(
                displayName="MQTT Control",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="ralmn",
                repo="OctoPrint-MQTT-Control",
                current=self._plugin_version,
                prerelease_branches=["develop"],
                prerelease=True,

                # update method: pip
                pip="https://github.com/ralmn/OctoPrint-MQTT-Control/archive/{target_version}.zip"
            )
        )


__plugin_name__ = "OctoPrint MQTT Control"
__plugin_pythoncompat__ = ">=3,<4"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = MQTTControlPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
