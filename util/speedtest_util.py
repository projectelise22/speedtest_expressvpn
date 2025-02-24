import json
import subprocess, platform, socket
import logging, time
from datetime import datetime

# Utility constants
INPUT_FILE = "locations.json"
VPN_ALIASES_FILE = "vpn_aliases.json"
REPEAT_TESTS = 5

# Output Files
start_time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = f"speedtest_util_{start_time_str}.log"
OUTPUT_FILE = f"results_{start_time_str}.json"

class VPNTester:
    def __init__(self):
        """Initialize the VPN tester and logging."""
        self.setup_logging()
        self.vpn_aliases = self.load_json_file(VPN_ALIASES_FILE)
        self.locations = self.load_json_file(INPUT_FILE)
        self.results = self.get_machine_info()

    def setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            filename=LOG_FILE,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Print logs to console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(console_formatter)
        logging.getLogger().addHandler(console_handler)

    @staticmethod
    def run_command(command):
        """Run shell command and return output."""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.stdout.strip()
        except Exception as e:
            logging.error(f"Error executing command `{command}`: {e}")
            return str(e)

    @staticmethod
    def load_json_file(filename):
        """Loads a JSON file."""
        try:
            with open(filename, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logging.error(f"Error loading {filename}: {e}")
            return {}

    def get_vpn_status(self):
        """Checks if ExpressVPN is connected or disconnected."""
        output = self.run_command("expressvpn status").lower()
        if "disconnected" in output:
            logging.info("🔌 VPN is currently DISCONNECTED.")
            return "disconnected"
        elif "connected" in output:
            logging.info("👍 VPN is currently CONNECTED.")
            return "connected"
        else:
            logging.warning(f"😵‍💫 Check if VPN is activated properly {output}")
            return "unknown"

    def get_vpn_alias(self, country, city):
        """Gets the VPN alias from the mapping file."""
        return self.vpn_aliases.get(country, {}).get(city, None)

    def measure_connection_time(self, country, city, max_retries=3):
        """Measures time taken to connect to an ExpressVPN server."""
        alias = self.get_vpn_alias(country, city)
        if not alias:
            logging.warning(f"❌ No VPN alias found for {city}, {country}. Skipping...")
            return None

        for attempt in range(1, max_retries + 1):
            logging.info(f"🔄 Connecting to {alias} (Attempt {attempt}/{max_retries})...")
            start_time = time.time()
            output = self.run_command(f"expressvpn connect {alias}")
            end_time = time.time()

            if "connected" in output.lower():
                logging.info(f"✅ Successfully connected to {alias} in {round(end_time - start_time, 2)} sec.")
                return round(end_time - start_time, 2)
            else:
                logging.warning(f"😵‍💫 Attempt {attempt}: Failed to connect to {alias}. Retrying...")
                if attempt < max_retries + 1:
                    time.sleep(5)

        logging.error(f"❌ Connection to {alias} failed after {max_retries} attempts. Skipping.")
        return None

    def get_speedtest(self, max_retries=3):
        """Runs speedtest-cli and returns download speed in Mbps."""
        for attempt in range(1, max_retries + 1):
            output = self.run_command("speedtest --json")

            if "403" in output:
                logging.warning(f"🥲 Attempt {attempt}: Speedtest fails to connect.")
            else:
                try:
                    result = json.loads(output)
                    speed_mbps = round(result.get("download", {}) / 1_000_000, 2)
                    logging.info(f"✅ Speedtest completed: {speed_mbps} Mbps")
                    return speed_mbps
                except json.JSONDecodeError:
                    logging.error(f"❌ Attempt {attempt}: Error decoding speedtest JSON output.")
                    logging.debug(f"Raw Output: {output}")

            if attempt < max_retries + 1:
                logging.info(f"Retrying speedtest in 5 seconds... (Attempt {attempt+1}/{max_retries})")
                time.sleep(5)

        logging.error("❌ Speedtest failed after max retries. Skipping.")
        return 0

    @staticmethod
    def get_machine_info():
        """Gets system information."""
        return {
            "MachineName": socket.gethostname(),
            "OS": f"{platform.system()} {platform.release()}"
        }

    def test_vpn_locations(self):
        """Main testing loop for all VPN locations."""
        # Ensure VPN is disconnected before starting tests
        if self.get_vpn_status() != "disconnected":
            logging.info("🔌 Disconnecting VPN before starting tests...")
            self.run_command("expressvpn disconnect")
            time.sleep(3)
        
        # Get speed without VPN connected
        self.results["WithoutVPN"] = f"{self.get_speedtest()} Mbps"

        # Turn off network_lock so speedtest-cli is useable when expressvpn is connected
        self.run_command("expressvpn preferences set network_lock off")
        time.sleep(3)

        # Get status for each location with expressvpn connected
        vpn_stats = []

        for location in self.locations.get("locations", []):
            country, city = location["country"], location["city"]
            logging.info(f"🚀 Testing VPN for {city}, {country}...")

            connection_times = []
            download_speeds = []

            for i in range(REPEAT_TESTS):
                logging.info(f"⏳ Running test {i+1}/{REPEAT_TESTS} for {city}, {country}...")

                connection_time = self.measure_connection_time(country, city, max_retries=1)
                if connection_time is None:
                    continue  

                download_speed = self.get_speedtest(max_retries=1)
                connection_times.append(connection_time)
                download_speeds.append(download_speed)

                self.run_command("expressvpn disconnect")
                time.sleep(5)

            if connection_times:
                vpn_stats.append({
                    "LocationName": f"{city}, {country}",
                    "TimeToConnect": f"{sum(connection_times) / len(connection_times):.2f} sec",
                    "VPNSpeed": f"{sum(download_speeds) / len(download_speeds):.2f} Mbps"
                })

        self.results["VPNStats"] = vpn_stats
        self.save_results()

        self.run_command("expressvpn disconnect")
        self.run_command("expressvpn preferences set network_lock on")

    def save_results(self):
        """Saves results to a JSON file."""
        with open(OUTPUT_FILE, "w") as file:
            json.dump(self.results, file, indent=4)
        logging.info(f"✅ Results saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    tester = VPNTester()
    tester.test_vpn_locations()
