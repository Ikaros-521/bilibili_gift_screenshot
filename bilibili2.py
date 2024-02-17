import logging, os
import threading
import random
import asyncio
import traceback

import http.cookies
from typing import *

import aiohttp

import blivedm
import blivedm.models.web as web_models
import blivedm.models.open_live as open_models

import pyautogui
from PIL import Image

from utils.common import Common
from utils.config import Config
from utils.logger import Configure_logger

"""
	___ _                       
	|_ _| | ____ _ _ __ ___  ___ 
	 | || |/ / _` | '__/ _ \/ __|
	 | ||   < (_| | | | (_) \__ \
	|___|_|\_\__,_|_|  \___/|___/

"""

config = None
common = None
my_handle = None
# last_liveroom_data = None
last_username_list = None
# 空闲时间计数器
global_idle_time = 0



# 点火起飞
def start_server():
    global config, common, my_handle, last_username_list, SESSDATA


    # 配置文件路径
    config_path = "config.json"

    common = Common()
    config = Config(config_path)
    # 日志文件路径
    log_path = "./log/log-" + common.get_bj_time(1) + ".txt"
    Configure_logger(log_path)

    # 获取 httpx 库的日志记录器
    httpx_logger = logging.getLogger("httpx")
    # 设置 httpx 日志记录器的级别为 WARNING
    httpx_logger.setLevel(logging.WARNING)

    # 最新入场的用户名列表
    last_username_list = [""]

    # 直播间ID的取值看直播间URL
    TEST_ROOM_IDS = [config.get("room_display_id")]

    try:
        if config.get("bilibili", "login_type") == "cookie":
            bilibili_cookie = config.get("bilibili", "cookie")
            SESSDATA = common.parse_cookie_data(bilibili_cookie, "SESSDATA")
        elif config.get("bilibili", "login_type") == "open_live":
            # 在开放平台申请的开发者密钥 https://open-live.bilibili.com/open-manage
            ACCESS_KEY_ID = config.get("bilibili", "open_live", "ACCESS_KEY_ID")
            ACCESS_KEY_SECRET = config.get("bilibili", "open_live", "ACCESS_KEY_SECRET")
            # 在开放平台创建的项目ID
            APP_ID = config.get("bilibili", "open_live", "APP_ID")
            # 主播身份码 直播中心获取
            ROOM_OWNER_AUTH_CODE = config.get("bilibili", "open_live", "ROOM_OWNER_AUTH_CODE")

    except Exception as e:
        logging.error(traceback.format_exc())

    def my_screenshot(data, type):
        """我的截图函数

        Args:
            data (dict): 数据json串
            type (str): 数据类型
        """
        try:
            if config.get("screenshot", "enable") == False:
                return
            
            if False == config.get("screenshot", type, "enable"):
                return
            
            if data["total_price"] < float(config.get("screenshot", type, "min_price")):
                return

            # 截取全屏
            screenshot = pyautogui.screenshot()

            for coordinate in config.get("screenshot", "coordinate"):
                # 定义截图区域 (left, top, right, bottom)
                bbox = (float(coordinate["x1"]), float(coordinate["y1"]), float(coordinate["x2"]), float(coordinate["y2"]))

                # 裁剪截图到指定区域
                partial_screenshot = screenshot.crop(bbox)

                folder_path = f"./out/{common.get_bj_time(1)}"

                # 检查文件夹是否存在
                if not os.path.exists(folder_path):
                    # 如果文件夹不存在，则创建它
                    os.makedirs(folder_path)
                    logging.info(f'文件夹已创建：{folder_path}')

                file_path = f"{folder_path}/{common.get_bj_time(7)}.png"

                # 保存截图
                partial_screenshot.save(file_path)

                logging.info(f'截图保存：{file_path}')
        except Exception as e:
            logging.error(traceback.format_exc())

    async def main_func():
        global session

        if config.get("bilibili", "login_type") == "open_live":
            await run_single_client2()
        else:
            try:
                init_session()

                await run_single_client()
                await run_multi_clients()
            finally:
                await session.close()


    def init_session():
        global session, SESSDATA

        cookies = http.cookies.SimpleCookie()
        cookies['SESSDATA'] = SESSDATA
        cookies['SESSDATA']['domain'] = 'bilibili.com'

        # logging.info(f"SESSDATA={SESSDATA}")

        session = aiohttp.ClientSession()
        session.cookie_jar.update_cookies(cookies)


    async def run_single_client():
        """
        演示监听一个直播间
        """
        global session

        room_id = random.choice(TEST_ROOM_IDS)
        client = blivedm.BLiveClient(room_id, session=session)
        handler = MyHandler()
        client.set_handler(handler)

        client.start()
        try:
            # 演示5秒后停止
            await asyncio.sleep(5)
            client.stop()

            await client.join()
        finally:
            await client.stop_and_close()

    async def run_single_client2():
        """
        演示监听一个直播间 开放平台
        """
        client = blivedm.OpenLiveClient(
            access_key_id=ACCESS_KEY_ID,
            access_key_secret=ACCESS_KEY_SECRET,
            app_id=APP_ID,
            room_owner_auth_code=ROOM_OWNER_AUTH_CODE,
        )
        handler = MyHandler2()
        client.set_handler(handler)

        client.start()
        try:
            # 演示70秒后停止
            # await asyncio.sleep(70)
            # client.stop()

            await client.join()
        finally:
            await client.stop_and_close()

    async def run_multi_clients():
        """
        演示同时监听多个直播间
        """
        global session

        clients = [blivedm.BLiveClient(room_id, session=session) for room_id in TEST_ROOM_IDS]
        handler = MyHandler()
        for client in clients:
            client.set_handler(handler)
            client.start()

        try:
            await asyncio.gather(*(
                client.join() for client in clients
            ))
        finally:
            await asyncio.gather(*(
                client.stop_and_close() for client in clients
            ))


    class MyHandler(blivedm.BaseHandler):
        # 演示如何添加自定义回调
        _CMD_CALLBACK_DICT = blivedm.BaseHandler._CMD_CALLBACK_DICT.copy()
        
        # 入场消息回调
        def __interact_word_callback(self, client: blivedm.BLiveClient, command: dict):
            # logging.info(f"[{client.room_id}] INTERACT_WORD: self_type={type(self).__name__}, room_id={client.room_id},"
            #     f" uname={command['data']['uname']}")
            
            global last_username_list

            user_name = command['data']['uname']

            logging.debug(f"用户：{user_name} 进入直播间")

            data = {
                "platform": "哔哩哔哩2",
                "username": user_name,
                "content": "进入直播间"
            }


        _CMD_CALLBACK_DICT['INTERACT_WORD'] = __interact_word_callback  # noqa

        def _on_heartbeat(self, client: blivedm.BLiveClient, message: web_models.HeartbeatMessage):
            logging.debug(f'[{client.room_id}] 心跳')

        def _on_danmaku(self, client: blivedm.BLiveClient, message: web_models.DanmakuMessage):
            global global_idle_time

            # 闲时计数清零
            global_idle_time = 0

            # logging.info(f'[{client.room_id}] {message.uname}：{message.msg}')
            content = message.msg  # 获取弹幕内容
            user_name = message.uname  # 获取发送弹幕的用户昵称

            logging.debug(f"[{user_name}]: {content}")

            data = {
                "platform": "哔哩哔哩2",
                "username": user_name,
                "content": content
            }


        def _on_gift(self, client: blivedm.BLiveClient, message: web_models.GiftMessage):
            # logging.info(f'[{client.room_id}] {message.uname} 赠送{message.gift_name}x{message.num}'
            #     f' （{message.coin_type}瓜子x{message.total_coin}）')
            
            gift_name = message.gift_name
            user_name = message.uname
            # 礼物数量
            combo_num = message.num
            # 总金额
            combo_total_coin = message.total_coin

            logging.info(f"用户：{user_name} 赠送 {combo_num} 个 {gift_name}，总计 {combo_total_coin}电池")

            data = {
                "platform": "哔哩哔哩2",
                "gift_name": gift_name,
                "username": user_name,
                "num": combo_num,
                "unit_price": combo_total_coin / combo_num / 1000,
                "total_price": combo_total_coin / 1000
            }

            my_screenshot(data, "gift")


        def _on_buy_guard(self, client: blivedm.BLiveClient, message: web_models.GuardBuyMessage):
            logging.debug(f"{message}")

            logging.info(f'[{client.room_id}] {message.username} 购买{message.gift_name}')

            gift_name = message.gift_name
            user_name = message.username

            data = {
                "platform": "哔哩哔哩2",
                "gift_name": gift_name,
                "username": user_name,
                "total_price": 138
            }

            my_screenshot(data, "guard")

        def _on_super_chat(self, client: blivedm.BLiveClient, message: web_models.SuperChatMessage):
            # logging.info(f'[{client.room_id}] 醒目留言 ¥{message.price} {message.uname}：{message.message}')
            # logging.info(f"{message}")

            message = message.message
            uname = message.uname
            price = message.price

            logging.info(f"用户：{uname} 发送 {price}元 SC：{message}")

            data = {
                "platform": "哔哩哔哩2",
                "gift_name": "SC",
                "username": uname,
                "num": 1,
                "unit_price": price,
                "total_price": price,
                "content": message
            }

            my_screenshot(data, "sc")


    class MyHandler2(blivedm.BaseHandler):
        def _on_heartbeat(self, client: blivedm.BLiveClient, message: web_models.HeartbeatMessage):
            logging.debug(f'[{client.room_id}] 心跳')

        def _on_open_live_danmaku(self, client: blivedm.OpenLiveClient, message: open_models.DanmakuMessage):
            global global_idle_time

            # 闲时计数清零
            global_idle_time = 0

            # logging.info(f'[{client.room_id}] {message.uname}：{message.msg}')
            content = message.msg  # 获取弹幕内容
            user_name = message.uname  # 获取发送弹幕的用户昵称

            logging.debug(f"[{user_name}]: {content}")

            data = {
                "platform": "哔哩哔哩2",
                "username": user_name,
                "content": content
            }

        def _on_open_live_gift(self, client: blivedm.OpenLiveClient, message: open_models.GiftMessage):
            gift_name = message.gift_name
            user_name = message.uname
            # 礼物数量
            combo_num = message.gift_num
            # 总金额
            combo_total_coin = message.price * message.gift_num

            logging.info(f"用户：{user_name} 赠送 {combo_num} 个 {gift_name}，总计 {combo_total_coin}电池")

            data = {
                "platform": "哔哩哔哩2",
                "gift_name": gift_name,
                "username": user_name,
                "num": combo_num,
                "unit_price": combo_total_coin / combo_num / 1000,
                "total_price": combo_total_coin / 1000
            }

            my_screenshot(data, "gift")


        def _on_open_live_buy_guard(self, client: blivedm.OpenLiveClient, message: open_models.GuardBuyMessage):
            logging.info(f'[{client.room_id}] {message.user_info.uname} 购买 大航海等级={message.guard_level}')

            user_name = message.user_info.uname

            data = {
                "platform": "哔哩哔哩2",
                "username": user_name,
                "total_price": 138
            }

            my_screenshot(data, "guard")

        def _on_open_live_super_chat(
            self, client: blivedm.OpenLiveClient, message: open_models.SuperChatMessage
        ):
            print(f'[{message.room_id}] 醒目留言 ¥{message.rmb} {message.uname}：{message.message}')

            message = message.message
            uname = message.uname
            price = message.rmb

            logging.info(f"用户：{uname} 发送 {price}元 SC：{message}")

            data = {
                "platform": "哔哩哔哩2",
                "gift_name": "SC",
                "username": uname,
                "num": 1,
                "unit_price": price,
                "total_price": price,
                "content": message
            }

            my_screenshot(data, "sc")

        def _on_open_live_super_chat_delete(
            self, client: blivedm.OpenLiveClient, message: open_models.SuperChatDeleteMessage
        ):
            logging.info(f'[直播间 {message.room_id}] 删除醒目留言 message_ids={message.message_ids}')

        def _on_open_live_like(self, client: blivedm.OpenLiveClient, message: open_models.LikeMessage):
            logging.debug(f'用户：{message.uname} 点了个赞')


    asyncio.run(main_func())


if __name__ == '__main__':
    # 这里填一个已登录账号的cookie。不填cookie也可以连接，但是收到弹幕的用户名会打码，UID会变成0
    SESSDATA = ''

    session: Optional[aiohttp.ClientSession] = None

    start_server()
