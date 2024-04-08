from nicegui import ui, app
import sys, os, json, subprocess, asyncio
import logging, traceback
# from functools import partial

import pyautogui

from utils.config import Config
from utils.common import Common
from utils.logger import Configure_logger


"""

@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@.:;;;++;;;;:,@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@:;+++++;;++++;;;.@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@:++++;;;;;;;;;;+++;,@@@@@@@@@@@@@@@@@
@@@@@@@@@@@.;+++;;;;;;;;;;;;;;++;:@@@@@@@@@@@@@@@@
@@@@@@@@@@;+++;;;;;;;;;;;;;;;;;;++;:@@@@@@@@@@@@@@
@@@@@@@@@:+++;;;;;;;;;;;;;;;;;;;;++;.@@@@@@@@@@@@@
@@@@@@@@;;+;;;;;;;;;;;;;;;;;;;;;;;++:@@@@@@@@@@@@@
@@@@@@@@;+;;;;:::;;;;;;;;;;;;;;;;:;+;,@@@@@@@@@@@@
@@@@@@@:+;;:;;:::;:;;:;;;;::;;:;:::;+;.@@@@@@@@@@@
@@@@@@.;+;::;:,:;:;;+:++:;:::+;:::::++:+@@@@@@@@@@
@@@@@@:+;;:;;:::;;;+%;*?;;:,:;*;;;;:;+;:@@@@@@@@@@
@@@@@@;;;+;;+;:;;;+??;*?++;,:;+++;;;:++:@@@@@@@@@@
@@@@@.++*+;;+;;;;+?;?**??+;:;;+.:+;;;;+;;@@@@@@@@@
@@@@@,+;;;;*++*;+?+;**;:?*;;;;*:,+;;;;+;,@@@@@@@@@
@@@@@,:,+;+?+?++?+;,?#%*??+;;;*;;:+;;;;+:@@@@@@@@@
@@@@@@@:+;*?+?#%;;,,?###@#+;;;*;;,+;;;;+:@@@@@@@@@
@@@@@@@;+;??+%#%;,,,;SSS#S*+++*;..:+;?;+;@@@@@@@@@
@@@@@@@:+**?*?SS,,,,,S#S#+***?*;..;?;**+;@@@@@@@@@
@@@@@@@:+*??*??S,,,,,*%SS+???%++;***;+;;;.@@@@@@@@
@@@@@@@:*?*;*+;%:,,,,;?S?+%%S?%+,:?;+:,,,@@@@@@@@
@@@@@@@,*?,;+;+S:,,,,%?+;S%S%++:+??+:,,,:@@@@@@@@
@@@@@@@,:,@;::;+,,,,,+?%*+S%#?*???*;,,,,,.@@@@@@@@
@@@@@@@@:;,::;;:,,,,,,,,,?SS#??*?+,.,,,:,@@@@@@@@@
@@@@@@;;+;;+:,:%?%*;,,,,SS#%*??%,.,,,,,:@@@@@@@@@
@@@@@.+++,++:;???%S?%;.+#####??;.,,,,,,:@@@@@@@@@
@@@@@:++::??+S#??%#??S%?#@#S*+?*,,,,,,:,@@@@@@@@@@
@@@@@:;;:*?;+%#%?S#??%SS%+#%..;+:,,,,,,@@@@@@@@@@@
@@@@@@,,*S*;?SS?%##%?S#?,.:#+,,+:,,,,,,@@@@@@@@@@@
@@@@@@@;%?%#%?*S##??##?,..*#,,+:,,;*;.@@@@@@@@@@@
@@@@@@.*%??#S*?S#@###%;:*,.:#:,+;:;*+:@@@@@@@@@@@@
@@@@@@,%S??SS%##@@#%S+..;;.,#*;???*?+++:@@@@@@@@@@
@@@@@@:S%??%####@@S,,*,.;*;+#*;+?%??#S%+.@@@@@@@@@
@@@@@@:%???%@###@@?,,:**S##S*;.,%S?;+*?+.,..@@@@@@
@@@@@@;%??%#@###@@#:.;@@#@%%,.,%S*;++*++++;.@@@@@
@@@@@@,%S?S@@###@@@%+#@@#@?;,.:?;??++?%?***+.@@@@@
@@@@@@.*S?S####@@####@@##@?..:*,+:??**%+;;;;..@@@@
@@@@@@:+%?%####@@####@@#@%;:.;;:,+;?**;++;,:;:,@@@
@@@@@@;;*%?%@##@@@###@#S#*:;*+,;.+***?******+:.@@@
@@@@@@:;:??%@###%##@#%++;+*:+;,:;+%?*;+++++;:.@@@@
@@@@@@.+;:?%@@#%;+S*;;,:::**+,;:%??*+.@....@@@@@@@
@@@@@@@;*::?#S#S+;,..,:,;:?+?++*%?+::@@@@@@@@@@@@@
@@@@@@@.+*+++?%S++...,;:***??+;++:.@@@@@@@@@@@@@@@
@@@@@@@@:::..,;+*+;;+*?**+;;;+;:.@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@,+*++;;:,..@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@::,.@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

"""


