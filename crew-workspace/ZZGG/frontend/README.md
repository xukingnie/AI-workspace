# ZZGG Frontend

基于 Vue 3 + Vite + Vant 的示例前端，包含：

- 日历：使用 `Calendar` 选择账单日期
- 账单表单：使用 `Field` 和 `Button` 提交账单
- 倒计时：使用 `CountDown` 展示下一个账单截止时间
- 预留后端联调：默认请求 `http://127.0.0.1:8000/api`

## 启动

```bash
npm install
npm run dev
```

如需修改后端地址，可创建 `.env.local`：

```bash
VITE_API_BASE=http://127.0.0.1:8000/api
```
