"""
命令行主入口
"""

import argparse

from ..services import AnswerService, CourseService, SmartService, StudyService


def cli():
    parser = argparse.ArgumentParser(
        description="DGUT Ulearning 课程学习工具",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    list_parser = subparsers.add_parser("list", help="列出课程")
    list_parser.add_argument("--status", choices=["all", "in-progress", "completed"], default="in-progress", help="课程状态筛选")
    list_parser.add_argument("--with-textbook-id", action="store_true", help="同时解析并显示教材ID")
    
    resolve_parser = subparsers.add_parser("resolve-textbook", help="通过课程实例ID解析教材ID")
    resolve_parser.add_argument("--course-instance-id", type=int, required=True, help="课程实例ID（LMS ocId）")
    
    info_parser = subparsers.add_parser("info", help="查看课程详情")
    info_parser.add_argument("--textbook-id", "--course-id", dest="textbook_id", type=int, required=True, help="教材ID（兼容旧参数 --course-id）")
    info_parser.add_argument("--class-id", type=int, required=True, help="班级ID")
    
    videos_parser = subparsers.add_parser("videos", help="列出课程视频")
    videos_parser.add_argument("--textbook-id", "--course-id", dest="textbook_id", type=int, required=True, help="教材ID（兼容旧参数 --course-id）")
    videos_parser.add_argument("--class-id", type=int, required=True, help="班级ID")
    
    complete_parser = subparsers.add_parser("complete", help="完成视频学习")
    complete_parser.add_argument("--textbook-id", "--course-id", dest="textbook_id", type=int, required=True, help="教材ID（兼容旧参数 --course-id）")
    complete_parser.add_argument("--class-id", type=int, required=True, help="班级ID")
    complete_parser.add_argument("--user-name", help="用户名；未提供时默认不发送 userName 字段")
    complete_parser.add_argument("--all", action="store_true", help="完成所有未完成视频")

    smart_parser = subparsers.add_parser("smart", help="自动遍历整本教材并完成视频与测试页")
    smart_parser.add_argument("--textbook-id", "--course-id", dest="textbook_id", type=int, required=True, help="教材ID（兼容旧参数 --course-id）")
    smart_parser.add_argument("--class-id", type=int, required=True, help="班级ID")
    smart_parser.add_argument("--user-name", help="用户名；未提供时默认不发送 userName 字段")
    smart_parser.add_argument("--force-tests", action="store_true", help="即使测试小节已完成，也重新提交答题记录以修正分数")
    smart_parser.add_argument("--test-interval", type=float, default=0.8, help="测试小节提交间隔秒数，默认 0.8")

    answer_parser = subparsers.add_parser("answer", help="保存测试页答题记录")
    answer_parser.add_argument("--textbook-id", "--course-id", dest="textbook_id", type=int, help="教材ID（兼容旧参数 --course-id）")
    answer_parser.add_argument("--class-id", type=int, help="班级ID")
    answer_parser.add_argument("--chapter-id", type=int, help="学习页 URL 中的目录层 chapterId")
    answer_parser.add_argument("--item-id", type=int, help="直接指定小节 itemid")
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    main(args)


def main(args):
    if args.command == "list":
        list_courses(args)
    elif args.command == "resolve-textbook":
        resolve_textbook(args)
    elif args.command == "info":
        show_course_info(args)
    elif args.command == "videos":
        list_videos(args)
    elif args.command == "complete":
        complete_videos(args)
    elif args.command == "smart":
        run_smart(args)
    elif args.command == "answer":
        answer_tests(args)


def list_courses(args):
    print("=" * 80)
    print("课程列表")
    print("=" * 80)
    
    service = CourseService()
    
    if args.status == "all":
        courses = service.get_all_courses()
    elif args.status == "completed":
        courses = service.get_completed_courses()
    else:
        courses = service.get_in_progress_courses()
    
    for i, course in enumerate(courses, 1):
        line = (
            f"{i}. {course.get('name', '')} "
            f"(课程实例ID: {course.get('id')}, 班级ID: {course.get('classId')}"
        )
        if args.with_textbook_id:
            textbook_ids = resolve_textbook_ids_for_course(service, course.get("id"))
            line += f", 教材ID: {textbook_ids}"
        line += ")"
        print(line)
    
    print(f"\n共 {len(courses)} 门课程")


def resolve_textbook_ids_for_course(service: CourseService, course_instance_id: int | None) -> str:
    if course_instance_id is None:
        return "未解析到"
    
    textbooks = service.resolve_textbooks(course_instance_id)
    textbook_ids = [
        str(textbook.get("courseId"))
        for textbook in textbooks
        if textbook.get("courseId") is not None
    ]
    if not textbook_ids:
        return "未解析到"
    return ", ".join(textbook_ids)


def resolve_textbook(args):
    print("=" * 80)
    print(f"教材ID解析 (课程实例ID: {args.course_instance_id})")
    print("=" * 80)
    
    service = CourseService()
    textbooks = service.resolve_textbooks(args.course_instance_id)
    
    if not textbooks:
        print("⚠️ 未找到教材映射，可能课程不存在教材任务或当前账号无访问权限")
        print("提示：请确认课程实例ID是否正确，或先在 LMS 中打开该课程教材页")
        return
    
    for index, textbook in enumerate(textbooks, 1):
        print(f"{index}. 教材ID: {textbook.get('courseId', '')}")
        print(f"   教材名称: {textbook.get('name', '')}")
        print(f"   类型: {textbook.get('type', '')}")
        print(f"   状态: {textbook.get('status', '')}")
        print(f"   截止时间: {textbook.get('limit', '')}")
    
    print(f"\n共解析到 {len(textbooks)} 个教材")


def show_course_info(args):
    print("=" * 80)
    print(f"课程详情 (教材ID: {args.textbook_id})")
    print("=" * 80)
    
    service = CourseService()
    course = service.get_course(args.textbook_id, args.class_id)
    
    if not course.name:
        print("⚠️ 无法获取课程信息，可能课程不存在或无访问权限")
        print(f"提示：请确认教材ID {args.textbook_id} 和班级ID {args.class_id} 是否正确")
        print("提示：若手里是课程实例ID，请先运行 resolve-textbook 获取教材ID")
        return
    
    print(f"课程名称: {course.name}")
    print(f"章节数量: {len(course.chapters)}")
    
    if not course.chapters:
        print("\n⚠️ 课程暂无章节内容")
        return
    
    for chapter in course.chapters:
        print(f"\n{chapter.title}")
        for section in chapter.sections:
            print(f"  - {section.title} (itemid: {section.item_id})")


def list_videos(args):
    print("=" * 80)
    print(f"课程视频列表 (教材ID: {args.textbook_id})")
    print("=" * 80)
    
    service = CourseService()
    course, videos = service.get_course_with_videos(args.textbook_id, args.class_id)
    
    if not course.name:
        print("⚠️ 无法获取课程信息，可能课程不存在或无访问权限")
        print(f"提示：请确认教材ID {args.textbook_id} 和班级ID {args.class_id} 是否正确")
        print("提示：若手里是课程实例ID，请先运行 resolve-textbook 获取教材ID")
        return
    
    print(f"课程名称: {course.name}")
    print(f"视频数量: {len(videos)}")
    
    if not videos:
        print("\n⚠️ 课程暂无视频内容")
        return
    
    total_duration = sum(v.duration for v in videos)
    print(f"总时长: {total_duration} 秒 ({total_duration / 3600:.2f} 小时)")
    
    study_service = StudyService()
    
    for i, video in enumerate(videos, 1):
        is_completed = study_service.check_video_status(video)
        status = "✅ 已完成" if is_completed else "❌ 未完成"
        print(f"{i}. {video.title} ({video.duration}秒) - {status}")


def complete_videos(args):
    print("=" * 80)
    print(f"完成视频学习 (教材ID: {args.textbook_id})")
    print("=" * 80)
    
    service = CourseService()
    study_service = StudyService()
    
    course, videos = service.get_course_with_videos(args.textbook_id, args.class_id)
    
    if not course.name:
        print("⚠️ 无法获取课程信息，可能课程不存在或无访问权限")
        print(f"提示：请确认教材ID {args.textbook_id} 和班级ID {args.class_id} 是否正确")
        print("提示：若手里是课程实例ID，请先运行 resolve-textbook 获取教材ID")
        return
    
    if not videos:
        print(f"课程名称: {course.name}")
        print("⚠️ 课程暂无视频内容")
        return
    
    incomplete_videos = []
    for video in videos:
        if not study_service.check_video_status(video):
            incomplete_videos.append(video)
    
    print(f"课程名称: {course.name}")
    print(f"视频总数: {len(videos)}")
    print(f"未完成数: {len(incomplete_videos)}")
    
    if not incomplete_videos:
        print("\n所有视频已完成！")
        return
    
    if args.all:
        print(f"\n开始批量完成 {len(incomplete_videos)} 个视频...")
        success, fail = study_service.batch_complete_videos(
            incomplete_videos, args.class_id, args.textbook_id, args.user_name
        )
        print(f"\n完成！成功: {success}, 失败: {fail}")
    else:
        video = incomplete_videos[0]
        print(f"\n完成第一个未完成视频...")
        study_service.complete_video(video, args.class_id, args.textbook_id, args.user_name)


def answer_tests(args):
    print("=" * 80)
    print("保存测试页答题记录")
    print("=" * 80)

    service = AnswerService()

    try:
        if args.item_id is not None:
            result = service.answer_item(args.item_id)
            print(f"模式: itemid 直达")
        else:
            missing = [
                name
                for name, value in (
                    ("textbook-id", args.textbook_id),
                    ("class-id", args.class_id),
                    ("chapter-id", args.chapter_id),
                )
                if value is None
            ]
            if missing:
                print(f"⚠️ 缺少参数: {', '.join(missing)}")
                print("用法1: answer --item-id <ITEM_ID>")
                print("用法2: answer --textbook-id <TEXTBOOK_ID> --class-id <CLASS_ID> --chapter-id <CHAPTER_ID>")
                raise SystemExit(2)

            result = service.answer_chapter(
                args.textbook_id,
                args.class_id,
                args.chapter_id,
            )
            print(f"模式: chapter 定位")
            print(f"输入 textbookId: {args.textbook_id}")
            print(f"输入 classId: {args.class_id}")
            print(f"输入 chapterId: {args.chapter_id}")
            print(f"章节内测试小节数: {result.get('section_count', 0)}")

        print(f"映射 chapterNodeId: {result.get('chapter_node_id')}")
        print(f"章节标题: {result.get('chapter_title', '')}")
        print(f"测试页数量: {result.get('test_page_count', 0)}")
        print(f"题目总数: {result.get('question_count', 0)}")
        print(f"成功答题数: {result.get('answered_question_count', 0)}")
        print(f"提交前分数: {result.get('baseline_score', 0)}")
        print(f"提交分数: {result.get('submitted_score', 0)}")
        print(f"同步返回码: {result.get('sync_result')}")
        print(f"首次回读分数: {result.get('readback_score', 0)}")

        items = result.get("items")
        if items:
            print("\n小节明细:")
            for item in items:
                print(
                    f"- itemid={item.get('item_id')} | {item.get('item_title', '')} | "
                    f"页数={item.get('test_page_count', 0)} | 题数={item.get('question_count', 0)} | "
                    f"提交={item.get('submitted_score', 0)} | 回读={item.get('readback_score', 0)}"
                )
        else:
            print(f"目标 itemid: {result.get('item_id')}")
            print(f"小节标题: {result.get('item_title', '')}")

        if result.get("matched"):
            print("\n✅ 已完成测试页答题保存，首次回读分数与提交分数一致")
            return

        print("\n⚠️ 提交完成，但首次回读分数与提交分数不一致")
        raise SystemExit(1)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"❌ 保存测试页答题记录失败: {exc}")
        raise SystemExit(1) from exc