"""
全局变量
"""
# 创建一个全局变量，用于表示程序是否正在运行
running_flag = False

# 创建一个子进程对象，用于存储正在运行的外部程序
running_process = None

common = None
config = None
audio = None
my_handle = None
config_path = None


web_server_port = 12345


"""
初始化基本配置
"""
def init():
    global config_path, config, common, audio

    common = Common()

    if getattr(sys, 'frozen', False):
        # 当前是打包后的可执行文件
        bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(sys.executable)))
        file_relative_path = os.path.dirname(os.path.abspath(bundle_dir))
    else:
        # 当前是源代码
        file_relative_path = os.path.dirname(os.path.abspath(__file__))

    # logging.info(file_relative_path)

    # 初始化文件夹
    def init_dir():
        # 创建日志文件夹
        log_dir = os.path.join(file_relative_path, 'log')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 创建音频输出文件夹
        audio_out_dir = os.path.join(file_relative_path, 'out')
        if not os.path.exists(audio_out_dir):
            os.makedirs(audio_out_dir)
            
        # # 创建配置文件夹
        # config_dir = os.path.join(file_relative_path, 'config')
        # if not os.path.exists(config_dir):
        #     os.makedirs(config_dir)

    init_dir()

    # 配置文件路径
    config_path = os.path.join(file_relative_path, 'config.json')

    # 日志文件路径
    file_path = "./log/log-" + common.get_bj_time(1) + ".txt"
    Configure_logger(file_path)

    # 获取 httpx 库的日志记录器
    httpx_logger = logging.getLogger("httpx")
    # 设置 httpx 日志记录器的级别为 WARNING
    httpx_logger.setLevel(logging.WARNING)

    # 获取特定库的日志记录器
    watchfiles_logger = logging.getLogger("watchfiles")
    # 设置日志级别为WARNING或更高，以屏蔽INFO级别的日志消息
    watchfiles_logger.setLevel(logging.WARNING)

    logging.debug("配置文件路径=" + str(config_path))

    # 实例化配置类
    config = Config(config_path)


init()

# 暗夜模式
dark = ui.dark_mode()

"""
通用函数
"""
def textarea_data_change(data):
    """
    字符串数组数据格式转换
    """
    tmp_str = ""
    for tmp in data:
        tmp_str = tmp_str + tmp + "\n"
    
    return tmp_str



"""
                                                                                                    
                                               .@@@@@                           @@@@@.              
                                               .@@@@@                           @@@@@.              
        ]]]]]   .]]]]`   .]]]]`   ,]@@@@@\`    .@@@@@,/@@@\`   .]]]]]   ]]]]]`  ]]]]].              
        =@@@@^  =@@@@@`  =@@@@. =@@@@@@@@@@@\  .@@@@@@@@@@@@@  *@@@@@   @@@@@^  @@@@@.              
         =@@@@ ,@@@@@@@ .@@@@` =@@@@^   =@@@@^ .@@@@@`  =@@@@^ *@@@@@   @@@@@^  @@@@@.              
          @@@@^@@@@\@@@^=@@@^  @@@@@@@@@@@@@@@ .@@@@@   =@@@@@ *@@@@@   @@@@@^  @@@@@.              
          ,@@@@@@@^ \@@@@@@@   =@@@@^          .@@@@@.  =@@@@^ *@@@@@  .@@@@@^  @@@@@.              
           =@@@@@@  .@@@@@@.    \@@@@@]/@@@@@` .@@@@@@]/@@@@@. .@@@@@@@@@@@@@^  @@@@@.              
            \@@@@`   =@@@@^      ,\@@@@@@@@[   .@@@@^\@@@@@[    .\@@@@@[=@@@@^  @@@@@.    
            
"""
# 配置
webui_ip = config.get("webui", "ip")
webui_port = config.get("webui", "port")
webui_title = config.get("webui", "title")

