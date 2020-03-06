# -*- coding: utf-8 -*-
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
# from modules.db_util import *
# from modules.update_db import *
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import urllib.request as req
import sys
import re
# import chromedriver_binary
import time
import ast
import pathlib
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir) + '/../')


class Sanai:
    baseurl = "https://www.san-ai.com/shoplist"
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
                           index=Sanai._result_df.columns)
        Sanai._result_df = Sanai._result_df.append(
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
    def _OpenPagesourceWithBeautifulSoup(page_source):
        """
        WebDriver.pagesourceをBeautifulSoup(パーサーはhtml.parser)で開く

        Parameter
        -----
        page_source
            開きたいページのページソース

        Return
        -----
        soup : BeautifulSoup
            ページを開いた後のBeautifulSoupオブジェクト
        """
        soup = BeautifulSoup(page_source, "html.parser")
        return soup

    @staticmethod
    def getStoreInfo():
        page = Sanai._OpenURLWithBeautifulSoup(Sanai.baseurl)

        """
        店舗情報がjavascriptによって動的に生成されているため、ページに含まれていたjavascriptのコードから店舗情報をスクレイピングしている
        """
        # var shop_data をpythonのリスト型に変換している
        inner_script = re.split(
            '(<div class="sysFuncText shoplist_json sysDisplayKeitaiNone">|<div class="sysFuncText shoplist_script sysDisplayKeitaiNone">)', str(page))
        data_dic_str = re.split('(var shop_data =|;)', inner_script[2])[2]
        data_dic_list = ast.literal_eval(data_dic_str)

        # 店舗情報を収集している
        # 店舗の判定条件はもとのページのjavascriptのプログラムと同じくしている
        for store in data_dic_list:
            if store['display'] == '○' and store['address'] != '':
                storeName = store['shop_name'] + " " + store["sc_name"]
                storeName = re.sub("<.*>", "", storeName)
                storeAddress = store['address']

                Sanai._AppendItemToDataFrame(storeName, storeAddress)

        return Sanai._result_df


if __name__ == "__main__":
    df = Sanai.getStoreInfo()
    # brand_id = UpdateDB.getBrandId(os.path.basename(__file__))
    # df['brand_id'] = brand_id
    # new_brand_df = df.rename(columns={0: 'store_name', 1: 'address'})
    # conn_pg = DBUtil.getConnect()
    # UpdateDB.execUpdateStandby(conn_pg, brand_id, new_brand_df)
