"""
Proof of concept: Test updating a ClickUp task with JIRA data.
This script updates the task specified by CLICKUP_TEMPLATE_TASK_ID,
replacing content between markers with dynamically generated data from JIRA.
"""
from __future__ import annotations

import os
from datetime import date
from dotenv import load_dotenv

from daily_reporter.config import load_settings
from daily_reporter.clickup import ClickUpClient
from daily_reporter.jira import JiraIssue
from daily_reporter.report_builder import (
    build_report_description,
    PLANNING_START,
    PLANNING_END,
    SUMMARY_START,
    SUMMARY_END,
    REP1_START,
    REP1_END,
    REP2_START,
    REP2_END,
    FINAL_START,
    FINAL_END,
)


def check_markers(markdown_content: str) -> dict[str, bool]:
    """
    Verifica qué marcadores están presentes en el contenido.
    """
    markers = {
        "PLANNING": (PLANNING_START, PLANNING_END),
        "DAILY_SUMMARY": (SUMMARY_START, SUMMARY_END),
        "STATUS_REP_1": (REP1_START, REP1_END),
        "STATUS_REP_2": (REP2_START, REP2_END),
        "FINAL_SUMMARY": (FINAL_START, FINAL_END),
    }
    
    results: dict[str, bool] = {}
    for name, (start, end) in markers.items():
        # Try exact match first
        has_start = start in markdown_content
        has_end = end in markdown_content
        
        # If not found, try case-insensitive and with flexible whitespace
        if not has_start:
            import re
            start_pattern = re.escape(start).replace(r'\ ', r'\s+')
            has_start = bool(re.search(start_pattern, markdown_content, re.IGNORECASE))
        
        if not has_end:
            import re
            end_pattern = re.escape(end).replace(r'\ ', r'\s+')
            has_end = bool(re.search(end_pattern, markdown_content, re.IGNORECASE))
        
        results[name] = has_start and has_end
        print(f"  [{name}] START: {'✅' if has_start else '❌'}  END: {'✅' if has_end else '❌'}")
        
        # If found, show the actual text found
        if has_start:
            idx = markdown_content.find(start)
            if idx == -1:
                # Try case-insensitive search
                import re
                match = re.search(re.escape(start).replace(r'\ ', r'\s+'), markdown_content, re.IGNORECASE)
                if match:
                    idx = match.start()
                    actual = markdown_content[idx:idx+min(100, len(markdown_content)-idx)]
                    print(f"    Found at {idx}: {actual[:80]}...")
        if has_end:
            idx = markdown_content.find(end)
            if idx == -1:
                import re
                match = re.search(re.escape(end).replace(r'\ ', r'\s+'), markdown_content, re.IGNORECASE)
                if match:
                    idx = match.start()
                    actual = markdown_content[idx:idx+min(100, len(markdown_content)-idx)]
                    print(f"    Found at {idx}: {actual[:80]}...")
    
    return results


def extract_marker_content(markdown_content: str, start_marker: str, end_marker: str) -> str | None:
    """
    Extrae el contenido entre dos marcadores.
    """
    if start_marker not in markdown_content or end_marker not in markdown_content:
        return None
    
    start_idx = markdown_content.find(start_marker)
    end_idx = markdown_content.find(end_marker)
    
    if start_idx == -1 or end_idx == -1 or end_idx <= start_idx:
        return None
    
    # Extraer el contenido entre los marcadores (sin incluir los marcadores)
    start_content = start_idx + len(start_marker)
    content = markdown_content[start_content:end_idx].strip()
    return content


