# coding: UTF-8
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup

import os
import requests
import time
import re


#画像の保存、大画像のファイル名取得
def storageImages(requests,folder_name,element,addText):
    URL_s = element.get('src')
    URL_b = URL_s
    #if URL_s.endswith('_50x50.jpg'):
    if '_50x50.' in URL_s:
            URL_b = URL_s[ :len(URL_s) - 10]
            URL_b += addText
    img_s = URL_s.split('/')[4] + URL_s.split('/')[5]
    img_b = URL_b.split('/')[4] + URL_b.split('/')[5]
    r = requests.get(URL_s)
    with open(folder_name + '/' + img_s,'wb') as f:
            f.write(r.content)
    r = requests.get(URL_b)
    with open(folder_name + '/' + img_b,'wb') as f:
            f.write(r.content)
    return URL_b,img_b


#展開商品の情報を取得
def storageDevelopment(driver): #,each_product
    html = driver.page_source.encode('utf-8')
    time.sleep(2)
    soup = BeautifulSoup(html, "html.parser")
    #展開された商品情報取得
    each_product = []
    try:
        each_product.append('name：' + soup.find_all(class_="product-title")[0].text)
    except IndexError:
        each_product.append('name：')
    try:
        each_product.append('price：' + soup.find_all(class_="product-price-value")[0].text)
    except IndexError:
        each_product.append('price：')
    try:
        each_product.append('listPrice：' + soup.find_all(class_="product-price-value")[1].text)
    except IndexError:
        each_product.append('listPrice：')
    try:
        each_product.append('remarks：' + soup.find_all(class_="sku-title-value")[0].text)
    except IndexError:
        each_product.append('remarks：')
    try:
        each_product.append('shipping：' + soup.find_all(class_="product-shipping-delivery")[0].text)
    except IndexError:
        each_product.append('shipping：')
    return each_product


URL = "https://www.●●●●"

options = Options()
#options.headless = True

driver = webdriver.Chrome(executable_path='C:\\chromedriver_win32\\chromedriver.exe',options=options)

#ブラウザ最大化
driver.maximize_window()

