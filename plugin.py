from appdirs import *
import codecs
import json
import asyncio
import socketio
import uuid
from youdao_word_api import YoudaoAPI
import pyperclip
import sys

APP_NAME = "electron-spirit"
PLUGIN_NAME = "ES Youdao Word"
SHORT_NAME = "ydword"
PLUGIN_SETTING = "plugin.setting.json"
DEFAULT_CONFIG = {"appid": "", "appkey": "", "clipboard": True}


class PluginApi(socketio.AsyncClientNamespace):
    def __init__(self, parent):
        super().__init__()
        self.elem_count = 0
        self.parent = parent

    def on_connect(self):
        print("Connected")

    def on_disconnect(self):
        print("Disconnected")
        sys.exit(0)

    def on_echo(self, data):
        print("Echo:", data)

    def on_addInputHook(self, data):
        print("Add input hook:", data)

    def on_delInputHook(self, data):
        print("Del input hook:", data)

    def on_insertCSS(self, data):
        print("Insert css:", data)

    def on_removeCSS(self, data):
        print("Remove css:", data)

    def on_addElem(self, data):
        print("Add elem:", data)
        self.elem_count += 1

    def on_delElem(self, data):
        print("Remove elem:", data)
        self.elem_count -= 1

    def on_showElem(self, data):
        print("Show view:", data)

    def on_hideElem(self, data):
        print("Hide view:", data)

    def on_setBound(self, data):
        print("Set bound:", data)

    def on_setContent(self, data):
        print("Set content:", data)

    def on_setOpacity(self, data):
        print("Set opacity:", data)

    def on_execJSInElem(self, data):
        print("Exec js in elem:", data)

    def on_notify(self, data):
        print("Notify:", data)

    def on_updateBound(self, key, bound):
        print("Update bound:", key, bound)

    def on_updateOpacity(self, key, opacity):
        print("Update opacity:", key, opacity)

    async def on_processContent(self, content):
        print("Process content:", content)
        await self.parent.trans(content)

    def on_modeFlag(self, flags):
        print("Mode flag:", flags)

    def on_elemRemove(self, key):
        print("Elem remove:", key)
        # prevent remove elem
        return True

    def on_elemRefresh(self, key):
        print("Elem refresh:", key)
        # prevent refresh elem
        return True


class Plugin(object):
    def __init__(self) -> None:
        self.load_config()
        if self.cfg["appid"] == "" or self.cfg["appkey"] == "":
            raise Exception(f"Please set appid and appkey in {PLUGIN_SETTING}")
        self.fanyi_api = YoudaoAPI(self.cfg["appid"], self.cfg["appkey"])
        self.api = PluginApi(self)

    async def trans(self, content):
        res = self.fanyi_api.get_basic(content)
        await sio.emit(
            "notify",
            data=(
                {"text": res, "title": PLUGIN_NAME, "duration": 3000 + len(res) * 100},
            ),
        )
        if self.cfg["clipboard"]:
            pyperclip.copy(res)
        print(res)

    def load_config(self):
        path = user_data_dir(APP_NAME, False, roaming=True)
        with codecs.open(path + "/api.json") as f:
            config = json.load(f)
        self.port = config["apiPort"]
        try:
            with codecs.open(PLUGIN_SETTING) as f:
                self.cfg = json.load(f)
            for k in DEFAULT_CONFIG:
                if k not in self.cfg or type(self.cfg[k]) != type(DEFAULT_CONFIG[k]):
                    self.cfg[k] = DEFAULT_CONFIG[k]
        except:
            self.cfg = DEFAULT_CONFIG
        self.save_cfg()

    def save_cfg(self):
        with codecs.open(PLUGIN_SETTING, "w") as f:
            json.dump(self.cfg, f)

    async def wait_for_elem(self):
        while self.api.elem_count < 2:
            await asyncio.sleep(0.1)

    async def test_case(self):
        await sio.emit("addInputHook", data=("yd"))
        await sio.emit(
            "notify",
            data=(
                {"text": "字典翻译已启动. 翻译结果将通过通知形式显示, 也可以复制到剪贴板中.", "title": PLUGIN_NAME}
            ),
        )

    async def loop(self):
        await sio.connect(f"http://localhost:{self.port}")
        await self.test_case()
        await sio.wait()


if __name__ == "__main__":
    # asyncio
    sio = socketio.AsyncClient()
    p = Plugin()
    sio.register_namespace(p.api)
    asyncio.run(p.loop())
