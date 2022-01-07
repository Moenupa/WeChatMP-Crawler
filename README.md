# 简易的微信公众号推送爬虫

爬取目标公众号内指定数量的推送，获取其发布时间、标题、链接、阅读量等信息。

## 原理

依据已有的：
1. **微信公众号账户** 获得目标公众号的 FakeID 并借此获取其发布的所有推送
2. **微信账户** 模拟微信登陆，获得推送的阅读量等数据

## 使用方法

使用大致有以下步骤：
1. fork 本 repo
1. 微信公众号后台打开任意图文编辑界面，点击上方插入超链接，选择要爬取的目标公众号，查找 Fetch/XHR 找到目标公众号的 FakeID 和自身账户的登录 Cookie
2. 微信电脑端打开任意公众号推送，通过 Fiddler 抓包（查找`getappmsgext`）获取自己微信号的登录信息（包括 Cookie、key、pass_ticket、token）
3. 自行设定 `CTRL_START` `CTRL_END`，注意尽量不要一次爬取超过 20 页
4. 打开你 fork 的 repo，创建一个名为 `CI` 的环境并将以上所有信息填写进 Environment Secret
5. 手动跑一次 Github Action
6. 爬取的内容会在你的 repo 的 PR 内名为 `output.csv` 文件内

注意：本 repo 内爬取阅读量、点赞数等数据暂不可用，显示为-1（截至最新 commit），笔者目前为止未搜索到可行解决方案，也无法复现 [https://github.com/wnma3mz/wechat_articles_spider](https://github.com/wnma3mz/wechat_articles_spider) 所提到的解决方案。

## API

| API 名 | 用途 |
| :--: | :-- |
| `CTRL_START` | 开始页码数（注：一页包含五篇推送） |
| `CTRL_END` | 截至页码数（注：一页包含五篇推送） |
| `MP_COOKIE` | 微信公众号账号的登陆 Cookie |
| `MP_TOKEN` | 微信公众号账号的登陆 token |
| `TARGET_FAKEID` | 爬取目标公众号的 FakeID |
| `WECHAT_COOKIE` | 微信账号的登录 Cookie |
| `WECHAT_KEY` | 微信账号登录 key |
| `WECHAT_PASS` | 微信账号登录 pass_ticket |
| `WECHAT_TOKEN` | 微信账号登录 token |

## LICENSE

[MIT LICENSE](./LICENSE)