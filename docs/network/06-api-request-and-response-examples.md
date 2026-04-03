# DGUT Ulearning 接口请求与响应样例

## 1. 文档范围

本文档汇总当前已验证接口的典型请求样例、关键请求头及响应样例，便于后续接口复核、抓包对照与脚本开发。

## 2. 课程基础信息接口样例

### 2.1 请求定义

| 项目 | 内容 |
| --- | --- |
| 方法 | `GET` |
| URL | `https://ua.dgut.edu.cn/uaapi/course/55892/basicinformation` |

### 2.2 关键请求头

| 请求头 | 样例值 | 说明 |
| --- | --- | --- |
| `AUTHORIZATION` | `<token>` | 主认证头 |
| `UA-AUTHORIZATION` | `<token>` | UA 学习页认证头 |
| `Accept-Language` | `zh-CN,zh;q=0.9` | 语言环境 |
| `Referer` | `https://ua.dgut.edu.cn/learnCourse/learnCourse.html?...` | 来源页 |

### 2.3 响应样例

```json
{
  "course": {
    "courseid": 55892,
    "name": "（混合公选）机器的征途：空天科技",
    "orgid": 3755,
    "coursetype": 4,
    "establishdate": "2025-02-26 18:03:10",
    "modifydate": "2025-06-05 23:54:38"
  },
  "publishStatus": 0,
  "subjects": [],
  "isHideUrl": 0
}
```

## 3. 班级配置接口样例

### 3.1 请求定义

| 项目 | 内容 |
| --- | --- |
| 方法 | `GET` |
| URL | `https://ua.dgut.edu.cn/uaapi/classes/55892?classId=944483` |

### 3.2 响应样例

```json
{
  "classid": 944483,
  "takeAgain": 0,
  "showCorrect": 1
}
```

## 4. 课程目录接口样例

### 4.1 请求定义

| 项目 | 内容 |
| --- | --- |
| 方法 | `GET` |
| URL | `https://ua.dgut.edu.cn/uaapi/course/stu/55892/directory?classId=944483` |

### 4.2 响应片段

```json
{
  "coursename": "（混合公选）机器的征途：空天科技",
  "chapters": [
    {
      "nodetitle": "第一章 空天科技的起源与现状",
      "id": 136397207,
      "nodeid": 2581780,
      "items": [
        {
          "itemid": 2584634,
          "id": 136397208,
          "title": "第一节 古代人类“疯狂”而“美好”的飞天梦想",
          "coursepages": [
            {
              "relationid": 2584635,
              "id": 6848124,
              "title": "教学视频",
              "contentType": 6
            }
          ]
        }
      ]
    }
  ]
}
```

## 5. 章节页面详情接口样例

### 5.1 请求定义

| 项目 | 内容 |
| --- | --- |
| 方法 | `GET` |
| URL | `https://ua.dgut.edu.cn/uaapi/wholepage/chapter/stu/2581780` |

### 5.2 响应片段

```json
{
  "chapterid": 2581780,
  "wholepageItemDTOList": [
    {
      "itemid": 2584634,
      "wholepageDTOList": [
        {
          "contentType": 6,
          "id": 6848124,
          "content": "教学视频",
          "relationid": 2584635,
          "coursepageDTOList": [
            {
              "type": 4,
              "resourceid": 1717243,
              "resourceFullurl": "https://obscloud.ulearning.cn/resources/web/17405354188653939.mp4",
              "videoLength": 214,
              "resourceContentSize": 16318231
            }
          ]
        }
      ]
    }
  ]
}
```

## 6. 学习记录初始化接口样例

### 6.1 请求定义

| 项目 | 内容 |
| --- | --- |
| 方法 | `GET` |
| URL | `https://ua.dgut.edu.cn/uaapi/studyrecord/initialize/2584634` |

### 6.2 响应样例

```json
1775134119
```

## 7. 学习记录读取接口样例

### 7.1 请求定义

| 项目 | 内容 |
| --- | --- |
| 方法 | `GET` |
| URL | `https://ua.dgut.edu.cn/uaapi/studyrecord/item/2584634?courseType=4` |

### 7.2 响应说明

