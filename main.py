import subprocess, json, sys, argparse, platform
import xml.etree.ElementTree as ET
import xml.dom.minidom
# ===================== WINDOWS ONLY WARNING =====================
if platform.system() != "Windows":
    print("[ERROR] This utility only works on Windows (netsh required). Exiting.")
    sys.exit(1)
# ===============================================================

class wifi:
    def __init__(self):
        self.wifi_profiles = {"group_policy_profiles": {}, "user_profiles": {}}

    def run_cmd(self, cmd) -> list:
        return subprocess.check_output(cmd, shell=True).decode('utf-8').splitlines()

    def get_profiles(self) -> None:
        output = self.run_cmd("netsh wlan show profile")
        group = None
        for line in output:
            if "User profiles" in line:
                group = "user_profiles"
            elif "Group policy profiles (read only)" in line:
                group = "group_policy_profiles"
            if line.startswith("   ") and "<None>" not in line:
                ssid = line.strip()
                self.wifi_profiles[group][ssid] = {}
        return None
    
    def analyze(self) -> None:
        for group in self.wifi_profiles:
            for ssid in self.wifi_profiles[group]:
                cmd = f'netsh wlan show profile "{ssid}" key=clear'
                output = self.run_cmd(cmd)
                data = {}
                for i in output[8:]:
                    if ":" in i:
                        key, value = i.split(":", 1)
                        key = key.strip()
                        value = value.strip()
                        if key in data:
                            old_value = data[key]
                            if type(old_value) == list:
                                old_value.append(value)
                                data[key] = old_value
                            else:
                                data[key] = [old_value, value]
                        else:
                            data[key] = value
                self.wifi_profiles[group][ssid] = data
        return None
    
class export:
    def __init__(self, data:dict, export_path="export.json") -> None:
        self.data = data
        self.export_path = export_path
        self.func = {
            "json": self.export_json,
            "xml": self.export_xml
        }
        pth = self.export_path.split(".")[-1]
        if pth in self.func.keys():
            self.func[pth]()

    def export_json(self):
        with open(self.export_path, 'w') as file:
            json.dump(self.data, file, indent=4)

    def export_xml(self):
        def add_elements(parent, data):
            if isinstance(data, dict):
                for key, value in data.items():
                    safe_key = ''.join(c if c.isalnum() or c == '_' else '_' for c in key.replace(" ", "_"))
                    if safe_key and safe_key[0].isdigit():
                        safe_key = f"_{safe_key}"
                    elem = ET.SubElement(parent, safe_key)
                    add_elements(elem, value)
            elif isinstance(data, list):
                for item in data:
                    item_elem = ET.SubElement(parent, "item")
                    add_elements(item_elem, item)
            else:
                parent.text = str(data)

        root = ET.Element("export")
        for group, profiles in self.data.items():
            group_elem = ET.SubElement(root, group)
            for ssid, details in profiles.items():
                profile_elem = ET.SubElement(group_elem, "Profile", name=ssid)
                add_elements(profile_elem, details)

        xml_str = ET.tostring(root, encoding='utf-8')
        pretty_xml = xml.dom.minidom.parseString(xml_str).toprettyxml(indent="  ")
        with open(self.export_path, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Export WiFi profiles and passwords from Windows."
    )
    parser.add_argument(
        "-p", "--path",
        nargs="?",
        const="export.json",
        type=str,
        help="Export to a file. If used without a value, defaults to export.json. If a value is provided, uses that as the export path. Supports .json, .xml."
    )
    parser.add_argument("-t", "--terminal", action="store_true", help="Print output to terminal instead of exporting to a file.")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    wifi_util = wifi()
    wifi_util.get_profiles()
    wifi_util.analyze()

    if args.terminal:
        print(json.dumps(wifi_util.wifi_profiles, indent=4))
    if args.path is not None:
        export(wifi_util.wifi_profiles, args.path)