# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.

INPUT_LIB_PATH = sys.argv[1]
sys.path.append(INPUT_LIB_PATH)

import os
import common
import basecase
import outlook
import shutil
import browser
import time


class Case(basecase.SikuliInputLatencyCase):

    def run(self):
        # Disable Sikuli action and info log
        com = common.General()
        com.infolog_enable(False)
        com.set_mouse_delay(0)

        # Prepare
        app = outlook.outlook()
        sample1_file_path = os.path.join(self.INPUT_IMG_SAMPLE_DIR_PATH, self.INPUT_IMG_OUTPUT_SAMPLE_1_NAME)
        sample1_file_path = sample1_file_path.replace(os.path.splitext(sample1_file_path)[1], '.png')
        capture_width = int(self.INPUT_RECORD_WIDTH)
        capture_height = int(self.INPUT_RECORD_HEIGHT)

        # Launch browser
        my_browser = browser.Firefox()

        # Access link and wait
        my_browser.clickBar()
        my_browser.enterLink(self.INPUT_TEST_TARGET)
        app.wait_for_loaded()

        # Wait for stable
        sleep(5)

        # PRE ACTIONS
        app.mouse_move_to_compose_new_mail_button()
        app._click(action_name='Click compose new mail icon', component=app.OUTLOOK_COMPOSE_NEW_MAIL_ICON)
        app.click_compose_new_mail_content()
        app.wait_for_new_mail_button_function_loaded()
        sleep(2)

        # Customized Region
        customized_region_name = 'end'
        type_area = self.find_match_region(app.OUTLOOK_MIDDLE_UPPER_MENU_ICON, similarity=0.75)
        modified_area = self.tuning_region(type_area, y_offset=260, x_offset=-58, w_offset=-85, h_offset=30)
        self.set_override_region_settings(customized_region_name, modified_area)

        # Record T1, and capture the snapshot image
        # Input Latency Action
        screenshot, t1 = app.il_type('a', capture_width, capture_height)

        # In normal condition, a should appear within 100ms,
        # but if lag happened, that could lead the show up after 100 ms,
        # and that will cause the calculation of AIL much smaller than expected.
        sleep(0.1)

        # Record T2
        t2 = time.time()

        # POST ACTIONS
        app.click_discard_mail()
        app.click_discard_mail_confirmation()

        # Write timestamp
        com.updateJson({'t1': t1, 't2': t2}, self.INPUT_TIMESTAMP_FILE_PATH)

        # Write the snapshot image
        shutil.move(screenshot, sample1_file_path)

case = Case(sys.argv)
case.run()