| 项目 | 说明 |
| --- | --- |
| 当前材料状态 | 已确认前端会调用该接口恢复历史记录 |
| 当前公开样例 | 未单独在文档中保留完整响应体 |
| 可恢复信息 | 页面完成状态、视频进度、累计观看记录 |

## 8. 心跳接口样例

### 8.1 请求定义

| 项目 | 内容 |
| --- | --- |
| 方法 | `GET` |
| URL | `https://ua.dgut.edu.cn/uaapi/studyrecord/heartbeat/2584634/1775134119` |

### 8.2 响应样例

```json
{
  "status": 0
}
```

## 9. 学习同步接口样例

### 9.1 请求定义

| 项目 | 内容 |
| --- | --- |
| 方法 | `POST` |
| URL | `https://ua.dgut.edu.cn/uaapi/yws/api/personal/sync?courseType=4&platform=PC` |
| Body 类型 | 加密字符串 |

### 9.2 典型请求头

| 请求头 | 样例值 | 说明 |
| --- | --- | --- |
| `Content-Type` | `application/json` | 请求体类型 |
| `AUTHORIZATION` | `<token>` | 认证头 |
| `Origin` | `https://ua.dgut.edu.cn` | 来源域名 |
| `Referer` | `https://ua.dgut.edu.cn/learnCourse/learnCourse.html?...` | 学习页来源 |

### 9.3 请求体样例

```text
+rydL4Ll3U+H04HRnrfI8L1vgYJivlRdz/bsowEmdj7nivosApeGLJTb21yJNa6KK...
```

### 9.4 解密后样例

```json
{
  "itemid": 2584634,
  "autoSave": 1,
  "withoutOld": null,
  "complete": 1,
  "studyStartTime": 1775134119,
  "userName": "<USER_NAME>",
  "score": 100,
  "pageStudyRecordDTOList": [
    {
      "pageid": 2584635,
      "complete": 1,
      "studyTime": 298,
      "score": 100,
      "answerTime": 1,
      "submitTimes": 0,
      "questions": [],
      "videos": [
        {
          "videoid": 1717243,
          "current": 0,
          "status": 1,
          "recordTime": 174.480233,
          "time": 214.480233,
          "startEndTimeList": [
            {
              "startTime": 1775134165,
              "endTime": 1775134187
            }
          ]
        }
      ],
      "speaks": []
    }
  ]
}
```

### 9.5 响应样例

```json
1
```

## 10. 视频行为打点接口样例

### 10.1 请求定义

| 项目 | 内容 |
| --- | --- |
| 方法 | `POST` |
| URL | `https://lms.dgut.edu.cn/courseapi/behavior/watchVideo` |
| Body 类型 | JSON |

### 10.2 请求体样例

```json
{
  "classId": 944483,
  "courseId": 55892,
  "chapterId": 2581780,
  "videoId": 1717243
}
```

### 10.3 关键请求头

| 请求头 | 样例值 |
| --- | --- |
| `Authorization` | `<token>` |
| `Content-Type` | `application/json` |
| `Origin` | `https://ua.dgut.edu.cn` |
| `Referer` | `https://ua.dgut.edu.cn/` |

## 11. MP4 媒体流接口样例

### 11.1 请求定义

| 项目 | 内容 |
| --- | --- |
| 方法 | `GET` |
| URL | `https://obscloud.ulearning.cn/resources/web/17405354188653939.mp4?token=<token>` |

### 11.2 典型请求头

| 请求头 | 样例值 |
| --- | --- |
| `Accept` | `video/webm,video/ogg,video/*;q=0.9,...` |
| `Range` | `bytes=2079443-` |
| `Origin` | `https://ua.dgut.edu.cn` |
| `Referer` | `https://ua.dgut.edu.cn/` |

### 11.3 典型响应头

| 响应头 | 样例值 |
| --- | --- |
| `Content-Type` | `video/mp4` |
| `Content-Length` | `6627834` |
| `Accept-Ranges` | `bytes` |
| `Content-Range` | `bytes 2079443-8707276/8707277` |
| `Server` | `Byte-nginx` |

## 12. 说明

| 项目 | 说明 |
| --- | --- |
| 文档用途 | 作为抓包样例对照，不作为接口稳定契约承诺 |
| 样例来源 | 当前已观察 HAR、实时接口调用及解密结果 |

## 13. 题目答案接口样例

### 13.1 请求定义

