def show_final_dialog(
    file_name: str,
    highlight_count: int,
    json_status: str | None = None,      # "success", "warning", "failed", or None if skipped
    csv_status: str | None = None,
    md_status: str | None = None,
    success_count: int = 0,
    issue_count: int = 0,
    fail_count: int = 0,
    elapsed_sec: float = 0.0,
):
    """Show a macOS dialog summarizing the run.

    Falls back to printing to stdout if osascript is unavailable.
    """
    import subprocess

    # Format elapsed time as Xm Ys
    time_min = int(elapsed_sec // 60)
    time_sec = int(elapsed_sec % 60)
    time_str = f"{time_min}m {time_sec}s" if time_min else f"{time_sec}s"

    # Build message body
    lines: list[str] = []
    lines.append("PDF Highlight Extraction Summary\n")
    lines.append(f"📄 File Name: {file_name}")
    lines.append(f"🔦 Highlights exported: {highlight_count}\n")

    if json_status:
        lines.append(f"🗒️ JSON exported:       {json_status}")
    if csv_status:
        lines.append(f"📊 CSV exported:        {csv_status}")
    if md_status:
        lines.append(f"📑 Markdown exported:   {md_status}")
    lines.append("")

    if success_count:
        lines.append(f"✅ Files processed successfully: {success_count}")
    if issue_count:
        lines.append(f"⚠️ Files with issues: {issue_count}")
    if fail_count:
        lines.append(f"❌ Files failed: {fail_count}")
    lines.append("")
    lines.append(f"🕒 Time elapsed: {time_str}")

    body = "\n".join(lines)

    # Escape for AppleScript string literal
    body_escaped = body.replace("\\", "\\\\").replace('"', '\\"')

    applescript = (
        f'display dialog "{body_escaped}" '
        f'buttons {{"OK"}} default button "OK" '
        f'with title "PDF Highlight Extraction"'
    )

    try:
        subprocess.run(["osascript", "-e", applescript], check=False)
    except Exception:
        # Fallback: just print to terminal
        print("\n=== PDF Highlight Extraction Summary ===\n")
        print(body)