def run_smart(args):
    print("=" * 80)
    print("教材级智能学习")
    print("=" * 80)
    print(f"输入 textbookId: {args.textbook_id}")
    print(f"输入 classId: {args.class_id}")
    print(f"强制重提测试: {'是' if args.force_tests else '否'}")
    print(f"测试提交间隔: {args.test_interval:.1f} 秒")

    service = SmartService()

    try:
        result = service.run_textbook(
            args.textbook_id,
            args.class_id,
            args.user_name,
            force_tests=args.force_tests,
            test_interval_seconds=args.test_interval,
        )

        print(f"课程名称: {result.get('course_name', '')}")
        print(f"章节总数: {result.get('chapter_count', 0)}")
        print(f"视频总数: {result.get('video_count', 0)}")
        print(f"测试小节总数: {result.get('test_section_count', 0)}")

        chapters = result.get("chapters", [])
        if chapters:
            print("\n章节执行明细:")
            for chapter in chapters:
                print(
                    f"- chapterId={chapter.get('chapter_id')} | {chapter.get('chapter_title', '')} | "
                    f"视频 完成/跳过/失败={chapter.get('completed_videos', 0)}/{chapter.get('skipped_videos', 0)}/{chapter.get('failed_videos', 0)} | "
                    f"测试 完成/跳过/失败={chapter.get('completed_tests', 0)}/{chapter.get('skipped_tests', 0)}/{chapter.get('failed_tests', 0)}"
                )
                for video in chapter.get("videos", []):
                    if video.get("status") != "failed":
                        continue
                    print(
                        f"  视频失败: itemid={video.get('item_id')} videoid={video.get('video_id')} "
                        f"title={video.get('title', '')} error={video.get('error', 'unknown')}"
                    )
                for test in chapter.get("tests", []):
                    if test.get("status") != "failed":
                        continue
                    print(
                        f"  测试失败: itemid={test.get('item_id')} "
                        f"title={test.get('item_title', '')} error={test.get('error', 'unknown')}"
                    )

        print("\n教材汇总:")
        print(
            f"视频 完成/跳过/失败: "
            f"{result.get('completed_videos', 0)}/"
            f"{result.get('skipped_videos', 0)}/"
            f"{result.get('failed_videos', 0)}"
        )
        print(
            f"测试 完成/跳过/失败: "
            f"{result.get('completed_tests', 0)}/"
            f"{result.get('skipped_tests', 0)}/"
            f"{result.get('failed_tests', 0)}"
        )

        if result.get("success"):
            print("\n✅ 智能学习执行完成，未发现失败项")
            return

        print("\n⚠️ 智能学习执行结束，但存在失败项")
        raise SystemExit(1)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"❌ 智能学习执行失败: {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    cli()
