# SigninTools 签到工具合集
<p align="center">
  <a href="https://hits.seeyoufarm.com">
     <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2F397179459%2FSigninTools&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false"/>
  </a>
  <a href="https://github.com/397179459/SigninTools">
    <img src="https://img.shields.io/github/stars/397179459/SigninTools" alt="GitHub Stars">
  </a>
  <a href="https://github.com/397179459/SigninTools">
    <img src="https://img.shields.io/github/forks/397179459/SigninTools" alt="GitHub Forks">
  </a>
  <a href="https://github.com/397179459/SigninTools/issues">
    <img src="https://img.shields.io/github/issues-closed-raw/397179459/SigninTools" alt="GitHub Closed Issues">
  </a>
  <a href="https://github.com/397179459/SigninTools">
    <img alt="GitHub commit activity (branch)" src="https://img.shields.io/github/commit-activity/y/397179459/SigninTools">
  </a>
  <a href="https://github.com/397179459/SigninTools">
    <img src="https://img.shields.io/github/last-commit/397179459/SigninTools" alt="GitHub Last Commit">
  </a>
</p>

#### 支持合集：
- [x] 百度贴吧 

#### 百度贴吧
- 用的是手机端的接口，签到经验更多，用户只需要填写`BDUSS`即可，利用Actions每日自动签到。
- 支持推送运行结果至微信(`server酱` `PushPlus`)

## 使用方法

### 1.fork本项目

### 2.获取BDUSS

在网页中登录上贴吧，然后按下`F12`打开调试模式，在`cookie`中找到`BDUSS`，并复制其`Value`值。

### 3.在Github Secrets配置你的AES密钥，pushplus，server酱的key

Name | Value
-|-
PRIVATE_AES_KEY | xxxxxxxxxxx
PUSHPLUS_KEY | xxxxxxxxxxx
SCKEY | xxxxxxxxxxx

### 4. 运行/core/baiduTieba/bduss.py，配置相关信息

### 5.第一次运行actions
`.github/workflows/actionActive.txt`中的随便修改一点内容`push`。

- 每天凌晨`2:30`将会自动进行签到