# coding: UTF-8
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup
import time


URL = "https://www.●●●"
#商品ページ

options = Options()
#options.headless = True

driver = webdriver.Chrome(executable_path='C:\\chromedriver_win32\\chromedriver.exe',options=options)

#ブラウザ最大化
driver.maximize_window()
driver.get(URL)
#driver.refresh()


#処理中断 → 手動ログイン、リロード、"start"入力
print("ログインページで手動でリロードを行ってからログインする")
print("商品の一覧ページを表示させる")
print("View:で１列表示をクリックする")
print("コンソールにstartと入力して処理を開始する")
while input() != "start":
    print("startと入力してください")



"""URLの取得"""
s = driver.current_url
html = driver.page_source.encode('utf-8')
time.sleep(2)
soup = BeautifulSoup(html, "html.parser")

#ページ数の取得
breadcrumb = soup.find_all(class_='next-breadcrumb-text')[1].find('span').text
#category_name = breadcrumb.split("\"")[1]
product_num = int(breadcrumb[breadcrumb.find(" (") + 2:breadcrumb.find(" Results)")].replace(',', '')) // 60 + 1


for listpage in range(1,product_num+1):
    #パラメータ付き一覧ページのURL作成
    listpage_url = s + "&page=" + str(listpage)
    #ドライバで読み込み
    driver.get(listpage_url)
    time.sleep(2)
    #商品リンクの部分までスクロール
    scroll = 180
    driver.execute_script("window.scrollTo(0, "+str(scroll)+");")
    time.sleep(1)

    #少しずつ下までスクロール
    while scroll < 12000:
        scroll += 700
        driver.execute_script("window.scrollTo(0, "+str(scroll)+");")

    #商品リストのhref取得する 不足があれば更にスクロール
    links = []
    flag = True
    while flag:
        #一覧ページのHTML取得
        html = driver.page_source.encode('utf-8')
        time.sleep(1)
        soup = BeautifulSoup(html, "html.parser")
        products_list = soup.find_all(class_='product-card')
        if not len(links) < len(products_list):
            flag = False
            continue
        for element in products_list:
            href_text = 'https:' + str(element.find_all("a")[0].get('href'))
            if href_text in links:
                continue
            links.append(href_text)

        scroll += 700
        driver.execute_script("window.scrollTo(0, "+str(scroll)+");")
        time.sleep(1)

    #hrefの値をcsv保存する
    with open("file/urls.txt","a",encoding="utf_8") as f:
        for ele in links:
            f.write(ele + '\n')

    #確認
    print( str(listpage) + "ページ終了:" + str(len(links)) )

