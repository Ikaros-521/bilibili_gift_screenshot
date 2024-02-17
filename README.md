# 前言

程序名：B站送礼截图  
主旨：记录B站观众送礼时的屏幕情况（如：操作截图、礼物特效、礼物弹幕等）
功能：用于哔哩哔哩直播时，用户送礼物时触发截图，可自定义截图区域  

# 开发环境

python：3.10.10  
操作系统：win11  

# 使用

## 安装依赖

`pip install requirements.txt`  

## 运行webui

`python webui.py`，启动后自动打开浏览器访问webui页面，完成配置后点击`保存配置`，再`一键运行`即可。  

# 效果图
![image](https://github.com/Ikaros-521/bilibili_gift_screenshot/assets/40910637/cb9c005d-2c63-4ae4-933a-f24067521b44)

![image](https://github.com/Ikaros-521/bilibili_gift_screenshot/assets/40910637/032813dd-dbca-4b49-8497-a2742ab689b0)


# 更新日志
- 2024-2-17
    - 新增 坐标组增删功能
    - 修改截图文件名到毫秒，修复多个区域截图被覆盖的bug
    - 修复SC数据处理bug
- 2024-2-15
    - 初版demo发布
    
