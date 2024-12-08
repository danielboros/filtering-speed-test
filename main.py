import argparse
import json
import numpy as np
import matplotlib.pyplot as plt
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import time

LOGGING_PREFERENCES = {
    "performance": "ALL", "browser": "ALL"
}

def configure_cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="Filtering Speed Test",
        description="A simple tester that measures latency to an upstream L7 filtering service."
    )

    parser.add_argument(
        "--doh-upstream",
        required=False,
        type=str,
        default="https://chrome.cloudflare-dns.com/dns-query",
        help="The upstream to use for DNS-over-HTTPS (DoH) tests."
    )

    parser.add_argument(
        "--url",
        required=True,
        type=str,
        help="The URL to use for this test."
    )

    parser.add_argument(
        "--figure",
        required=False,
        type=str,
        default="latency.png",
        help="Path to output final distribution to."
    )

    parser.add_argument(
        "--num", "-n",
        required=True,
        type=int,
        help="Number of times to run domain."
    )
    
    return parser.parse_args()

def distribution(log_entries, save_path):
    start_request_timestamps = {}
    finish_request_timestamps = {}

    for e in log_entries:
        try:
            if e['message']['method'] == 'Network.requestWillBeSent':
                start_request_timestamps[e['message']['params']['requestId']] = e['message']['params']['timestamp']
            elif e['message']['method'] == 'Network.responseReceived':
                finish_request_timestamps[e['message']['params']['requestId']] = e['message']['params']['timestamp']
        except KeyError:
            pass

    request_total_latency = {}
    request_millis = []

    for rid, final_ts in finish_request_timestamps.items():
        try:
            start_ts = start_request_timestamps[rid]
            latency = (final_ts - start_ts) * 1000 # S -> MS
            request_total_latency[rid] = latency
            request_millis.append(latency)
        except KeyError:
            pass

    plt.title('Chrome Driver Request Latency Distribution\nAVG: {:.2f}ms, MIN: {:.2f}ms, MAX: {:.2f}ms, TOTAL: {} Requests'.format(
        np.average(request_millis),
        np.min(request_millis),
        np.max(request_millis),
        len(request_millis)))
    plt.ylabel('# Requests')
    plt.xlabel('Latency (ms)')
    plt.hist(request_millis, bins=int(len(request_millis) / 8))
    plt.autoscale(tight=True)
    plt.savefig(save_path)

def main():
    args = configure_cli()
    
    local_state = {
        "dns_over_https.mode": "secure",
        "dns_over_https.templates": args.doh_upstream,
    }

    options = Options()
    options.add_experimental_option('localState', local_state)
    options.set_capability("goog:loggingPrefs", LOGGING_PREFERENCES)

    # Run the test multiple times to suss out the unlucky tail case.
    log_entries = []
    for _ in range(args.num):
        driver = Chrome(options=options)
        driver.get(args.url)
        driver.fullscreen_window()
        for _ in range(20):
            driver.execute_script("window.scrollBy(0, 750);")
            time.sleep(1.)
        current_entries = driver.get_log("performance")
        for e in current_entries:
            log_entries.append(json.loads(e['message']))
        driver.close()
        
    distribution(log_entries, args.figure)

if __name__ == "__main__":
    main()