#CSVファイルから商品ページのURLを取得
a = input('urls.txtファイルの何行目から取得しますか？')
index = int(a)-1
loop = True
while loop:
    with open("file/urls.txt","r",encoding="utf_8") as f:
        try:
            URL = f.readlines()[index]
            print(str(index+1) + "：" + URL)
        except IndexError:# as e:
            print("error")
            loop = False
            continue
    driver.get(URL)

    if int(a)-1 == index:
        #処理中断 → 手動ログイン、リロード、"start"入力
        print("ログインページで手動でリロードを行ってからログインする")
        print("file/urls.txtファイルを同階層に用意する")
        print("コンソールにstartと入力して処理を開始する")
        while input() != "start":
            print("startと入力してください")

    #商品情報の格納
    product_general = [1]
    time.sleep(2)

    """商品IDの取得"""
    s = driver.current_url
    productURL = re.match(r'^https://www.aliexpress.com/item/[0-9]+\.html', s).group()
    productID = productURL.rstrip('.html').split('/')[-1]
    product_general.append(productURL)#商品URL
    product_general.append(productID)#商品ID

    driver.execute_script("window.scrollTo(0, 200);")

    html = driver.page_source.encode('utf-8')
    time.sleep(2)
    soup = BeautifulSoup(html, "html.parser")

    print("商品ID/URL：完了")

    #商品単位のデータの格納

    #商品画像の格納
    folder_name = 'picture/' + str(productID)
    os.makedirs(folder_name, exist_ok=True)
    url_list = []
    img_list = []

    #画像取得　表示画像の下の画像　1商品に対して1セットのため色、サイズ展開は不要
    for target in soup.find_all(class_='images-view-item'):
        for element in target.find_all('img'):
            #画像の保存
            URL_b,img_b = storageImages(requests,folder_name,element,'')
            url_list.append(URL_b)
            img_list.append(img_b)
            time.sleep(1)
    product_general.append(url_list)
    product_general.append(img_list)

    print("商品画像：完了")

    """商品ページのサイズや色の展開ボタンをクリックしながら値を取得"""
    product_development = [2]
    num = len(driver.find_elements_by_class_name('sku-property-list'))

    #展開ごとに画像とテキストを取得
    html = driver.page_source.encode('utf-8')
    time.sleep(1)
    soup = BeautifulSoup(html, "html.parser")
    deployElements = []

    if num >= 1:
        #1番目の展開
        list1 = driver.find_elements_by_class_name('sku-property-list')[0]
        element1 = soup.find_all(class_='sku-property-list')[0]
        dep1 = []
        len1 = 0
        #画像だったら
        images = element1.find_all(class_='sku-property-image')
        len1 = len(images)
        if len1 >= 1:
            for image in images:
                element = image.find('img')
                URL_b,img_b = storageImages(requests,folder_name,element,'_640x640.jpg')
                each = []
                each.append(URL_b)
                each.append(img_b)
                dep1.append(each)
        #テキストだったら
        else:
            texts = element1.find_all(class_='sku-property-text')
            len1 = len(texts)
            for text in texts:
                each = []
                each.append(text.find('span').text)
                dep1.append(each)
        #格納
        deployElements.append(dep1)

    if num >= 2:
        #2番目の展開
        list2 = driver.find_elements_by_class_name('sku-property-list')[1]
        element2 = soup.find_all(class_='sku-property-list')[1]
        dep2 = []
        len2 = 0
        #画像だったら
        images = element2.find_all(class_='sku-property-image')
        len2 = len(images)
        if len2 >= 1:
            for image in images:
                element = image.find('img')
                URL_b,img_b = storageImages(requests,folder_name,element,'_640x640.jpg')
                each = []
                each.append(URL_b)
                each.append(img_b)
                dep2.append(each)
        #テキストだったら
        else:
            texts = element2.find_all(class_='sku-property-text')
            len2 = len(texts)
            for text in texts:
                each = []
                each.append(text.find('span').text)
                dep2.append(each)
        #格納
        deployElements.append(dep2)

    if num >= 3:
        #3番目の展開
        list3 = driver.find_elements_by_class_name('sku-property-list')[2]
        element3 = soup.find_all(class_='sku-property-list')[2]
        dep3 = []
        len3 = 0
        #画像だったら
        images = element3.find_all(class_='sku-property-image')
        len3 = len(images)
        if len(images) >= 1:
            for image in images:
                element = image.find('img')
                URL_b,img_b = storageImages(requests,folder_name,element,'_640x640.jpg')
                each = []
                each.append(URL_b)
                each.append(img_b)
                dep3.append(each)
        #テキストだったら
        else:
            texts = element3.find_all(class_='sku-property-text')
            len3 = len(texts)
            for text in texts:
                each = []
                each.append(text.find('span').text)
                dep3.append(each)
        #格納
        deployElements.append(dep3)

    print("商品展開ボタン要素：完了")

    #
    each_product = []
    if num >= 1:
        for i,elm1 in enumerate(list1.find_elements_by_class_name('sku-property-item')):
            if len1 >= 2:#ボタンが１つだけの場合はスキップ
                try:
                    elm1.click()
                    time.sleep(1)
                except selenium.common.exceptions.ElementClickInterceptedException:
                    continue
            if num == 1:
                each_product = storageDevelopment(driver)
                try:
                    each_product.append(deployElements[0][i])
                except IndexError:
                    pass
                product_development.append(each_product)
            else:
                for k,elm2 in enumerate(list2.find_elements_by_class_name('sku-property-item')):
                    if len2 >= 2:#ボタンが１つだけの場合はスキップ
                        try:
                            elm2.click()
                            time.sleep(1)
                        except selenium.common.exceptions.ElementClickInterceptedException as e:
                            continue
                    if num == 2:
                        each_product = storageDevelopment(driver)
                        try:
                            each_product.append(deployElements[0][i])
                            each_product.append(deployElements[1][k])
                        except IndexError:
                            pass
                        product_development.append(each_product)
                    else:
                        for m,elm3 in enumerate(list3.find_elements_by_class_name('sku-property-item')):
                            if len3 >= 2:#ボタンが１つだけの場合はスキップ
                                try:
                                    elm3.click()
                                    time.sleep(1)
                                except selenium.common.exceptions.ElementClickInterceptedException as e:
                                    continue
                            each_product = storageDevelopment(driver)
                            try:
                                each_product.append(deployElements[0][i])
                                each_product.append(deployElements[1][k])
                                each_product.append(deployElements[2][m])
                            except IndexError:
                                pass
                            product_development.append(each_product)
    else:
        each_product = storageDevelopment(driver)
        product_development.append(each_product)

    print("各商品展開情報：完了")


    """説明の下部の取得"""
    driver.execute_script("window.scrollTo(0, 550);")
    time.sleep(1)

    info_general = [3]

    html = driver.page_source.encode('utf-8')
    time.sleep(2)
    soup = BeautifulSoup(html, "html.parser")
    try:
        OVERVIEW = soup.find_all(class_="origin-part")
        if len(OVERVIEW) >= 1:
            info_general.append(OVERVIEW[0])
    except IndexError:
        info_general.append('NG OVERVIEW')


    try:
        driver.find_elements_by_class_name('tab-inner-text')[6].click()#
    except:
        pass

    html = driver.page_source.encode('utf-8')
    time.sleep(2)
    soup = BeautifulSoup(html, "html.parser")

    try:
        SPECIFICATIONS = soup.find_all(class_="product-specs")
        if len(SPECIFICATIONS) >= 1:
            info_general.append(SPECIFICATIONS[0])
    except IndexError:
        info_general.append('NG SPECIFICTATIONS')


    print("OVERVIEW/SPECIFICATIONS：完了")

    #パンクズ取得
    driver.execute_script("window.scrollTo(0, 5000);")

    flag = True
    while flag:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        html = driver.page_source.encode('utf-8')
        time.sleep(1)
        soup = BeautifulSoup(html, "html.parser")
        try:
            elements = soup.find_all(class_='breadcrumb')[0]
        except selenium.common.exceptions.NoSuchElementException as e:
            continue

        breadcrumb_list = []
        a_list = elements.find_all("a")
        if len(a_list) >= 1:
            for crumb in a_list:
                breadcrumb_list.append(crumb.text)
            info_general.append(breadcrumb_list)
            flag = False

    print("パンクズ情報：完了")
    print("")

    #商品情報を保存する
    with open("file/products.txt","a",encoding="utf_8") as f:
        for line in product_general:
            f.write(str(line) + '\n')
        for line in product_development:
            f.write(str(line) + '\n')
        for line in info_general:
            f.write(str(line) + '\n')

    index += 1