| 项目 | 内容 |
| --- | --- |
| 方法 | `GET` |
| URL | `https://ua.dgut.edu.cn/uaapi/questionAnswer/18692023?parentId=7023243` |

### 13.2 关键请求头

| 请求头 | 样例值 | 说明 |
| --- | --- | --- |
| `AUTHORIZATION` | `<token>` | UA 学习页认证头 |
| `UA-AUTHORIZATION` | `<token>` | UA 学习页附加认证头 |
| `Referer` | `https://ua.dgut.edu.cn/learnCourse/learnCourse.html?...` | 来源页 |

### 13.3 响应样例

```json
{
  "questionid": 18692023,
  "correctreply": "",
  "correctAnswerList": ["D"]
}
```

### 13.4 说明

| 项目 | 说明 |
| --- | --- |
| `parentId` 语义 | 测试页页面对象 ID，不是学习记录 `relationid` |
| 是否观察到请求体加密 | 否 |
| 是否观察到额外签名 | 否 |

## 14. 测试页学习记录读取样例

### 14.1 请求定义

| 项目 | 内容 |
| --- | --- |
| 方法 | `GET` |
| URL | `https://ua.dgut.edu.cn/uaapi/studyrecord/item/2693412?courseType=4` |

### 14.2 响应样例

```json
{
  "completion_status": 1,
  "learner_name": "<USER_NAME>",
  "activity_title": "第一章测试",
  "item_id": 2693412,
  "score": 90,
  "pageStudyRecordDTOList": [
    {
      "pageid": 2693413,
      "complete": 1,
      "studyTime": 2144,
      "score": 90,
      "answerTime": 1,
      "submitTimes": 1,
      "coursepageId": 7024037,
      "questions": [
        {
          "questionid": 18692023,
          "answerList": ["D"],
          "score": 1.0
        },
        {
          "questionid": 18692035,
          "answerList": ["false"],
          "score": 0.0
        }
      ],
      "videos": [],
      "speaks": []
    }
  ]
}
```

### 14.3 说明

| 项目 | 说明 |
| --- | --- |
| 题目结果落点 | `pageStudyRecordDTOList[].questions[]` |
| 提交次数落点 | `pageStudyRecordDTOList[].submitTimes` |
| 页面得分落点 | `pageStudyRecordDTOList[].score` |
| 练习组件 ID 落点 | `pageStudyRecordDTOList[].coursepageId` |
| 结论 | 测试页最终落库数据可通过 `studyrecord/item` 原样恢复 |

## 15. 测试页 `personal/sync` 样例

### 15.1 请求定义

| 项目 | 内容 |
| --- | --- |
| 方法 | `POST` |
| URL | `https://ua.dgut.edu.cn/uaapi/yws/api/personal/sync?courseType=4&platform=PC` |
| 来源样本 | `developer/network/ua.dgut.edu.cn_Archive [26-04-03 11-20-37].har` |

### 15.2 解密后请求体样例

```json
{
  "itemid": 2773380,
  "autoSave": 0,
  "withoutOld": 1,
  "complete": 1,
  "studyStartTime": 1775186156,
  "userName": "<USER_NAME>",
  "score": 0,
  "pageStudyRecordDTOList": [
    {
      "pageid": 2773381,
      "complete": 1,
      "studyTime": 264,
      "score": 0,
      "answerTime": 1,
      "submitTimes": 2,
      "coursepageId": 7242129,
      "questions": [
        {
          "questionid": 19548732,
          "answerList": ["B"],
          "score": 0
        },
        {
          "questionid": 19548733,
          "answerList": [],
          "score": 0
        },
        {
          "questionid": 19548734,
          "answerList": ["C"],
          "score": 0
        },
        {
          "questionid": 19548735,
          "answerList": ["D"],
          "score": 0
        }
      ],
      "videos": [],
      "speaks": []
    }
  ]
}
```

### 15.3 说明

| 项目 | 说明 |
| --- | --- |
| 这是视频还是测试页 | 测试页 |
| 是否携带题目结果 | 是，进入 `questions[]` |
| 是否携带提交次数 | 是，`submitTimes=2` |
| 是否携带组件 ID | 是，`coursepageId=7242129` |
| 语义 | 证明测试页最终也是通过 `personal/sync` 完成服务端持久化 |

