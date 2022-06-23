from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def members_of_Inno():
    op = Options()
    op.add_argument("--disable-blink-features=Automationcontrolled")
    s = Service("chromedriver.exe")
    driver = webdriver.Chrome(service=s, options=op)
    driver.get("https://www.researchgate.net/institution/Innopolis-University/members")
    n = driver.find_elements(by=By.CLASS_NAME,
                             value="nova-legacy-c-button.nova-legacy-c-button--align-center.nova-legacy-c"
                                   "-button--radius-full.nova-legacy-c-button--size-s.nova-legacy-c"
                                   "-button--color-grey.nova-legacy-c-button--theme-bare.nova-legacy-c"
                                   "-button--width-square.nova-legacy-c-pagination__button")

    print(driver.page_source)
    members = dict()
    for i in range(2, int(n[len(n) - 1].text) + 2):
        members_info = driver.find_elements(by=By.CLASS_NAME,
                                            value="nova-legacy-v-person-list-item__stack.nova-legacy-v-person-list"
                                                  "-item__stack--gutter-m")
        jpg = driver.find_elements(by=By.CLASS_NAME, value="nova-legacy-e-avatar__img")
        for j in range(len(members_info)):
            info = members_info[j].find_elements(by=By.CLASS_NAME, value="nova-legacy-v-person-list-item__stack-item")
            name = info[0].find_element(by=By.CLASS_NAME,
                                        value="nova-legacy-e-link.nova-legacy-e-link--color-inherit.nova-legacy-e-link"
                                              "--theme-bare").text
            department = "None"
            disciplines = []
            if len(info) == 3:
                department = info[1].find_element(by=By.CLASS_NAME,
                                                  value="nova-legacy-e-list__item.nova-legacy-v-person-list-item__info"
                                                        "-section-list-item").text
                disciplines = [x.text for x in info[2].find_elements(by=By.CLASS_NAME,
                                                                     value="nova-legacy-e-link.nova-legacy-e-link--color"
                                                                           "-inherit.nova"
                                                                           "-legacy-e-link--theme-bare")]
            if len(info) == 2:
                if info[1].find_element(by=By.CLASS_NAME,
                                        value="nova-legacy-e-text.nova-legacy-e-text--size-s.nova-legacy-e-text--family"
                                              "-sans-serif.nova-legacy-e-text--spacing-none.nova-legacy-e-text--color"
                                              "-inherit.nova-legacy-v-person-list-item__info-section-title").text == \
                        "Department":
                    department = info[1].find_element(by=By.CLASS_NAME,
                                                      value="nova-legacy-e-list__item.nova-legacy-v-person-list"
                                                            "-item__info-section-list-item").text
                else:
                    disciplines = [x.text for x in info[1].find_elements(by=By.CLASS_NAME,
                                                                         value="nova-legacy-e-link.nova-legacy-e-link"
                                                                               "--color-inherit.nova"
                                                                               "-legacy-e-link--theme-bare")]
            members[name] = [jpg[j].get_attribute("src"), department, disciplines]
            # f = "src"
            # print(f"Name: {name}, Jpg: {jpg[j].get_attribute(f)}, Department: {department}, Disciplines: {disciplines}")
        driver.switch_to.new_window("tab")
        driver.get(f"https://www.researchgate.net/institution/Innopolis-University/members/{i}")
    return members
