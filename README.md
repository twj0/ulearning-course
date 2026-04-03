# DGUT Ulearning 课程学习工具

东莞理工学院 Ulearning 平台课程学习管理工具，支持课程列表查询、视频资源管理和学习记录同步。

## 功能特性

- 课程列表管理（进行中/已完成/全部）
- 课程详情查看
- 视频资源列表查询
- 学习记录同步与视频完成
- 测试页答题记录保存与即时读分
- 教材级智能遍历与自动学习

## 项目结构

```
src/ulearning_course/
├── core/                    # 核心模块
│   ├── config.py           # 配置管理
│   ├── crypto.py           # DES 加密
│   └── auth.py             # 认证管理
├── api/                     # API 客户端
│   ├── base.py             # 基础客户端
│   ├── course_client.py    # 课程 API
│   ├── study_client.py     # 学习记录 API
│   └── behavior_client.py  # 行为打点 API
├── models/                  # 数据模型
│   ├── course.py           # 课程模型
│   ├── video.py            # 视频模型
│   └── study_record.py     # 学习记录模型
├── services/                # 业务服务
│   ├── course_service.py   # 课程服务
│   ├── answer_service.py   # 测试页答题服务
│   └── study_service.py    # 学习服务
└── cli/                     # 命令行入口
    └── main.py             # 主入口
```

## 安装

```bash
# 克隆项目
git clone https://gtihub.com/twj0/ulearning-course.git
cd ulearning-course

# 安装依赖
uv sync
```

## 配置

在项目根目录创建 `.env` 文件，设置认证 Token：
```env
cp .env.example .env
```

```env
AUTHORIZATION=your-token-value
```

从浏览器开发者工具中获取 `token` 或 `AUTHORIZATION` Cookie 的值，两者是相同的。

可选：也可以使用 `cookie.json5` 文件（兼容旧方式）：

```json
[
  {"name": "token", "value": "your-token-value"}
]
```

## 使用方法

### 命令行工具

说明：
- `list` 返回的是 LMS `course_instance_id`
- `list --with-textbook-id` 会额外解析并显示对应的 UA `textbook_id`
- `resolve-textbook` 用于把 `course_instance_id` 解析成 UA `textbook_id`
- `info`、`videos`、`complete`、`smart` 使用的是 UA `textbook_id`
- `smart` 会遍历整本教材，自动识别未完成视频与测试小节，依次执行“播放/同步/答题/同步”
- `smart` 也会识别纯内容小节（例如纯富文本/HTML 页面），并通过 `personal/sync` 完成这些页面
- `smart --force-tests` 会忽略测试小节已完成状态，重新提交测试页答题记录，适合修正历史错误分数
- `smart --video-retries <次数>` 可在单个视频同步失败后自动重试
- `smart --video-interval <秒数>` 可降低视频连续提交频率，适合远端连接不稳定时使用
- `smart --test-interval <秒数>` 可降低测试页连续提交频率，适合远端连接不稳定或批量重提场景
- `answer` 支持按 `--textbook-id --class-id --chapter-id` 或 `--item-id` 直接保存测试页答题记录
- `videos` 会逐个读取学习记录，并显示每个视频当前是 `✅ 已完成` 还是 `❌ 未完成`
- `complete` 会先读取真实学习记录，只处理当前第一个未完成视频；加 `--all` 时才会批量处理全部未完成视频
- `smart` 会自动跳过已完成视频和已完成测试小节，只处理当前仍未完成的内容
- `answer --chapter-id` 接收的是学习页 URL 中的目录层 `chapterId`，命令内部会自动映射到内部 `chapterNodeId`
- `answer --chapter-id` 会遍历该章节下全部测试小节，分别提交答题记录，并输出汇总分数与小节明细
- `--course-id` 仍可用，但现在仅作为 `--textbook-id` 的兼容别名
- 所谓的`<教材id>`(`textbook_id`)就是我们看到的课件的ID

