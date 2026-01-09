import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from app.services.comment_rephraser import CommentRephraser
from app.models.rephrase_schemas import ReviewStatus

def run_checks():
    print("🧪 Starting AI Intent Verification...")
    rephraser = CommentRephraser()
    
    # 1. Test SUBMIT Intent
    print("   - Verifying SUBMIT intent...", end=" ")
    prompt_submit = rephraser._build_prompt(
        input_text="looks good",
        status=ReviewStatus.SUBMIT,
        expanded_text="looks good"
    )
    if "Use positive, confirming language" in prompt_submit and "STATUS: SUBMIT" in prompt_submit:
        print("✅ PASS")
    else:
        print("❌ FAIL")
        print(prompt_submit)
        return

    # 2. Test REVISE Intent
    print("   - Verifying REVISE intent...", end=" ")
    prompt_revise = rephraser._build_prompt(
        input_text="bad dims",
        status=ReviewStatus.REVISE,
        expanded_text="bad dimensions"
    )
    if "Use constructive, helpful language" in prompt_revise and "STATUS: REVISE" in prompt_revise:
        print("✅ PASS")
    else:
        print("❌ FAIL")
        return

    # 3. Test COMMENT Intent
    print("   - Verifying COMMENT intent...", end=" ")
    prompt_comment = rephraser._build_prompt(
        input_text="check grid",
        status=ReviewStatus.COMMENT,
        expanded_text="check grid"
    )
    if "Use neutral, informative language" in prompt_comment and "STATUS: COMMENT" in prompt_comment:
        print("✅ PASS")
    else:
        print("❌ FAIL")
        return

    # 4. Test Thread Context
    print("   - Verifying Thread Context...", end=" ")
    history = [
        {"user_name": "Alice", "status": "REVISE", "text": "Fix this."},
        {"user_name": "Bob", "status": "COMMENT", "text": "On it."}
    ]
    prompt_thread = rephraser._build_prompt(
        input_text="done",
        status=ReviewStatus.SUBMIT,
        expanded_text="done",
        thread_history=history
    )
    if 'Alice: "Fix this."' in prompt_thread and 'Bob: "On it."' in prompt_thread:
        print("✅ PASS")
    else:
        print("❌ FAIL")
        print(prompt_thread)
        return

    print("\n✨ All AI Intent Checks Passed!")

if __name__ == "__main__":
    run_checks()
