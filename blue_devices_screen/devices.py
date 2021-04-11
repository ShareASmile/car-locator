from kivymd.uix.screen import MDScreen
from kivymd.uix.list import OneLineListItem
from kivymd.uix.list import MDList
from kivymd.uix.toolbar import MDToolbar
from kivymd.app import MDApp
from kivymd.toast import toast
from kivy.utils import platform
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock


if platform == 'android':
    from jnius import autoclass

    BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
    BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
    Intent = autoclass('android.content.Intent')
    mActivity = autoclass('org.kivy.android.PythonActivity').mActivity


class BlueDevicesScreen(MDScreen):
    def __init__(self, **kw):
        self.devices = []
        self.list_of_devices = None
        if platform == 'android':
            self.bluetoothAdapter = BluetoothAdapter.getDefaultAdapter()
            if not self.bluetoothAdapter:
                toast("This device doesn't support bluetooth", 80, True)
        else:
            self.bluetoothAdapter = None
        Clock.schedule_once(self.post_init, 0)
        super().__init__(**kw)

    def post_init(self, dt):

        scroll = ScrollView()
        self.list_of_devices = MDList()
        scroll.add_widget(self.list_of_devices)
        box = BoxLayout()
        box.add_widget(scroll)

        self.container = BoxLayout(orientation='vertical')
        toolbar = MDToolbar(pos_hint={'top': 1})
        toolbar.left_action_items = [
            'chevron-left', lambda x: self.switch_screen()]
        self.container.add_widget(toolbar)
        self.container.add_widget(box)

        self.add_widget(self.container)

    def enable_bluetooth(self):
        enableAdapter = Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE)
        mActivity.startActivityForResult(enableAdapter, 0)

    def on_enter(self, *args):
        if self.bluetoothAdapter:
            if not self.bluetoothAdapter.isEnabled():
                self.enable_bluetooth()
            self.get_bluetooth_devices()
        return super().on_enter(*args)

    def on_leave(self, *args):
        self.devices = []
        self.list_of_devices.clear_widgets()
        Clock.schedule_once(MDApp.get_running_app().save_theme, 0)
        return super().on_leave(*args)

    def get_bluetooth_devices(self):

        if self.bluetoothAdapter:
            if self.bluetoothAdapter.isEnabled():
                results = self.bluetoothAdapter.getBondedDevices()
                self.devices = results.toArray()

                for device in self.devices:
                    name = OneLineListItem(text=device.getName())
                    name.bind(on_release=self.save_device_name)
                    self.list_of_devices.add_widget(name)
            else:
                self.enable_bluetooth()

    def save_device_name(self, widget):
        app = MDApp.get_running_app()
        app.paired_car = widget.text
        app.root.ids.content_drawer.ids.md_list.children[0].text = widget.text
        toast(f'{widget.text} is choosen to be listen for', True, 80)

    def switch_screen(self):
        MDApp.get_running_app().root.ids.sm.current = 'scr 1'
