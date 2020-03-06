# -*- coding: utf-8 -*-
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import urllib.request as req
import sys
import pathlib
import chromedriver_binary
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir) + '/../')


class Starbucks:
    _result_df = pd.DataFrame(columns=['store_name', 'address'])

    @staticmethod
    def _AppendItemToDataFrame(storeName: str, storeAddress: str):
        """
        店舗名と住所を受け取り、クラス変数のDataFrameに追加する

        Parameters
        -----
        storeName : str
            店舗名
        storeAddress : str
            住所
        """
        tmp_se = pd.Series([storeName, storeAddress],
                           index=Starbucks._result_df.columns)
        Starbucks._result_df = Starbucks._result_df.append(
            tmp_se, ignore_index=True)

    @staticmethod
    def _OpenURLWithSelenium(url: str):
        """
        URLをSeleniumで開く

        Parameter
        -----
        url : str
            開きたいページのURL

        Return
        -----
        browser : WebDriver
            ページを開いた後のWebDriverオブジェクト
        """
        browser = webdriver.Chrome()
        browser.get(url)
        return browser

    @staticmethod
    def _OpenURLWithBeautifulSoup(url: str):
        """
        URLをBeautifulSoup(パーサーはhtml.parser)で開く

        Parameter
        -----
        url : str
            開きたいページのURL

        Return
        -----
        soup : BeautifulSoup
            ページを開いた後のBeautifulSoupオブジェクト
        """
        res = req.urlopen(url)
        soup = BeautifulSoup(res, "html.parser")
        return soup

    @staticmethod
    def getStoreInfo():
        BASE_URL = 'https://store.starbucks.co.jp/?keyword='
        browser = Starbucks._OpenURLWithSelenium(BASE_URL)

        # 「もっと見る」ボタンが表示されているうちは、ボタンを押下し続ける
        BUTTON_XPATH = '/html/body/div[3]/article/div[2]/div[3]/div/ul/li[1]/div[2]/p'
        moreshow_button = browser.find_element_by_xpath(BUTTON_XPATH)
        wait = WebDriverWait(browser, 200, poll_frequency=0.1)
        while moreshow_button.get_attribute("style") != 'display: none;':
            wait.until(EC.presence_of_element_located(
                (By.XPATH, BUTTON_XPATH)))
            moreshow_button.click()

        # 店舗一覧が表示されたら、DataFrameへの格納を開始する
        res = browser.page_source
        soup = BeautifulSoup(res, "lxml")
        shoplist_html = soup.find('ul',
                                  class_='resultStores js-component', id='list')
        for li_tag in shoplist_html:
            for shopdiv_html in li_tag.find_all('div', class_="detailContainer"):
                storeName = shopdiv_html.find("p", class_="storeName").string
                storeAddress = shopdiv_html.find(
                    "p", class_="storeAddress").string
                Starbucks._AppendItemToDataFrame(storeName, storeAddress)

        # 実行確認用
        # print(Starbucks._result_df)
        # Starbucks._result_df.to_csv('./Starbucks.csv')
        return Starbucks._result_df


if __name__ == "__main__":
    starbucks = Starbucks()
    starbucks.getStoreInfo()
