#!/usr/bin/env python3
"""Register Community MCP only when the user has requested Codex connection."""
import argparse
import json
import shutil
import sys
import subprocess
from pathlib import Path
sys.dont_write_bytecode = True  # Never mutate a signed app when loading its bundled Skill.
from noteford import discovery_file, load_record

NAME = 'noteford-community'


def configure(cli, record, run=subprocess.run):
    command = str(Path(record['command']).resolve())
    # Use the packaged service directly so Python does not become the MCP caller.
    if Path(command).name not in {'noteford-service', 'noteford-service.exe'} or record.get('args'):
        raise RuntimeError('请先安装并打开 Noteford 开源版安装包；不注册开发运行时。')
    args = ['--mcp-auto', '--client-name', 'Codex']

    def read():
        result = run([cli, 'mcp', 'list', '--json'], capture_output=True, text=True, check=True)
        return {item['name']: item for item in json.loads(result.stdout)}

    def matches(item):
        transport = item.get('transport', {})
        return (item.get('enabled', True) and transport.get('type') == 'stdio'
                and transport.get('command') == command and transport.get('args') == args
                and not transport.get('env') and not transport.get('env_vars')
                and not transport.get('cwd'))

    def stale_default(item):
        t = item.get('transport', {})
        old = Path(t.get('command', ''))
        # Only repair a missing default Community app; never another product,
        # a live alternate install, disabled entry or customized configuration.
        return (item.get('enabled', True) and t.get('type') == 'stdio'
                and old.name == 'noteford-service' and not old.exists()
                and old.parts[-5:] in {
                    ('Noteford 开源版.app', 'Contents', 'Resources', 'service', 'noteford-service'),
                    ('Noteford Community.app', 'Contents', 'Resources', 'service', 'noteford-service')}
                and t.get('args') == args and not t.get('env')
                and not t.get('env_vars') and not t.get('cwd')
                and all(item.get(k) is None for k in ('enabled_tools', 'disabled_tools', 'startup_timeout_sec', 'tool_timeout_sec')))

    before = read()
    repairing = False
    if NAME in before:
        if matches(before[NAME]):
            return 'already_configured'
        if not stale_default(before[NAME]):
            raise RuntimeError('同名 MCP 为自定义配置、仍有效的其他安装或已停用；保留原设置，请在客户端核对。')
        repairing = True
    run([cli, 'mcp', 'add', NAME, '--', command, *args], capture_output=True, text=True, check=True)
    after = read()
    if NAME not in after or not matches(after[NAME]):
        raise RuntimeError('注册后的配置与预期不符，请检查 Codex MCP 设置。')
    if {k: v for k, v in after.items() if k != NAME} != {k: v for k, v in before.items() if k != NAME}:
        raise RuntimeError('其他 MCP 配置发生变化，请检查；不自动覆盖恢复。')
    return 'repaired_stale_path' if repairing else 'configured'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--codex', help='Codex CLI 路径；默认从 PATH 查找')
    options = parser.parse_args()
    cli = options.codex or shutil.which('codex')
    if not cli:
        raise SystemExit('未找到 Codex CLI；请使用当前客户端提供的 MCP 添加入口，不修改其他客户端。')
    record = load_record(discovery_file())
    if sys.platform == 'darwin':
        app = Path(record['command']).parents[3]
        requirement = 'anchor apple generic and identifier "com.followhongyun.noteford.community" and certificate leaf[subject.OU] = "QD3H9VHB23"'
        subprocess.run(['/usr/bin/codesign', '--verify', '--deep', '--strict', '-R=' + requirement, str(app)], check=True, capture_output=True)
    result = configure(cli, record)
    print(json.dumps({'status': result, 'server': NAME, 'data_access_verified': False,
                      'next': '在 Codex 加载此 MCP；若当前会话没有工具，请重新打开客户端。首次访问在 Noteford 确认授权，再用原生 list_libraries 与 get_status 验证。注册成功不代表读取已通过。'}, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError, ValueError) as exc:
        raise SystemExit(str(exc))
