# 123云盘离线下载工具 - 使用说明

## 📋 目录
- [功能简介](#功能简介)
- [环境要求](#环境要求)
- [安装步骤](#安装步骤)
- [获取Token教程](#获取token教程)
- [配置Token](#配置token)
- [使用方法](#使用方法)
- [常见问题](#常见问题)

---

## 功能简介

本工具基于 123 云盘官方 API 实现，支持：
- ✅ 解析磁力链接，获取文件列表
- ✅ 提交离线下载任务到 123 云盘
- ✅ 批量处理多个磁力链接
- ✅ 详细的进度反馈和错误提示

---

## 环境要求

- **Python 版本**: Python 3.7+
- **依赖库**: requests
- **操作系统**: Windows / macOS / Linux

---

## 安装步骤

### 1. 安装 Python
如果尚未安装 Python，请访问 [https://www.python.org/downloads/](https://www.python.org/downloads/) 下载并安装。

### 2. 安装依赖库
打开命令行（CMD 或 PowerShell），执行：
```bash
pip install requests
```

### 3. 验证安装
```bash
python --version
pip list | findstr requests
```

---

## 获取Token教程

### 方法一：通过浏览器开发者工具（推荐）

#### Chrome / Edge 浏览器

1. **登录 123 云盘**
   - 访问 [https://www.123pan.com/](https://www.123pan.com/)
   - 使用账号密码登录

2. **打开开发者工具**
   - 按 `F12` 键
   - 或右键页面 → 选择"检查"

3. **查找 Token**
   - 切换到 **Application** 标签页（Chrome）或 **存储** 标签页（Firefox）
   - 在左侧菜单展开 **Local Storage**
   - 点击 `https://www.123pan.com`
   - 在右侧找到以下任一字段：
     - `authorToken`（优先使用）
     - `userInfo`（需要解析 JSON）

4. **复制 Token**
   - 双击 `authorToken` 对应的值
   - 按 `Ctrl+C` 复制
   - Token 通常是一个长字符串（长度 > 50 字符）

#### Firefox 浏览器

1. 按 `F12` 打开开发者工具
2. 切换到 **存储** 标签
3. 展开 **本地存储** → `https://www.123pan.com`
4. 找到 `authorToken` 并复制其值

---

### 方法二：通过油猴脚本自动获取

如果您已安装 `AnySite Magnet to 123pan` 油猴脚本：

1. 访问 [https://www.123pan.com/](https://www.123pan.com/) 并登录
2. 等待右下角出现蓝色悬浮球（☁️ 图标）
3. 点击悬浮球，Token 会自动同步到油猴存储
4. 在 Tampermonkey 仪表盘中查看脚本存储的值：
   - 打开 Tampermonkey 管理面板
   - 找到 `AnySite Magnet to 123pan` 脚本
   - 点击"存储"标签
   - 复制 `123_token` 的值

---

### 方法三：通过网络请求捕获

1. 登录 123 云盘后，保持开发者工具打开
2. 切换到 **Network** 标签页
3. 刷新页面或执行任意操作
4. 找到任意发送到 `www.123pan.com` 的请求
5. 查看请求头中的 `Authorization` 字段
6. 复制 `Bearer` 后面的部分（即 Token）

---

## 配置Token

### 方式一：直接在脚本中配置（推荐用于个人使用）

1. 打开 `pan123_offline_download.py` 文件

2. 找到第 18 行附近的 `__init__` 方法

3. 在类定义上方添加全局变量：
```python
# ==================== 用户配置区域 ====================
# 在此处填入您的 123 云盘 Token
USER_TOKEN = "在此粘贴您的Token字符串"
# ====================================================
```

4. 修改 `__init__` 方法，使用全局变量：
```python
def __init__(self, token: str = None):
    """
    初始化客户端
    
    Args:
        token: 123云盘授权Token (Bearer Token)，如果不提供则使用全局配置
    """
    self.token = token or USER_TOKEN
    # ... 其余代码保持不变
```

5. 修改 `main()` 函数，跳过手动输入：
```python
def main():
    """主函数"""
    try:
        # 使用配置的Token
        if not USER_TOKEN or USER_TOKEN == "在此粘贴您的Token字符串":
            print("[ERROR] 请先在脚本顶部配置 USER_TOKEN")
            return 1
        
        # 创建客户端
        client = Pan123OfflineDownload()
        
        # ... 其余代码保持不变
```

---

### 方式二：通过环境变量配置（推荐用于服务器部署）

#### Windows 系统

1. **临时设置**（当前会话有效）
```powershell
$env:PAN123_TOKEN="你的Token字符串"
python pan123_offline_download.py
```

2. **永久设置**
   - 右键"此电脑" → 属性 → 高级系统设置
   - 点击"环境变量"
   - 在"用户变量"或"系统变量"中新建：
     - 变量名：`PAN123_TOKEN`
     - 变量值：`你的Token字符串`
   - 重启命令行窗口

#### macOS / Linux 系统

1. **临时设置**
```bash
export PAN123_TOKEN="你的Token字符串"
python pan123_offline_download.py
```

2. **永久设置**
编辑 `~/.bashrc` 或 `~/.zshrc`：
```bash
echo 'export PAN123_TOKEN="你的Token字符串"' >> ~/.bashrc
source ~/.bashrc
```

3. **修改脚本读取环境变量**
在脚本顶部添加：
```python
import os

# 从环境变量读取Token，如果没有则使用默认值
USER_TOKEN = os.getenv('PAN123_TOKEN', '')
```

---

### 方式三：通过配置文件（推荐用于多用户场景）

1. 创建配置文件 `config.json`：
```json
{
    "token": "你的Token字符串",
    "auto_select_all": true,
    "timeout": 30
}
```

2. 在脚本中添加配置加载逻辑：
```python
import json
import os

def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

config = load_config()
USER_TOKEN = config.get('token', '')
```

---

## 使用方法

### 基础用法

1. **配置 Token**（参考上一节）

2. **运行脚本**
```bash
python pan123_offline_download.py
```

3. **输入磁力链接**
```
请输入磁力链接:
magnet:?xt=urn:btih:5c9668b76b9e3e046066d700c4d2e37a84c0ff69&dn=...
```

4. **查看结果**
脚本会自动解析并提交任务，显示：
```
[SUCCESS] 解析成功!
[INFO] 任务ID: task_xxxxx
[INFO] 文件数量: 3
  [1] example.mp4 (1024.50 MB)
  [2] subtitle.srt (0.05 MB)
  
[SUCCESS] 任务提交成功!
[INFO] 下载任务ID: task_xxxxx
[INFO] 任务状态: processing

[COMPLETE] 成功添加 2 个文件到离线下载
```

---

### 批量处理示例

创建 `batch_download.py`：
```python
from pan123_offline_download import Pan123OfflineDownload

# 配置Token
TOKEN = "你的Token字符串"

# 磁力链接列表
magnets = [
    "magnet:?xt=urn:btih:...",
    "magnet:?xt=urn:btih:...",
    # 添加更多链接...
]

# 创建客户端
client = Pan123OfflineDownload(TOKEN)

# 批量处理
for idx, magnet in enumerate(magnets, 1):
    print(f"\n{'='*60}")
    print(f"处理第 {idx}/{len(magnets)} 个链接")
    print(f"{'='*60}")
    
    try:
        result = client.save_to_123pan(magnet)
        print(f"[OK] 第 {idx} 个任务提交成功")
    except Exception as e:
        print(f"[FAIL] 第 {idx} 个任务失败: {e}")
    
    # 避免请求过快，间隔1秒
    import time
    time.sleep(1)

print("\n批量处理完成！")
```

---

## 常见问题

### Q1: Token 有效期是多久？

**A**: Token 通常在登录后 7-30 天内有效，具体取决于 123 云盘的策略。如果收到 "TOKEN_EXPIRED" 错误，请重新获取 Token。

---

### Q2: 为什么提示 "Token长度异常"？

**A**: 可能的原因：
1. 复制时遗漏了部分字符
2. 包含了多余的空格或换行符
3. 复制的是 `userInfo` 的整个 JSON 而非其中的 `token` 字段

**解决方法**：
- 确保完整复制 `authorToken` 的值
- 使用 `.strip()` 去除首尾空格
- Token 长度通常在 100-300 字符之间

---

### Q3: 如何验证 Token 是否有效？

**A**: 运行脚本并尝试解析任意磁力链接，如果成功则 Token 有效。或者访问 123 云盘官网，确认仍处于登录状态。

---

### Q4: 支持哪些类型的链接？

**A**: 目前仅支持标准磁力链接格式：
```
magnet:?xt=urn:btih:[哈希值]&dn=[文件名]&tr=[tracker地址]
```

不支持：
- HTTP/HTTPS 直链
- ed2k 链接
- 迅雷专用链接

---

### Q5: 离线下载有次数限制吗？

**A**: 123 云盘对免费用户可能有每日离线下载次数限制，具体请查看 123 云盘官方说明。VIP 用户通常享有更高限额。

---

### Q6: 如何查看已提交的离线下载任务？

**A**: 
1. 访问 [https://www.123pan.com/](https://www.123pan.com/)
2. 登录后点击左侧菜单的"离线下载"
3. 查看所有任务和下载进度

---

### Q7: 脚本报错 "网络连接失败" 怎么办？

**A**: 
1. 检查网络连接是否正常
2. 确认可以访问 `https://www.123pan.com/`
3. 检查防火墙或代理设置
4. 尝试增加超时时间（修改 `_request` 方法中的 `timeout=30`）

---

### Q8: 可以在服务器上长期运行吗？

**A**: 可以，但建议：
1. 使用环境变量或配置文件管理 Token
2. 添加日志记录功能
3. 实现 Token 自动刷新机制
4. 设置定时任务定期清理已完成的任务

---

## 安全提示

⚠️ **重要提醒**：

1. **不要公开分享 Token**
   - Token 等同于您的登录凭证
   - 任何人获得 Token 都可以访问您的 123 云盘账户
   - 不要将包含 Token 的代码上传到 GitHub 等公开平台

2. **定期更换 Token**
   - 建议每 30 天更换一次
   - 如怀疑 Token 泄露，立即在 123 云盘官网退出所有设备并重新登录

3. **使用环境变量存储敏感信息**
   - 避免在代码中硬编码 Token
   - 使用 `.gitignore` 排除配置文件

---

## 技术支持

如遇问题，请提供：
1. Python 版本 (`python --version`)
2. 完整的错误信息
3. 操作步骤复现方法

---

**最后更新**: 2026-04-13  
**脚本版本**: v1.0  
**作者**: Nagisa
