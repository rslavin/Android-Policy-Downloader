#!/usr/bin/env python3

# Google Play privacy policy downloader
# Author: Rocky Slavin

import argparse
import sys
import urllib.error as urlerror
import urllib.request as request
import re
import socket
import os

URL_PREFIX = "https://play.google.com/store/apps/details?id="
URL_SUFFIX = "&hl=en"
DEFAULT_OUT_DIR = "./downloaded_policies"
DEFAULT_TIMEOUT = 15
POLICY_PATTERN = r'<a href=\"([^\"]+)\"[^>]*?>Privacy Policy</a'


def get_policy(policy_url, filename, out_dir):
    """
    Retrieves an html or pdf policy file and saves it locally
    :param policy_url: url for the policy file
    :param filename: name, without extension, to save file as locally
    :param out_dir: directory in which to save the policy
    :return returns True if the policy is successfully downloaded, False otherwise
    """
    print(f"Retrieving policy from {policy_url}")
    # determine name and extension of output file
    policy_ext = "pdf" if "pdf" in policy_url else "html"
    policy_file_path = os.path.join(out_dir, f"{filename}.{policy_ext}")

    try:
        # request the remote file
        with request.urlopen(policy_url) as response:
            try:
                # save policy to local filesystem
                print("Saving policy to " + policy_file_path)
                with open(policy_file_path, "wb") as out_file:
                    out_file.write(response.read())
                    print(f"SUCCESS: saved to {policy_file_path}")
                    return True
            except IOError:
                print(f"ERROR: unable to write policy file to {policy_file_path}", file=sys.stderr)
    except urlerror.HTTPError as e:
        if e.code == 404:
            print(f"ERROR: policy not found at {policy_url}", file=sys.stderr)
        else:
            print(f"ERROR: HTTP exception for policy at {policy_url}: {e.code}", file=sys.stderr)
    except OSError as e:
        print(f"ERROR: request timed out for policy file at {policy_url}", file=sys.stderr)
    return False


def get_policy_url(app_package):
    """
    Retrieves the privacy policy url from the Google Play store for a specific app
    :param app_package: app's package name (e.g., com.android.chrome)
    :return returns either the policy url or None if not found
    """
    print(f"Retrieving policy url for {app_package}")
    # build url based on package name
    app_url = URL_PREFIX + re.sub(r'\.apk$', '', app_package) + URL_SUFFIX

    try:
        # request Google Play page for the app
        response = request.urlopen(app_url)
    except urlerror.HTTPError as e:
        if e.code == 404:
            print(f"ERROR: 404 - app page not found at {app_url}", file=sys.stderr)
        else:
            print(f"ERROR: HTTP exception for app page at {app_url}: {e.code}", file=sys.stderr)
        return None
    except OSError as e:
        print(f"ERROR: request timed out for app page at {app_url}", file=sys.stderr)
        return None

    # locate the privacy policy url in the Google Play page
    match = re.search(POLICY_PATTERN, response.read().decode('utf-8'))

    # return url if found
    if match:
        print(f"FOUND URL: {app_url}")
        return match.group(1)

    print(f"ERROR: 404 - no policy file found at {app_url}", file=sys.stderr)


def get_all_policies(app_list, out_dir):
    """
    Given a file containing a list of app packages, downloads their policies to specified output directory
    :param app_list: file containing list of apps, one per line, specified as package names (e.g., com.android.chrome)
    :param out_dir: path to output directory
    """
    try:
        # parse the list of app package names one line at a time
        with open(app_list, "r") as apps:
            for app in apps:
                app = app.rstrip()
                # locate the policy url
                policy_url = get_policy_url(app)
                if policy_url:
                    try:
                        # attempt to save the policy to the file system
                        get_policy(policy_url, app, out_dir)
                    except Exception as e:
                        print(f"ERROR: unknown error for app {app}: {e}", file=sys.stderr)
                print("")
    except IOError:
        print(f"ERROR: unable to open file {app_list}", file=sys.stderr)




def parse_args():
    """
    Parses arguments. Use --help for usage info.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("app_list", metavar="<app_list>",
                        help="location of file containing list of apps, one per line as package name (e.g., "
                             "com.android.chrome")
    parser.add_argument("-o", "--out_dir", default=DEFAULT_OUT_DIR,
                        help=f"output directory ({DEFAULT_OUT_DIR} by default)")
    parser.add_argument("-t", "--timeout", default=DEFAULT_TIMEOUT,
                        help=f"HTTP request timeout in seconds ({DEFAULT_TIMEOUT} by default)")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    # set default timeout for all socket objects
    socket.setdefaulttimeout(args.timeout)
    # create output dir if it doesn't exist
    if not os.path.exists(args.out_dir):
        os.makedirs(args.out_dir)
    get_all_policies(args.app_list, args.out_dir)