# CSS
theme_choose = config.get("webui", "theme", "choose")
tab_panel_css = config.get("webui", "theme", "list", theme_choose, "tab_panel")
card_css = config.get("webui", "theme", "list", theme_choose, "card")
button_bottom_css = config.get("webui", "theme", "list", theme_choose, "button_bottom")
button_bottom_color = config.get("webui", "theme", "list", theme_choose, "button_bottom_color")
button_internal_css = config.get("webui", "theme", "list", theme_choose, "button_internal")
button_internal_color = config.get("webui", "theme", "list", theme_choose, "button_internal_color")
switch_internal_css = config.get("webui", "theme", "list", theme_choose, "switch_internal")


def goto_func_page():
    """
    跳转到功能页
    """
    global audio

    """

      =@@^      ,@@@^        .@@@. .....   =@@.      ]@\  ,]]]]]]]]]]]]]]].  .]]]]]]]]]]]]]]]]]]]]    ,]]]]]]]]]]]]]]]]]`    ,/. @@@^ /]  ,@@@.               
      =@@^ .@@@@@@@@@@@@@@^  /@@\]]@@@@@=@@@@@@@@@.  \@@@`=@@@@@@@@@@@@@@@.  .@@@@@@@@@@@@@@@@@@@@    =@@@@@@@@@@@@@@@@@^   .\@@^@@@\@@@`.@@@^                
    @@@@@@@^@@@@@@@@@@@@@@^ =@@@@@^ =@@\]]]/@@]]@@].  =@/`=@@^  .@@@  .@@@.  .@@@^    @@@^    =@@@             ,/@@@@/`     =@@@@@@@@@@@^=@@@@@@@@@.          
    @@@@@@@^@@@^@@\`   =@@^.@@@]]]`=@@^=@@@@@@@@@@@.]]]]` =@@^=@@@@@@@^@@@.  .@@@\]]]]@@@\]]]]/@@@   @@@\/@\..@@@@[./@/@@@. ,[[\@@@@/[[[\@@@`..@@@`           
      =@@^ ,]]]/@@@]]]]]]]].\@@@@@^@@@OO=@@@@@@@@@..@@@@^ =@@^]]]@@@]]`@@@.  .@@@@@@@@@@@@@@@@@@@@   @@@^=@@@^@@@^/@@@\@@@..]@@@@@@@@@@]@@@@^ .@@@.           
      =@@@@=@@@@@@@@@@@@@@@. =@@^ .OO@@@.[[\@@[[[[.  =@@^ =@@^@@@@@@@@^@@@.  .@@@^    @@@^    =@@@   @@@^ .`,]@@@^`,` =@@@. \@/.]@@@^,@@@@@@\ =@@^            
   .@@@@@@@. .@@@`   /@@/  .@@@@@@@,.=@@=@@@@@@@@@^  =@@^,=@@^=@@@@@@@.@@@.  .@@@\]]]]@@@\]]]]/@@@   @@@^]@@@@@@@@@@@]=@@@. ]]]@@@\]]]]] .=@@\@@@.            
    @@\@@^  .@@@\.  /@@@.    =@@^ =@\@@^.../@@.....  =@@@@=@@^=@@[[\@@.@@@.  .@@@@@@@@@@@@@@@@@@@@   @@@@@@/..@@@^,@@@@@@@. O@@@@@@@@@@@  .@@@@@^             
      =@@^   ,\@@@@@@@@.     =@@^/^\@@@`@@@@@@@@@@^  /@@@/@@@`=@@OO@@@.@@@.  =@@@`    @@@^    =@@@   @@@^  \@@@@@^   .=@@@. .@@@@\`/@@/    /@@@\.             
      =@@^    ,/@@@@@@@@]    =@@@@^/@@@@]` =@@.     .\@/.=@@@ =@@[[[[[.@@@.  /@@@     @@@^   ./@@@   @@@^.............=@@@.    O@@@@@@\`,/@@@@@@@@`           
    @@@@@^.@@@@@@@/..[@@@@/. ,@@`/@@@`[@@@@@@@@@@@@.    /@@@^      =@@@@@@. /@@@^     @@@^,@@@@@@^   @@@@@@@@@@@@@@@@@@@@@..\@@@@@[,\@@\@@@@` ,@@@^           
    ,[[[.  .O[[.        [`        ,/         ......       ,^       .[[[[`     ,`      .... [[[[`                      ,[[[. .[.         ,/.     .`

    """
    # -增加
    def coordinate_add():
        tmp_len = len(screenshot_coordinate_var)
        with coordinate_card.style(card_css):
            with ui.row():
                screenshot_coordinate_var[str(tmp_len)] = ui.input(label=f"x1#{int(tmp_len / 4) + 1}", value="", placeholder='截图选框左上角的x坐标').style("width:100px;")
                screenshot_coordinate_var[str(tmp_len + 1)] = ui.input(label=f"y1#{int(tmp_len / 4) + 1}", value="", placeholder='截图选框左上角的y坐标').style("width:100px;")
                screenshot_coordinate_var[str(tmp_len + 2)] = ui.input(label=f"x2#{int(tmp_len / 4) + 1}", value="", placeholder='截图选框右上角的x坐标').style("width:100px;")
                screenshot_coordinate_var[str(tmp_len + 3)] = ui.input(label=f"y2#{int(tmp_len / 4) + 1}", value="", placeholder='截图选框右上角的y坐标').style("width:100px;")
                
                
    # -删除
    def coordinate_del(index):
        try:
            coordinate_card.remove(int(index) - 1)
            # 删除操作
            keys_to_delete = [str(4 * (int(index) - 1) + i) for i in range(4)]
            for key in keys_to_delete:
                if key in screenshot_coordinate_var:
                    del screenshot_coordinate_var[key]

            # 重新编号剩余的键
            updates = {}
            for key in sorted(screenshot_coordinate_var.keys(), key=int):
                new_key = str(int(key) - 4 if int(key) > int(keys_to_delete[-1]) else key)
                updates[new_key] = screenshot_coordinate_var[key]

            # 应用更新
            screenshot_coordinate_var.clear()
            screenshot_coordinate_var.update(updates)
        except Exception as e:
            ui.notify(position="top", type="negative", message=f"错误，索引值配置有误：{e}")
            logging.error(traceback.format_exc())

    # 创建一个函数，用于运行外部程序
    def run_external_program(config_path="config.json", type="webui"):
        global running_flag, running_process

        if running_flag:
            if type == "webui":
                ui.notify(position="top", type="warning", message="运行中，请勿重复运行")
            return

        try:
            running_flag = True

            # 在这里指定要运行的程序和参数
            # 例如，运行一个名为 "bilibili.py" 的 Python 脚本
            running_process = subprocess.Popen(["python", f"{select_platform.value}.py"])

            if type == "webui":
                ui.notify(position="top", type="positive", message="程序开始运行")
            logging.info("程序开始运行")

            return {"code": 200, "msg": "程序开始运行"}
        except Exception as e:
            if type == "webui":
                ui.notify(position="top", type="negative", message=f"错误：{e}")
            logging.error(traceback.format_exc())
            running_flag = False

            return {"code": -1, "msg": f"运行失败！{e}"}


    # 定义一个函数，用于停止正在运行的程序
    def stop_external_program(type="webui"):
        global running_flag, running_process

        if running_flag:
            try:
                running_process.terminate()  # 终止子进程
                running_flag = False
                if type == "webui":
                    ui.notify(position="top", type="positive", message="程序已停止")
                logging.info("程序已停止")
            except Exception as e:
                if type == "webui":
                    ui.notify(position="top", type="negative", message=f"停止错误：{e}")
                logging.error(f"停止错误：{e}")

                return {"code": -1, "msg": f"重启失败！{e}"}


    # 开关灯
    def change_light_status(type="webui"):
        if dark.value:
            button_light.set_text("关灯")
        else:
            button_light.set_text("开灯")
        dark.toggle()

    # 重启
    def restart_application(type="webui"):
        try:
            # 先停止运行
            stop_external_program(type)

            logging.info(f"重启webui")
            if type == "webui":
                ui.notify(position="top", type="ongoing", message=f"重启中...")
            python = sys.executable
            os.execl(python, python, *sys.argv)  # Start a new instance of the application
        except Exception as e:
            logging.error(traceback.format_exc())
            return {"code": -1, "msg": f"重启失败！{e}"}
        
    # 恢复出厂配置
    def factory(src_path='config.json.bak', dst_path='config.json', type="webui"):
        # src_path = 'config.json.bak'
        # dst_path = 'config.json'

        try:
            with open(src_path, 'r', encoding="utf-8") as source:
                with open(dst_path, 'w', encoding="utf-8") as destination:
                    destination.write(source.read())
            logging.info("恢复出厂配置成功！")
            if type == "webui":
                ui.notify(position="top", type="positive", message=f"恢复出厂配置成功！")
            
            # 重启
            restart_application()

            return {"code": 200, "msg": "恢复出厂配置成功！"}
        except Exception as e:
            logging.error(f"恢复出厂配置失败！\n{e}")
            if type == "webui":
                ui.notify(position="top", type="negative", message=f"恢复出厂配置失败！\n{e}")
            
            return {"code": -1, "msg": f"恢复出厂配置失败！\n{e}"}
    
    
    # 页面滑到顶部
    def scroll_to_top():
        # 这段JavaScript代码将页面滚动到顶部
        ui.run_javascript("window.scrollTo(0, 0);")   


    """
    配置操作
    """
    # 配置检查
    def check_config():
        # 通用配置 页面 配置正确性校验
        if select_platform.value == 'bilibili2' and select_bilibili_login_type.value == 'cookie' and input_bilibili_cookie.value == '':
            ui.notify(position="top", type="warning", message="请先前往 通用配置-哔哩哔哩，填写B站cookie")
            return False
        elif select_platform.value == 'bilibili2' and select_bilibili_login_type.value == 'open_live' and \
            (input_bilibili_open_live_ACCESS_KEY_ID.value == '' or input_bilibili_open_live_ACCESS_KEY_SECRET.value == '' or \
            input_bilibili_open_live_APP_ID.value == '' or input_bilibili_open_live_ROOM_OWNER_AUTH_CODE.value == ''):
            ui.notify(position="top", type="warning", message="请先前往 通用配置-哔哩哔哩，填写开放平台配置")
            return False


        """
        针对配置情况进行提示
        """

        # 检测平台配置，进行提示
        if select_platform.value == "dy":
            ui.notify(position="top", type="warning", message=f"对接抖音平台时，请先开启抖音弹幕监听程序！直播间号不需要填写")
        elif select_platform.value == "bilibili":
            ui.notify(position="top", type="info", message=f"哔哩哔哩1 监听不是很稳定，推荐使用 哔哩哔哩2")
        elif select_platform.value == "bilibili2":
            if select_bilibili_login_type.value == "不登录":
                ui.notify(position="top", type="warning", message=f"哔哩哔哩2 在不登录的情况下，无法获取用户完整的用户名")

        return True

    async def get_mouse_xy():
        sleep_time = 5
        await asyncio.sleep(sleep_time)
        
        # 获取鼠标当前的 x 和 y 坐标
        x, y = pyautogui.position()
        logging.info(f'鼠标当前坐标：x={x}, y={y}')
        ui.notify(position="top", type="info", message=f'鼠标当前坐标：x={x}, y={y}')


    # 保存配置
    def save_config():
        global config, config_path

        # 配置检查
        if not check_config():
            return

        try:
            with open(config_path, 'r', encoding="utf-8") as config_file:
                config_data = json.load(config_file)
        except Exception as e:
            logging.error(f"无法读取配置文件！\n{e}")
            ui.notify(position="top", type="negative", message=f"无法读取配置文件！{e}")
            return False

        def common_textarea_handle(content):
            """通用的textEdit 多行文本内容处理

            Args:
                content (str): 原始多行文本内容

            Returns:
                _type_: 处理好的多行文本内容
            """
            # 通用多行分隔符
            separators = [" ", "\n"]

            ret = [token.strip() for separator in separators for part in content.split(separator) if (token := part.strip())]
            if 0 != len(ret):
                ret = ret[1:]

            return ret


        try:
            """
            通用配置
            """
            if True:
                config_data["platform"] = select_platform.value
                config_data["room_display_id"] = input_room_display_id.value

                # 哔哩哔哩
                config_data["bilibili"]["login_type"] = select_bilibili_login_type.value
                config_data["bilibili"]["cookie"] = input_bilibili_cookie.value
                config_data["bilibili"]["open_live"]["ACCESS_KEY_ID"] = input_bilibili_open_live_ACCESS_KEY_ID.value
                config_data["bilibili"]["open_live"]["ACCESS_KEY_SECRET"] = input_bilibili_open_live_ACCESS_KEY_SECRET.value
                config_data["bilibili"]["open_live"]["APP_ID"] = int(input_bilibili_open_live_APP_ID.value)
                config_data["bilibili"]["open_live"]["ROOM_OWNER_AUTH_CODE"] = input_bilibili_open_live_ROOM_OWNER_AUTH_CODE.value

                config_data["screenshot"]["enable"] = switch_screenshot_enable.value
                config_data["screenshot"]["gift"]["enable"] = switch_screenshot_gift_enable.value
                config_data["screenshot"]["gift"]["min_price"] = float(input_screenshot_gift_min_price.value)
                config_data["screenshot"]["gift"]["screen_delay"] = float(input_screenshot_gift_screen_delay.value)
                config_data["screenshot"]["sc"]["enable"] = switch_screenshot_sc_enable.value
                config_data["screenshot"]["sc"]["min_price"] = float(input_screenshot_sc_min_price.value)
                config_data["screenshot"]["sc"]["screen_delay"] = float(input_screenshot_sc_screen_delay.value)
                config_data["screenshot"]["guard"]["enable"] = switch_screenshot_guard_enable.value
                config_data["screenshot"]["guard"]["min_price"] = float(input_screenshot_guard_min_price.value)
                config_data["screenshot"]["guard"]["screen_delay"] = float(input_screenshot_guard_screen_delay.value)

                tmp_arr = []
                # logging.debug(screenshot_coordinate_var)
                for index in range(len(screenshot_coordinate_var) // 4):
                    tmp_json = {
                        "x1": 0,
                        "y1": 0,
                        "x2": 1920,
                        "y2": 1080
                    }
                    tmp_json["x1"] = float(screenshot_coordinate_var[str(4 * index)].value)
                    tmp_json["y1"] = float(screenshot_coordinate_var[str(4 * index + 1)].value)
                    tmp_json["x2"] = float(screenshot_coordinate_var[str(4 * index + 2)].value)
                    tmp_json["y2"] = float(screenshot_coordinate_var[str(4 * index + 3)].value)
                    tmp_arr.append(tmp_json)
                # logging.info(tmp_arr)
                config_data["screenshot"]["coordinate"] = tmp_arr

            """
            UI配置
            """
            if True:
                config_data["webui"]["title"] = input_webui_title.value
                config_data["webui"]["ip"] = input_webui_ip.value
                config_data["webui"]["port"] = int(input_webui_port.value)
                config_data["webui"]["auto_run"] = switch_webui_auto_run.value

                config_data["webui"]["theme"]["choose"] = select_webui_theme_choose.value

        except Exception as e:
            logging.error(f"无法写入配置文件！\n{e}")
            ui.notify(position="top", type="negative", message=f"无法写入配置文件！\n{e}")
            logging.error(traceback.format_exc())


        # 写入配置到配置文件
        try:
            with open(config_path, 'w', encoding="utf-8") as config_file:
                json.dump(config_data, config_file, indent=2, ensure_ascii=False)
                config_file.flush()  # 刷新缓冲区，确保写入立即生效

            logging.info("配置数据已成功写入文件！")
            ui.notify(position="top", type="positive", message="配置数据已成功写入文件！")

            return True
        except Exception as e:
            logging.error(f"无法写入配置文件！\n{e}")
            ui.notify(position="top", type="negative", message=f"无法写入配置文件！\n{e}")
            return False
    



    """

    ..............................................................................................................
    ..............................................................................................................
    ..........................,]].................................................................................
    .........................O@@@@^...............................................................................
    .....=@@@@@`.....O@@@....,\@@[.....................................,@@@@@@@@@@]....O@@@^......=@@@@....O@@@^..
    .....=@@@@@@.....O@@@............................................=@@@@/`..,[@@/....O@@@^......=@@@@....O@@@^..
    .....=@@@@@@@....O@@@....,]]]].......]@@@@@]`.....,/@@@@\`....../@@@@..............O@@@^......=@@@@....O@@@^..
    .....=@@@/@@@\...O@@@....=@@@@....,@@@@@@@@@@^..,@@@@@@@@@@\...=@@@@...............O@@@^......=@@@@....O@@@^..
    .....=@@@^,@@@\..O@@@....=@@@@...,@@@@`........=@@@/....=@@@\..=@@@@....]]]]]]]]...O@@@^......=@@@@....O@@@^..
    .....=@@@^.=@@@^.O@@@....=@@@@...O@@@^.........@@@@......@@@@..=@@@@....=@@@@@@@...O@@@^......=@@@@....O@@@^..
    .....=@@@^..\@@@^=@@@....=@@@@...@@@@^........,@@@@@@@@@@@@@@..=@@@@.......=@@@@...O@@@^......=@@@@....O@@@^..
    .....=@@@^...\@@@/@@@....=@@@@...O@@@^.........@@@@`...........,@@@@`......=@@@@...O@@@^......=@@@@....O@@@^..
    .....=@@@^....@@@@@@@....=@@@@...,@@@@`........=@@@@......,.....=@@@@`.....=@@@@...=@@@@`.....@@@@^....O@@@^..
    .....=@@@^....,@@@@@@....=@@@@....,@@@@@@@@@@`..=@@@@@@@@@@@`....,@@@@@@@@@@@@@@....,@@@@@@@@@@@@`.....O@@@^..
    .....,[[[`.....,[[[[[....,[[[[.......[@@@@@[`.....,[@@@@@[`.........,\@@@@@@[`.........[@@@@@@[........[[[[`..
    ..............................................................................................................
    ..............................................................................................................

    """


    with ui.tabs().classes('w-full') as tabs:
        common_config_page = ui.tab('通用配置')
        web_page = ui.tab('页面配置')
        about_page = ui.tab('关于')

    with ui.tab_panels(tabs, value=common_config_page).classes('w-full'):
        with ui.tab_panel(common_config_page).style(tab_panel_css):
            with ui.row():
                select_platform = ui.select(
                    label='平台', 
                    options={
                        'bilibili2': '哔哩哔哩2'
                    }, 
                    value=config.get("platform")
                ).style("width:200px;")

                input_room_display_id = ui.input(label='直播间号', placeholder='一般为直播间URL最后/后面的字母或数字', value=config.get("room_display_id")).style("width:200px;")

            with ui.card().style(card_css):
                ui.label('平台相关')
                with ui.card().style(card_css):
                    ui.label('哔哩哔哩')
                    with ui.row():
                        select_bilibili_login_type = ui.select(
                            label='登录方式',
                            options={'cookie': 'cookie', 'open_live': '开放平台', '不登录': '不登录'},
                            value=config.get("bilibili", "login_type")
                        ).style("width:100px")
                        input_bilibili_cookie = ui.input(label='cookie', placeholder='b站登录后F12抓网络包获取cookie，强烈建议使用小号！有封号风险', value=config.get("bilibili", "cookie")).style("width:500px;")
                    with ui.row():
                        with ui.card().style(card_css):
                            ui.label('开放平台')
                            with ui.row():
                                input_bilibili_open_live_ACCESS_KEY_ID = ui.input(label='ACCESS_KEY_ID', value=config.get("bilibili", "open_live", "ACCESS_KEY_ID"), placeholder='开放平台ACCESS_KEY_ID').style("width:300px;")
                                input_bilibili_open_live_ACCESS_KEY_SECRET = ui.input(label='ACCESS_KEY_SECRET', value=config.get("bilibili", "open_live", "ACCESS_KEY_SECRET"), placeholder='开放平台ACCESS_KEY_SECRET').style("width:300px;")
                                input_bilibili_open_live_APP_ID = ui.input(label='项目ID', value=config.get("bilibili", "open_live", "APP_ID"), placeholder='开放平台 创作者服务中心 项目ID').style("width:200px;")
                                input_bilibili_open_live_ROOM_OWNER_AUTH_CODE = ui.input(label='身份码', value=config.get("bilibili", "open_live", "ROOM_OWNER_AUTH_CODE"), placeholder='直播中心用户 身份码').style("width:200px;")
                
            with ui.card().style(card_css):
                ui.label('截图配置')
                with ui.row():
                    switch_screenshot_enable = ui.switch('启用', value=config.get("screenshot", "enable")).style(switch_internal_css)
                    button_get_mouse_xy = ui.button('5s后获取鼠标当前xy坐标', on_click=lambda: get_mouse_xy(), color=button_bottom_color).style(button_bottom_css)
                with ui.row():
                    switch_screenshot_gift_enable = ui.switch('礼物截图', value=config.get("screenshot", "gift", "enable")).style(switch_internal_css)
                    input_screenshot_gift_min_price = ui.input(label='金额下限（元）', value=config.get("screenshot", "gift", "min_price"), placeholder='触发截图的最小金额，大于等于此值').style("width:200px;")
                    input_screenshot_gift_screen_delay = ui.input(label='截图延迟（秒）', value=config.get("screenshot", "gift", "screen_delay"), placeholder='触发截图的延迟时间，解决截图可能过快的问题').style("width:100px;")

                    switch_screenshot_sc_enable = ui.switch('SC截图', value=config.get("screenshot", "sc", "enable")).style(switch_internal_css)
                    input_screenshot_sc_min_price = ui.input(label='金额下限（元）', value=config.get("screenshot", "sc", "min_price"), placeholder='触发截图的最小金额，大于等于此值').style("width:200px;")
                    input_screenshot_sc_screen_delay = ui.input(label='截图延迟（秒）', value=config.get("screenshot", "sc", "screen_delay"), placeholder='触发截图的延迟时间，解决截图可能过快的问题').style("width:100px;")

                    switch_screenshot_guard_enable = ui.switch('舰团截图', value=config.get("screenshot", "guard", "enable")).style(switch_internal_css)
                    input_screenshot_guard_min_price = ui.input(label='金额下限（元）', value=config.get("screenshot", "guard", "min_price"), placeholder='触发截图的最小金额，大于等于此值').style("width:200px;")
                    input_screenshot_guard_screen_delay = ui.input(label='截图延迟（秒）', value=config.get("screenshot", "guard", "screen_delay"), placeholder='触发截图的延迟时间，解决截图可能过快的问题').style("width:100px;")

                with ui.card().style(card_css):
                    ui.label("截图坐标")
                    with ui.row():
                        input_coordinate_index = ui.input(label='坐标索引', value="", placeholder='坐标组的排序号，就是说第一个组是1，第二个组是2，以此类推。请填写纯正整数')
                        button_coordinate_add = ui.button('增加坐标组', on_click=coordinate_add, color=button_internal_color).style(button_internal_css)
                        button_coordinate_del = ui.button('删除坐标组', on_click=lambda: coordinate_del(input_coordinate_index.value), color=button_internal_color).style(button_internal_css)

                    screenshot_coordinate_var = {}
                    coordinate_card = ui.card()
                    for index, coordinate in enumerate(config.get("screenshot", "coordinate")):
                        with coordinate_card.style(card_css):
                            with ui.row():
                                screenshot_coordinate_var[str(4 * index)] = ui.input(label=f"x1#{int(len(screenshot_coordinate_var) / 4) + 1}", value=coordinate["x1"], placeholder='截图选框左上角的x坐标').style("width:100px;")
                                screenshot_coordinate_var[str(4 * index + 1)] = ui.input(label=f"y1#{int(len(screenshot_coordinate_var) / 4) + 1}", value=coordinate["y1"], placeholder='截图选框左上角的y坐标').style("width:100px;")
                                screenshot_coordinate_var[str(4 * index + 2)] = ui.input(label=f"x2#{int(len(screenshot_coordinate_var) / 4) + 1}", value=coordinate["x2"], placeholder='截图选框右下角的x坐标').style("width:100px;")
                                screenshot_coordinate_var[str(4 * index + 3)] = ui.input(label=f"y2#{int(len(screenshot_coordinate_var) / 4) + 1}", value=coordinate["y2"], placeholder='截图选框右下角的y坐标').style("width:100px;")

        with ui.tab_panel(web_page).style(tab_panel_css):
            with ui.card().style(card_css):
                ui.label("webui配置")
                with ui.row():
                    input_webui_title = ui.input(label='标题', placeholder='webui的标题', value=config.get("webui", "title")).style("width:250px;")
                    input_webui_ip = ui.input(label='IP地址', placeholder='webui监听的IP地址', value=config.get("webui", "ip")).style("width:150px;")
                    input_webui_port = ui.input(label='端口', placeholder='webui监听的端口', value=config.get("webui", "port")).style("width:100px;")
                    switch_webui_auto_run = ui.switch('自动运行', value=config.get("webui", "auto_run")).style(switch_internal_css)

            with ui.card().style(card_css):
                ui.label("CSS")
                with ui.row():
                    theme_list = config.get("webui", "theme", "list").keys()
                    data_json = {}
                    for line in theme_list:
                        data_json[line] = line
                    select_webui_theme_choose = ui.select(
                        label='主题', 
                        options=data_json, 
                        value=config.get("webui", "theme", "choose")
                    )

            
        with ui.tab_panel(about_page).style(tab_panel_css):
            with ui.card().style(card_css):
                ui.label('注意').style("font-size:24px;")
                ui.label('严禁将此项目用于一切违反《中华人民共和国宪法》，《中华人民共和国刑法》，《中华人民共和国治安管理处罚法》和《中华人民共和国民法典》之用途。')
                ui.label('严禁用于任何政治相关用途。')
    with ui.grid(columns=6).style("position: fixed; bottom: 10px; text-align: center;"):
        button_save = ui.button('保存配置', on_click=lambda: save_config(), color=button_bottom_color).style(button_bottom_css)
        button_run = ui.button('一键运行', on_click=lambda: run_external_program(), color=button_bottom_color).style(button_bottom_css)
        # 创建一个按钮，用于停止正在运行的程序
        button_stop = ui.button("停止运行", on_click=lambda: stop_external_program(), color=button_bottom_color).style(button_bottom_css)
        button_light = ui.button('关灯', on_click=lambda: change_light_status(), color=button_bottom_color).style(button_bottom_css)
        # button_stop.enabled = False  # 初始状态下停止按钮禁用
        restart_light = ui.button('重启', on_click=lambda: restart_application(), color=button_bottom_color).style(button_bottom_css)
        # factory_btn = ui.button('恢复出厂配置', on_click=lambda: factory(), color=button_bottom_color).style(tab_panel_css)

    with ui.row().style("position:fixed; bottom: 20px; right: 20px;"):
        ui.button('⇧', on_click=lambda: scroll_to_top(), color=button_bottom_color).style(button_bottom_css)

    # 是否启用自动运行功能
    if config.get("webui", "auto_run"):
        logging.info("自动运行 已启用")
        run_external_program(type="api")


goto_func_page()

ui.run(host=webui_ip, port=webui_port, title=webui_title, language="zh-CN", dark=False, reload=False)
