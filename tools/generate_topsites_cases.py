import os
import sys
import json
import time
import shutil
from urlparse import urlparse

from lib.sikuli import Sikuli
from lib.browser.chrome import BrowserChrome
from lib.browser.firefox import BrowserFirefox
from lib.helper import desktopHelper


BROWSER_FIREFOX = 'firefox'
BROWSER_CHROME = 'chrome'
DEFAULT_BROWSER_WIDTH = 1200
DEFAULT_BROWSER_HEIGHT = 980

links = [
    'https://www.google.com/#hl=en&q=barack+obama',
    'https://www.facebook.com/barackobama',
    'https://en.wikipedia.org/wiki/Barack_Obama'
]

BROWSER_FIREFOX_LAUNCH_SCRIPT = """
sys.path.append(sys.argv[2])
import browser
import common

com = common.General()
ff = browser.Firefox()

ff.clickBar()
ff.enterLink(sys.argv[3])

sleep(2)
wait(Pattern('{}.png').similar(0.80), 60)
"""
BROWSER_CHROME_LAUNCH_SCRIPT = """
sys.path.append(sys.argv[2])
import browser
import common

com = common.General()
ch = browser.Chrome()

ch.clickBar()
ch.enterLink(sys.argv[3])

sleep(2)
wait(Pattern('{}.png').similar(0.80), 60)
"""

platform = sys.platform
current_file_path = os.path.dirname(os.path.realpath(__file__))
hasal_path = os.path.abspath(os.path.join(current_file_path, '..'))

topsites_link_file = os.path.join(current_file_path, 'topsites.txt')

sikuli_exec_path = os.path.abspath(os.path.join(current_file_path, '..', 'thirdParty', 'runsikulix'))
top_sites_cases_path = os.path.join(hasal_path, 'tests', 'regression', 'topsites')

print('##################################')
print('#  Generate the Top Sites Cases  #')
print('##################################\n\n')

# Load Top Sites list from file
if os.path.isfile(topsites_link_file):
    print('### Loading Top Sites list from {}'.format(topsites_link_file))
    with open(topsites_link_file, 'r') as f:
        links = f.read().split()

print('### There are {} sites:'.format(len(links)))
if len(links) > 5:
    for l in links[:2]:
        print('    - {}'.format(l))
    print('      ...')
    for l in links[-2:]:
        print('    - {}'.format(l))
else:
    for l in links:
        print('    - {}'.format(l))
raw_input('Press Enter to continue...\n')


# init Sikuli runner
runner = Sikuli(sikuli_exec_path, hasal_path)


def generate_topsites(browser):
    # Launch Firefox
    if BROWSER_FIREFOX == browser:
        browser_type = desktopHelper.DEFAULT_BROWSER_TYPE_FIREFOX
        browser_obj = BrowserFirefox(DEFAULT_BROWSER_HEIGHT, DEFAULT_BROWSER_WIDTH)
        launch_script_template = BROWSER_FIREFOX_LAUNCH_SCRIPT
    elif BROWSER_CHROME == browser:
        browser_type = desktopHelper.DEFAULT_BROWSER_TYPE_CHROME
        browser_obj = BrowserChrome(DEFAULT_BROWSER_HEIGHT, DEFAULT_BROWSER_WIDTH)
        launch_script_template = BROWSER_CHROME_LAUNCH_SCRIPT
    else:
        raise Exception('Unknown browser: {}'.format(browser))
    browser_obj.launch()

    print('##############################')
    print('#  Please move {} to the top ...'.format(browser))
    print('##############################')
    raw_input('Press Enter to continue...\n')
    time.sleep(5)
    desktopHelper.lock_window_pos(browser_type)

    # Get Tab location
    print('### [{}] Getting the Tab Icon Location ...'.format(browser))
    script_path = os.path.join(current_file_path, 'topsites_tabicon_location.sikuli')
    params = [current_file_path, browser, platform]
    runner.run_sikulix_cmd(script_path, args_list=params)

    # Load Tab location from file
    xy_json_file = os.path.join(current_file_path, 'tab_xy.json')
    xy = {'x': 0, 'y': 0}
    with open(xy_json_file) as xy_f:
        xy = json.load(xy_f)
    x = xy.get('x')
    y = xy.get('y')
    os.remove(xy_json_file)
    print('### [{}] Loading the Tab location X: {} Y: {}'.format(browser, x, y))

    # Generate the Firefox cases
    script_path = os.path.join(current_file_path, 'topsites_get_cases_tabicon.sikuli')
    for link in links:
        print('### [{}] Generate for: {}'.format(browser, link))

        link_domain = urlparse(link if link.startswith('http') else 'http://{}'.format(link)).netloc
        link_domain_str = link_domain.replace('.', '_').replace(':', '_')
        case_name = 'test_{}_topsites_{}_launch'.format(browser, link_domain_str)
        case_py_file = os.path.join(top_sites_cases_path, '{}.py'.format(case_name))
        case_sikuli_path = os.path.join(top_sites_cases_path, '{}.sikuli'.format(case_name))
        case_sikuli_file = os.path.join(case_sikuli_path, '{}.py'.format(case_name))

        if not os.path.exists(case_sikuli_path):
            os.makedirs(case_sikuli_path)
        if not os.path.exists(case_sikuli_path):
            os.makedirs(case_sikuli_path)

        # Run script to get the tab pic
        params = [current_file_path, link, browser, str(x), str(y), platform]
        runner.run_sikulix_cmd(script_path, args_list=params)

        # Get the tab pic, from current_file_path to cases' folder
        shutil.move(os.path.join(current_file_path, '{}.png'.format(link_domain_str)),
                    os.path.join(case_sikuli_path, '{}.png'.format(link_domain_str)))

        with open(case_py_file, 'w') as pyf:
            pyf.write("""
from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):

    def setUp(self):
        super(TestSikuli, self).setUp()

    def {}(self):
        self.sikuli_status = self.sikuli.run_test(self.env.test_name, self.env.output_name, test_target="{}", script_dp=self.env.test_script_py_dp)
""".format(case_name, link))

        with open(case_sikuli_file, 'w') as spyf:
            spyf.write(launch_script_template.format(link_domain_str))

    print('##############################')
    print('#  You can CLOSE {} now.'.format(browser))
    print('##############################\n\n')


# Create top sites cases folder
if not os.path.exists(top_sites_cases_path):
    os.makedirs(top_sites_cases_path)
with open(os.path.join(top_sites_cases_path, '__init__.py'), 'w') as initf:
    initf.write('')

"""
Firefox Part
"""
generate_topsites(BROWSER_FIREFOX)


"""
Chrome Part
"""
generate_topsites(BROWSER_CHROME)

print('##################################')
print('#           .Finished.           #')
print('# You can press ^C to kill all   #')
print('# sub processes.                 #')
print('##################################')
