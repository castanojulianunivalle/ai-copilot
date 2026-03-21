"""
Proof of concept: Create small tasks per section and merge them into target task.
This strategy avoids ITEM_238 errors by keeping each task update small.
"""
from __future__ import annotations

import os
from datetime import date, datetime
from dotenv import load_dotenv

from daily_reporter.config import load_settings
from daily_reporter.clickup import ClickUpClient
from daily_reporter.jira import JiraIssue
from daily_reporter.report_builder import (
    PLANNING_START,
    PLANNING_END,
    SUMMARY_START,
    SUMMARY_END,
    FINAL_START,
    FINAL_END,
)
from daily_reporter.runtime import build_run_context


def extract_marker_content(markdown_content: str, start_marker: str, end_marker: str) -> str | None:
    """Extrae el contenido entre dos marcadores."""
    if start_marker not in markdown_content or end_marker not in markdown_content:
        return None
    start_idx = markdown_content.find(start_marker)
    end_idx = markdown_content.find(end_marker)
    if start_idx == -1 or end_idx == -1 or end_idx <= start_idx:
        return None
    start_content = start_idx + len(start_marker)
    content = markdown_content[start_content:end_idx].strip()
    return content


def main() -> int:
    print("=" * 70)
    print("Test: Merge Strategy - Create Small Tasks and Merge")
    print("=" * 70)
    
    # Load settings
    load_dotenv(override=False)
    settings = load_settings()
    
    if not settings.clickup_list_id:
        print("❌ ERROR: CLICKUP_LIST_ID not set in .env")
        return 1
    
    # HARDCODED: Task IDs that contain the header sections (purple callouts)
    # These tasks should already exist with the template headers
    # Note: "Status Rep #1" and "Status Rep #2" are COLUMNS in Planning & Execution, not separate sections
    SECTION_TASK_IDS = {
        "Planning": "86c7890v3",  # Planning & Execution section (includes table with Issue Link, Status Rep #1, Status Rep #2 columns)
        "Daily Summary": "86c789103",  # Daily Summary section (table with developer stats)
        "Final Summary": "86c78914f",  # Final Summary section
    }
    
    print(f"\n📋 List ID: {settings.clickup_list_id}")
    print(f"📅 Date: {date.today()}")
    print(f"⚙️  Phase: report1 (for testing)")
    print(f"\n📌 Section task IDs (hardcoded):")
    for name, task_id in SECTION_TASK_IDS.items():
        print(f"  - {name}: {task_id}")
    print()
    
    # Initialize client
    print("[1/4] Initializing ClickUp client...")
    clickup = ClickUpClient(token=settings.clickup_token)
    
    # Build context to get proper task title
    print("[2/4] Preparing context...")
    try:
        ctx = build_run_context(force_date=None, run_phase="report1")
        from daily_reporter.runtime import daily_task_title
        target_task_name = daily_task_title(ctx.today, ctx.phase)
        print(f"✅ Target task name: {target_task_name}")
    except Exception as e:
        print(f"❌ Failed to prepare context: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Create mock JIRA issues
    print("\n[3/5] Creating mock JIRA issues...")
    dev_fe = [
        JiraIssue(
            key="AIMMWEBUI-1570",
            url="https://pacificoutdoorliving.atlassian.net/browse/AIMMWEBUI-1570",
            summary="[Front] Implement External Link Button in Main Menu",
            issue_type="Task",
            status="In Progress",
            assignee="Camilo",
            created=datetime(2025, 12, 3, 10, 0),
            updated=datetime(2025, 12, 25, 14, 0),
            due_date=date(2025, 12, 20),
            original_estimate_seconds=1800,
            story_points=None,
            project_key="AIMMWEBUI",
        ),
        JiraIssue(
            key="AIMMWEBUI-1568",
            url="https://pacificoutdoorliving.atlassian.net/browse/AIMMWEBUI-1568",
            summary="[Front] Refactor GET Requests in GPMD View",
            issue_type="Task",
            status="Pending Review",
            assignee="Camilo",
            created=datetime(2025, 12, 3, 10, 0),
            updated=datetime(2025, 12, 25, 12, 0),
            due_date=None,
            original_estimate_seconds=3600,
            story_points=None,
            project_key="AIMMWEBUI",
        ),
    ]
    
    dev_be = [
        JiraIssue(
            key="AIMMWEBAPI-69",
            url="https://pacificoutdoorliving.atlassian.net/browse/AIMMWEBAPI-69",
            summary="Diagnose and Fix 500 Error on Estimate Creation",
            issue_type="Bug",
            status="Pending Review",
            assignee="Lautaro",
            created=datetime(2025, 12, 3, 10, 0),
            updated=datetime(2025, 12, 25, 13, 0),
            due_date=None,
            original_estimate_seconds=3600,
            story_points=None,
            project_key="AIMMWEBAPI",
        ),
    ]
    
    qa = []
    
    print(f"  ✅ Created {len(dev_fe)} Frontend, {len(dev_be)} Backend, {len(qa)} QA issues")
    
    # Build context
    print("\n[3/4] Building sections...")
    try:
        ctx = build_run_context(force_date=None, run_phase="report1")
        print(f"✅ Context prepared!")
        print(f"   Phase: {ctx.phase}")
        print(f"   Date: {ctx.today}")
    except Exception as e:
        print(f"❌ Failed to prepare context: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Build sections directly using the report builder functions
    print("\n[4/4] Building sections for merge strategy...")
    
    from daily_reporter.report_builder import (
        build_planning_rows_preserving_rep1,
        build_daily_summary_section,
        build_final_summary_section,
        _parse_planning_rows,
    )
    
    sections = []
    issues_all = dev_fe + dev_be + qa
    
    # Planning section - build directly (no existing rows since we're using merge strategy)
    existing_by_key = {}  # Empty for merge strategy
    planning_content = build_planning_rows_preserving_rep1(
        today=ctx.today,
        phase=ctx.phase,
        issues=issues_all,
        existing_rows_by_key=existing_by_key,
    )
    if planning_content and planning_content.strip():
        sections.append(("Planning", planning_content))
        print(f"  ✅ Planning section: {len(planning_content)} chars")
    else:
        print(f"  ⚠️  Planning section is empty")
    
    # Daily Summary section - build directly
    summary_content = build_daily_summary_section(today=ctx.today, issues_all=issues_all)
    if summary_content and summary_content.strip():
        sections.append(("Daily Summary", summary_content))
        print(f"  ✅ Daily Summary section: {len(summary_content)} chars")
    else:
        print(f"  ⚠️  Daily Summary section is empty")
    
    # Final Summary section (include for testing purposes, regardless of phase)
    # Note: Status Rep #1 and #2 are COLUMNS within Planning & Execution, not separate sections
    # For testing, we'll include Final Summary even in report1 phase
    final_content = build_final_summary_section(
        when_local=ctx.now_local.strftime("%Y-%m-%d %H:%M:%S %Z"),
        issues_all=issues_all,
        today=ctx.today,
    )
    if final_content and final_content.strip():
        sections.append(("Final Summary", final_content))
        print(f"  ✅ Final Summary section: {len(final_content)} chars")
    else:
        print(f"  ⚠️  Final Summary section is empty")
    
    print(f"\n  📊 Total sections to merge: {len(sections)}")
    
    # Show preview of each section
    if sections:
        print("\n  📝 Section previews:")
        for name, content in sections:
            preview = content[:100].replace("\n", " ")
            print(f"    [{name}]: {preview}...")
    
    if not sections:
        print("⚠️  No sections found. Cannot proceed with merge.")
        return 1
    
    # Map sections to their corresponding header task IDs
    section_to_header_task = {}
    for section_name, _ in sections:
        if section_name in SECTION_TASK_IDS:
            section_to_header_task[section_name] = SECTION_TASK_IDS[section_name]
        else:
            print(f"⚠️  Warning: No header task ID defined for section '{section_name}'")
    
    # Ask for confirmation
    print("\n" + "=" * 70)
    print("⚠️  READY TO CREATE AND MERGE TASKS")
    print("=" * 70)
    print(f"Target task name: {target_task_name}")
    print(f"\nStrategy:")
    print(f"  1. Create {len(sections)} small tasks with dynamic content only")
    print(f"  2. Duplicate header tasks and merge each content task into its duplicate")
    print(f"  3. Create target task with name: {target_task_name}")
    print(f"  4. Merge all duplicated header tasks into the target task")
    print("\nPress ENTER to continue, or Ctrl+C to cancel...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user.")
        return 1
    
    # Step 1: Create small tasks with dynamic content only
    print("\n[STEP 1] Creating small tasks with dynamic content...")
    content_task_ids: list[tuple[str, str]] = []  # [(section_name, task_id)]
    
    for i, (section_name, content) in enumerate(sections, 1):
        task_name = f"[CONTENT] {section_name} - {date.today().isoformat()}"
        print(f"\n[{i}/{len(sections)}] Creating content task: {section_name}")
        print(f"   Content length: {len(content)} characters")
        
        try:
            temp_task = clickup.create_task(
                list_id=settings.clickup_list_id,
                name=task_name,
                description=content,
                status="Report #1",
            )
            
            content_task_ids.append((section_name, temp_task.id))
            print(f"   ✅ Created: {temp_task.id} ({temp_task.url})")
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    if not content_task_ids:
        print("\n❌ No content tasks were created. Cannot proceed.")
        return 1
    
    print(f"\n✅ Created {len(content_task_ids)} content tasks")
    
    # Step 2: Duplicate header tasks (to preserve originals) and merge content into copies
    print("\n[STEP 2] Duplicating header tasks and merging content...")
    header_task_ids: list[str] = []
    
    for section_name, content_task_id in content_task_ids:
        if section_name not in section_to_header_task:
            print(f"⚠️  Skipping {section_name}: no header task ID defined")
            continue
        
        original_header_task_id = section_to_header_task[section_name]
        print(f"\n  Processing '{section_name}'...")
        print(f"    Original header task: {original_header_task_id}")
        print(f"    Content task: {content_task_id}")
        
        try:
            # Get original header task to get its name
            original_header_task = clickup.get_task(original_header_task_id)
            print(f"    ✅ Original header task found: {original_header_task.name}")
            
            # Duplicate the header task (to preserve the original)
            duplicate_name = f"[{date.today().isoformat()}] {section_name} - {original_header_task.name}"
            print(f"    Creating duplicate: {duplicate_name}")
            
            duplicate_header_task = clickup.copy_task_to_list(
                template_task_id=original_header_task_id,
                list_id=settings.clickup_list_id,
                new_name=duplicate_name,
            )
            print(f"    ✅ Duplicate created: {duplicate_header_task.id}")
            
            # Merge content task into the duplicate header task
            print(f"    Merging content into duplicate...")
            clickup.merge_tasks(
                target_task_id=duplicate_header_task.id,
                source_task_ids=[content_task_id],
            )
            print(f"    ✅ Content merged into duplicate!")
            
            header_task_ids.append(duplicate_header_task.id)
            
        except Exception as e:
            print(f"    ❌ Failed: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    if not header_task_ids:
        print("\n❌ No header tasks were merged. Cannot proceed to final merge.")
        return 1
    
    print(f"\n✅ Merged content into {len(header_task_ids)} header tasks")
    
    # Step 3: Create target task with correct name and merge all header tasks into it
    print(f"\n[STEP 3] Creating target task and merging all header tasks...")
    print(f"   Target task name: {target_task_name}")
    print(f"   Header tasks to merge: {', '.join(header_task_ids)}")
    
    try:
        # Create the target task with the correct name (it will be empty initially)
        target_task = clickup.create_task(
            list_id=settings.clickup_list_id,
            name=target_task_name,
            description="",  # Empty, will be filled by merge
            status="Report #1",
        )
        print(f"   ✅ Target task created: {target_task.id} ({target_task.url})")
        
        # Merge all header tasks (with content) into the target task
        clickup.merge_tasks(
            target_task_id=target_task.id,
            source_task_ids=header_task_ids,
        )
        print("✅ Final merge completed successfully!")
        
    except Exception as e:
        print(f"❌ Failed to create target task or merge: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n" + "=" * 70)
    print("✅ MERGE STRATEGY TEST COMPLETED!")
    print("=" * 70)
    print(f"📋 Target task: {target_task.url}")
    print(f"📋 Task name: {target_task_name}")
    print(f"\n💡 Summary:")
    print(f"  - Created {len(content_task_ids)} content tasks with dynamic data")
    print(f"  - Duplicated {len(header_task_ids)} header tasks (originals preserved)")
    print(f"  - Merged content into duplicated header tasks")
    print(f"  - Created target task with name: {target_task_name}")
    print(f"  - Merged all header tasks (with content) into target task")
    print(f"  - Target task now contains all sections with headers and content")
    print(f"\n⚠️  Note:")
    print(f"  - Content tasks have been merged (no longer exist)")
    print(f"  - Duplicated header tasks have been merged (no longer exist)")
    print(f"  - Original header tasks remain intact (can be reused)")
    print(f"  - Only the target task remains with complete content")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

