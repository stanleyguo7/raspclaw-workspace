# Assistant Playbook (Stanley)

> 从既有 MEMORY/工作记录中整理的可执行规则（仅保留工作相关）。

## 默认执行偏好

1. **项目改动默认 push**
   - 在项目完成 commit 后直接 push。
   - 不需要每次询问是否推送。

2. **“告诉我今日资讯”固定流程**
   - 抓取主要新闻网站 + 社交媒体热点
   - 输出标题、摘要、链接
   - 先给汇总介绍
   - 创建或更新飞书文档保存结果
   - 默认加强“中国国内 + 科技方向”覆盖

3. **“做一个小程序”默认流程**
   - 在 `stanley-rasp-demos/demos/<app-name>/` 新建
   - 生成代码与 README
   - 提交并 push 到 `stanleyguo7/stanley-rasp-demos`
   - 提供可访问链接

4. **“检查网络代理”默认动作**
   - 运行：`stanley-homeboard/scripts/check-proxy-and-recover.sh`

## 项目入口与地址

- `stanley-rasp-demos`：<https://stanley-rasp-demos.vercel.app/>
- `kids-habbit`：<https://kids-habbit.vercel.app/>

## 每日日志流程（GitHub）

- 日志仓库：`git@github.com:stanleyguo7/raspclaw-workspace.git`
- 路径：`daily-logs/YYYY-MM-DD.md`
- 收尾模板：完成项 / 未完成项 / 明日第一步
- 写完后：commit + push