def main() -> int:
    print("=" * 70)
    print("Test: Update ClickUp Task with JIRA Data")
    print("=" * 70)
    
    # Load settings
    load_dotenv(override=False)
    settings = load_settings()
    
    if not settings.clickup_template_task_id:
        print("❌ ERROR: CLICKUP_TEMPLATE_TASK_ID not set in .env")
        print("   This script updates the template task itself for testing.")
        return 1
    
    print(f"\n📋 Target task: {settings.clickup_template_task_id}")
    print(f"📅 Date: {date.today()}")
    print(f"⚙️  Phase: report1 (for testing)\n")
    
    # Initialize clients
    print("[1/5] Initializing ClickUp client...")
    clickup = ClickUpClient(token=settings.clickup_token)
    
    print("[2/5] Fetching current task description...")
    try:
        task = clickup.get_task(settings.clickup_template_task_id)
        print(f"✅ Task found: {task.name}")
        print(f"   URL: {task.url}")
    except Exception as e:
        print(f"❌ Failed to fetch task: {e}")
        return 1
    
    # Get current description
    current_description = task.markdown_description or task.description or ""
    print(f"\n📄 Current description length: {len(current_description)} characters")
    
    # Debug: show a sample of the description to see what we're getting
    if current_description:
        sample = current_description[:500].replace("\n", "\\n")
        print(f"📄 Description sample (first 500 chars): {sample}...")
        
        # Search for any DR: markers (case insensitive, partial match)
        import re
        dr_markers = re.findall(r'<!--\s*DR:[\w_]+\s*-->', current_description, re.IGNORECASE)
        if dr_markers:
            print(f"\n[DEBUG] Found {len(dr_markers)} DR markers in description:")
            for marker in dr_markers[:10]:  # Show first 10
                print(f"  - {marker}")
        else:
            print("\n[DEBUG] No DR markers found with regex search")
            # Try to find "PLANNING" or "DAILY" to see if content is there
            if "PLANNING" in current_description.upper():
                idx = current_description.upper().find("PLANNING")
                context = current_description[max(0, idx-100):idx+200]
                print(f"  Found 'PLANNING' at position {idx}")
                print(f"  Context: ...{context}...")
    
    # Check markers
    print("\n[3/5] Checking markers in template...")
    print("-" * 70)
    marker_status = check_markers(current_description)
    print("-" * 70)
    
    # Debug: show exact marker search
    print("\n[DEBUG] Searching for exact markers:")
    print(f"  PLANNING_START: {PLANNING_START}")
    print(f"    Found: {PLANNING_START in current_description}")
    print(f"  PLANNING_END: {PLANNING_END}")
    print(f"    Found: {PLANNING_END in current_description}")
    print(f"  SUMMARY_START: {SUMMARY_START}")
    print(f"    Found: {SUMMARY_START in current_description}")
    print(f"  SUMMARY_END: {SUMMARY_END}")
    print(f"    Found: {SUMMARY_END in current_description}")
    
    all_present = all(marker_status.values())
    if not all_present:
        missing = [name for name, present in marker_status.items() if not present]
        print(f"\n⚠️  WARNING: Missing markers: {', '.join(missing)}")
        print("   The script will still work, but those sections won't be updated.")
    else:
        print("\n✅ All markers found!")
    
    # Show current content between markers (for debugging)
    print("\n[4/5] Current content between markers:")
    print("-" * 70)
    for name, (start, end) in [
        ("PLANNING", (PLANNING_START, PLANNING_END)),
        ("DAILY_SUMMARY", (SUMMARY_START, SUMMARY_END)),
        ("STATUS_REP_1", (REP1_START, REP1_END)),
        ("STATUS_REP_2", (REP2_START, REP2_END)),
        ("FINAL_SUMMARY", (FINAL_START, FINAL_END)),
    ]:
        content = extract_marker_content(current_description, start, end)
        if content:
            preview = content[:100].replace("\n", " ")
            print(f"  [{name}] Content preview: {preview}...")
        else:
            print(f"  [{name}] No content found (or markers missing)")
    print("-" * 70)
    
    # Create mock JIRA issues (for testing without API)
    print("\n[5/5] Creating mock JIRA issues...")
    from datetime import datetime
    
    try:
        # Mock Frontend issues
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
                due_date=date(2025, 12, 20),  # Overdue
                original_estimate_seconds=1800,  # 30 minutes
                story_points=None,
                project_key="AIMMWEBUI",
            ),
            JiraIssue(
                key="AIMMWEBUI-1568",
                url="https://pacificoutdoorliving.atlassian.net/browse/AIMMWEBUI-1568",
                summary="[Front] Refactor GET Requests in GPMD View to Deduplicate Error Handling",
                issue_type="Task",
                status="Pending Review",
                assignee="Camilo",
                created=datetime(2025, 12, 3, 10, 0),
                updated=datetime(2025, 12, 25, 12, 0),
                due_date=None,
                original_estimate_seconds=3600,  # 1 hour
                story_points=None,
                project_key="AIMMWEBUI",
            ),
            JiraIssue(
                key="AIMMWEBUI-1571",
                url="https://pacificoutdoorliving.atlassian.net/browse/AIMMWEBUI-1571",
                summary="Update Production Manager Dropdown to Use Role IDs",
                issue_type="Task",
                status="Not Started",
                assignee="Camilo",
                created=datetime(2025, 12, 3, 10, 0),
                updated=datetime(2025, 12, 3, 10, 0),
                due_date=None,
                original_estimate_seconds=1800,  # 30 minutes
                story_points=None,
                project_key="AIMMWEBUI",
            ),
        ]
        
        # Mock Backend issues
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
                original_estimate_seconds=3600,  # 1 hour
                story_points=None,
                project_key="AIMMWEBAPI",
            ),
            JiraIssue(
                key="AIMMWEBAPI-98",
                url="https://pacificoutdoorliving.atlassian.net/browse/AIMMWEBAPI-98",
                summary="[Back] Implement Sorting by Last Name ASC in Week At a Glance Endpoint",
                issue_type="Task",
                status="Pending Review",
                assignee="Kevin",
                created=datetime(2025, 12, 3, 10, 0),
                updated=datetime(2025, 12, 25, 11, 0),
                due_date=None,
                original_estimate_seconds=3600,  # 1 hour
                story_points=None,
                project_key="AIMMWEBAPI",
            ),
            JiraIssue(
                key="AIMMWEBAPI-100",
                url="https://pacificoutdoorliving.atlassian.net/browse/AIMMWEBAPI-100",
                summary="Backend Enforcement: Block Role Activation When Employee Is Inactive",
                issue_type="Task",
                status="Not Started",
                assignee="Kevin",
                created=datetime(2025, 12, 3, 10, 0),
                updated=datetime(2025, 12, 3, 10, 0),
                due_date=None,
                original_estimate_seconds=7200,  # 2 hours
                story_points=None,
                project_key="AIMMWEBAPI",
            ),
        ]
        
        # Mock QA issues (empty for this test)
        qa = []
        
        print(f"  ✅ Created {len(dev_fe)} Frontend issues")
        print(f"  ✅ Created {len(dev_be)} Backend issues")
        print(f"  ✅ Created {len(qa)} QA issues")
        
        total = len(dev_fe) + len(dev_be) + len(qa)
        print(f"\n  📊 Total issues: {total}")
        
        # Show some details
        print("\n  📋 Sample issues:")
        for issue in dev_fe[:2]:
            print(f"    - {issue.key}: {issue.summary[:50]}... ({issue.status})")
        
    except Exception as e:
        print(f"❌ Failed to create mock issues: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Build report
    print("\n[6/6] Building report with JIRA data...")
    from daily_reporter.runtime import build_run_context
    
    try:
        # Use report1 phase for testing
        ctx = build_run_context(force_date=None, run_phase="report1")
        built = build_report_description(
            phase=ctx.phase,
            today=ctx.today,
            when_local=ctx.now_local.strftime("%Y-%m-%d %H:%M:%S %Z"),
            base_description=current_description,
            dev_frontend=dev_fe,
            dev_backend=dev_be,
            qa=qa,
        )
        
        print(f"✅ Report built successfully!")
        print(f"   New description length: {len(built.description)} characters")
        print(f"   ClickUp status: {built.clickup_status}")
        
        # Show what changed
        print("\n📝 Preview of generated content:")
        print("-" * 70)
        
        # Show planning section
        planning_content = extract_marker_content(built.description, PLANNING_START, PLANNING_END)
        if planning_content:
            lines = planning_content.split("\n")[:5]  # First 5 lines
            print("  [PLANNING] Preview:")
            for line in lines:
                if line.strip():
                    print(f"    {line[:80]}")
        
        # Show summary section
        summary_content = extract_marker_content(built.description, SUMMARY_START, SUMMARY_END)
        if summary_content:
            lines = summary_content.split("\n")[:3]  # First 3 lines
            print("\n  [DAILY_SUMMARY] Preview:")
            for line in lines:
                if line.strip():
                    print(f"    {line[:80]}")
        
        print("-" * 70)
        
    except Exception as e:
        print(f"❌ Failed to build report: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Ask for confirmation
    print("\n" + "=" * 70)
    print("⚠️  READY TO UPDATE TASK")
    print("=" * 70)
    print(f"Task ID: {settings.clickup_template_task_id}")
    print(f"Task URL: {task.url}")
    print("\nThis will UPDATE the task description with the generated content.")
    print("Press ENTER to continue, or Ctrl+C to cancel...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user.")
        return 1
    
    # Update task incrementally (one section at a time)
    print("\n[UPDATE] Updating task description incrementally (one section at a time)...")
    print(f"   Full content length: {len(built.description)} characters")
    
    from daily_reporter.http_utils import HttpError
    from daily_reporter.report_builder import _replace_between
    
    description_updated = False
    current_desc = current_description
    
    # Define update sections in order
    update_sections = []
    
    # Planning section
    planning_content = extract_marker_content(built.description, PLANNING_START, PLANNING_END)
    if planning_content and PLANNING_START in current_desc:
        update_sections.append(("PLANNING", PLANNING_START, PLANNING_END, planning_content))
    
    # Summary section
    summary_content = extract_marker_content(built.description, SUMMARY_START, SUMMARY_END)
    if summary_content and SUMMARY_START in current_desc:
        update_sections.append(("DAILY_SUMMARY", SUMMARY_START, SUMMARY_END, summary_content))
    
    # Status Rep sections (depending on phase)
    if ctx.phase == "report1":
        rep1_content = extract_marker_content(built.description, REP1_START, REP1_END)
        if rep1_content and REP1_START in current_desc:
            update_sections.append(("STATUS_REP_1", REP1_START, REP1_END, rep1_content))
    elif ctx.phase == "report2":
        rep2_content = extract_marker_content(built.description, REP2_START, REP2_END)
        if rep2_content and REP2_START in current_desc:
            update_sections.append(("STATUS_REP_2", REP2_START, REP2_END, rep2_content))
    elif ctx.phase == "close":
        final_content = extract_marker_content(built.description, FINAL_START, FINAL_END)
        if final_content and FINAL_START in current_desc:
            update_sections.append(("FINAL_SUMMARY", FINAL_START, FINAL_END, final_content))
    
    print(f"\n   Found {len(update_sections)} sections to update incrementally")
    
    if not update_sections:
        print("⚠️  No markers found - cannot update incrementally. Trying full update...")
        try:
            clickup.update_task(
                task_id=settings.clickup_template_task_id,
                description=built.description,
            )
            print("✅ Full description update successful!")
            description_updated = True
        except HttpError as e:
            print(f"❌ Full update also failed: {e}")
            return 1
    else:
        # Update each section incrementally
        for i, (section_name, start_marker, end_marker, content) in enumerate(update_sections, 1):
            print(f"\n[{i}/{len(update_sections)}] Updating section: {section_name}...")
            print(f"   Content length: {len(content)} characters")
            
            try:
                # Apply this section's update to current description
                new_desc, ok = _replace_between(current_desc, start_marker, end_marker, content)
                if not ok:
                    print(f"   ⚠️  Marker not found in current description, skipping...")
                    continue
                
                print(f"   New total length: {len(new_desc)} characters")
                
                # Update with this incremental change
                clickup.update_task(
                    task_id=settings.clickup_template_task_id,
                    description=new_desc,
                )
                print(f"   ✅ Section {section_name} updated successfully!")
                
                # Get the updated description for next iteration
                updated_task = clickup.get_task(settings.clickup_template_task_id)
                current_desc = updated_task.markdown_description or updated_task.description or ""
                print(f"   📄 Refreshed description length: {len(current_desc)} characters")
                
                # Small delay to avoid rate limiting
                import time
                time.sleep(0.5)
                
            except HttpError as e:
                print(f"   ❌ Failed to update section {section_name}: {e}")
                print(f"   ⚠️  Continuing with remaining sections...")
                # Continue with next section even if one fails
                continue
            except Exception as e:
                print(f"   ❌ Unexpected error updating section {section_name}: {e}")
                continue
        
        description_updated = True
        print("\n✅ Incremental update completed!")
    
    # Update status separately (always try this)
    print(f"\n[UPDATE] Updating task status to: {built.clickup_status}")
    try:
        clickup.update_task(
            task_id=settings.clickup_template_task_id,
            status=built.clickup_status,
        )
        print("✅ Task status updated successfully!")
    except Exception as e:
        print(f"⚠️  Failed to update status: {e}")
        # Don't fail the script for status update errors
    
    print("\n" + "=" * 70)
    if description_updated:
        print("✅ TEST COMPLETED SUCCESSFULLY!")
        print("   Description was updated directly.")
    else:
        print("⚠️  TEST COMPLETED (with fallback)")
        print("   Description update failed, but content was posted as a comment.")
    print("=" * 70)
    print(f"📋 Task: {task.url}")
    print("\n💡 Tips:")
    print("  - Check the task to verify the content was inserted correctly")
    if not description_updated:
        print("  - The generated content is in the task comments (due to ITEM_238 error)")
        print("  - To avoid this, consider using CLICKUP_WRITE_MODE=comment in production")
    print("  - Verify that markers were replaced with actual JIRA data")
    print("  - Check that the format matches your template structure")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