```bash
# 列出课程
uv run python -c "import sys; sys.path.insert(0, 'src'); from ulearning_course.cli import cli; cli()" list
```
```bash
# 列出进行中课程
uv run python -c "import sys; sys.path.insert(0, 'src'); from ulearning_course.cli import cli; cli()" list --status in-progress
```
```bash
# 列出进行中课程并同步显示教材ID
uv run python -c "import sys; sys.path.insert(0, 'src'); from ulearning_course.cli import cli; cli()" list --status in-progress --with-textbook-id
```
```bash
# 列出已完成课程
uv run python -c "import sys; sys.path.insert(0, 'src'); from ulearning_course.cli import cli; cli()" list --status completed
```
```bash
# 通过课程实例ID解析教材ID
uv run python -c "import sys; sys.path.insert(0, 'src'); from ulearning_course.cli import cli; cli()" resolve-textbook --course-instance-id <课程实例ID>
```
```bash
# 查看课程详情
uv run python -c "import sys; sys.path.insert(0, 'src'); from ulearning_course.cli import cli; cli()" info --textbook-id <教材ID> --class-id <班级ID>
```
```bash
# 只查看某一章的深层结构（chapter / item / page / component）
uv run python -c "import sys; sys.path.insert(0, 'src'); from ulearning_course.cli import cli; cli()" info --textbook-id <教材ID> --class-id <班级ID> --chapter-id <URL中的chapterId>
```
```bash
# 列出课程视频
uv run python -c "import sys; sys.path.insert(0, 'src'); from ulearning_course.cli import cli; cli()" videos --textbook-id <教材ID> --class-id <班级ID>
```
```bash
# 完成单个未完成视频
uv run python -c "import sys; sys.path.insert(0, 'src'); from ulearning_course.cli import cli; cli()" complete --textbook-id <教材ID> --class-id <班级ID>
```
```bash
# 完成所有未完成视频
uv run python -c "import sys; sys.path.insert(0, 'src'); from ulearning_course.cli import cli; cli()" complete --textbook-id <教材ID> --class-id <班级ID> --all
```
```bash
# 智能遍历整本教材，自动完成未完成视频与测试页
uv run python -c "import sys; sys.path.insert(0, 'src'); from ulearning_course.cli import cli; cli()" smart --textbook-id <教材ID> --class-id <班级ID>
```
```bash
# 智能遍历整本教材，并在需要时附带 userName
uv run python -c "import sys; sys.path.insert(0, 'src'); from ulearning_course.cli import cli; cli()" smart --textbook-id <教材ID> --class-id <班级ID> --user-name <用户名>
```
```bash
# 智能遍历整本教材，并强制重提所有测试小节以修正历史分数
uv run python -c "import sys; sys.path.insert(0, 'src'); from ulearning_course.cli import cli; cli()" smart --textbook-id <教材ID> --class-id <班级ID> --force-tests
```
```bash
# 智能遍历整本教材，并给视频失败增加重试
uv run python -c "import sys; sys.path.insert(0, 'src'); from ulearning_course.cli import cli; cli()" smart --textbook-id <教材ID> --class-id <班级ID> --video-retries 3 --video-interval 2.0
```
```bash
# 智能遍历整本教材，强制重提测试，并放慢测试提交频率
uv run python -c "import sys; sys.path.insert(0, 'src'); from ulearning_course.cli import cli; cli()" smart --textbook-id <教材ID> --class-id <班级ID> --force-tests --test-interval 1.5
```
```bash
# 按 textbook/class/chapter 定位并保存该章节下全部测试小节的答题记录
uv run python -c "import sys; sys.path.insert(0, 'src'); from ulearning_course.cli import cli; cli()" answer --textbook-id <教材ID> --class-id <班级ID> --chapter-id <URL中的chapterId>
```
```bash
# 直接按 itemid 保存测试页答题记录
uv run python -c "import sys; sys.path.insert(0, 'src'); from ulearning_course.cli import cli; cli()" answer --item-id <小节ITEM_ID>
```
```bash
# 需要时手动附带 userName
uv run python -c "import sys; sys.path.insert(0, 'src'); from ulearning_course.cli import cli; cli()" complete --textbook-id <教材ID> --class-id <班级ID> --user-name <用户名>
```
```bash
# 兼容旧参数名（仍可用，但建议迁移）
uv run python -c "import sys; sys.path.insert(0, 'src'); from ulearning_course.cli import cli; cli()" info --course-id <教材ID> --class-id <班级ID>
```

### Python API

```python
import sys
sys.path.insert(0, 'src')

from ulearning_course.services import AnswerService, CourseService, StudyService

# 课程服务
course_service = CourseService()

# 获取进行中课程
courses = course_service.get_in_progress_courses()
for course in courses:
    print(f"{course['name']} (course_instance_id={course['id']})")

# 获取课程视频
textbook_id = 55892
course, videos = course_service.get_course_with_videos(textbook_id, class_id)
print(f"视频数量: {len(videos)}")

# 学习服务
study_service = StudyService()

# 检查视频状态
is_completed = study_service.check_video_status(videos[0])

# 完成视频（默认不发送 userName）
study_service.complete_video(videos[0], class_id, textbook_id)

# 需要时手动附带 userName
study_service.complete_video(videos[0], class_id, textbook_id, user_name="your-display-name")

# 测试页答题服务
answer_service = AnswerService()

# 按 itemid 保存答题记录并立即验证读分
result = answer_service.answer_item(2773463)
print(result["submitted_score"], result["readback_score"], result["matched"])
```

## 技术栈

- Python 3.11+
- requests - HTTP 请求
- pycryptodome - DES 加密
- python-dotenv - 环境变量管理

## API 文档

详细的 API 文档位于 `docs/network/` 目录：

| 文档 | 说明 |
|------|------|
| `01-api-overview-and-domain-model.md` | API 概览与领域模型 |
| `02-api-course-directory-and-content.md` | 课程目录与内容接口 |
| `03-api-study-record-and-sync.md` | 学习记录与同步接口 |
| `04-api-video-playback-and-behavior.md` | 视频播放与行为打点 |
| `12-api-test-page-and-question-answer.md` | 测试页答案接口与提交链路 |
| `13-test-page-record-data-model.md` | 测试页记录在本项目中的数据模型建议 |
