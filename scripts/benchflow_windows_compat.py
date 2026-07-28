#!/usr/bin/env python3
"""Launch BenchFlow with POSIX container paths on Windows hosts.

BenchFlow 0.6.3 derives Dockerfile symlink parents with ``pathlib.Path``.
On Windows that turns paths such as ``/root/.agents/skills`` into backslash
paths, which are invalid inside the Linux task image. Keep host paths native
and patch only the Dockerfile skill-injection helper.
"""

from __future__ import annotations

import base64
import os
import posixpath
import shutil
import shlex
from pathlib import Path, PurePosixPath


CODEX_ACP_DIST = (
    "/opt/benchflow/js-agents/lib/node_modules/"
    "@agentclientprotocol/codex-acp/dist/index.js"
)
CODEX_ACP_PATCH_MARKER = "BenchFlow configured-model compatibility"
CODEX_ACP_PATCH_JS = rf"""
const fs = require("node:fs");
const path = {CODEX_ACP_DIST!r};
const marker = {CODEX_ACP_PATCH_MARKER!r};
let source = fs.readFileSync(path, "utf8");
if (!source.includes(marker)) {{
  const before = `  async fetchAvailableModels() {{
    const models = [];
    let cursor = null;
    do {{
      const response = await this.codexClient.listModels({{ cursor, limit: null }});
      models.push(...response.data);
      cursor = response.nextCursor;
    }} while (cursor);
    return models;
  }}`;
  const after = `  async fetchAvailableModels() {{
    const models = [];
    let cursor = null;
    do {{
      const response = await this.codexClient.listModels({{ cursor, limit: null }});
      models.push(...response.data);
      cursor = response.nextCursor;
    }} while (cursor);
    // {CODEX_ACP_PATCH_MARKER}: expose the configured custom-provider model.
    const configuredModel = this.config?.model;
    if (configuredModel && !models.some((model) => model.id === configuredModel)) {{
      const template = models.find((model) => model.isDefault) ?? models[0];
      if (template) {{
        models.unshift({{
          ...template,
          id: configuredModel,
          displayName: configuredModel,
          isDefault: true
        }});
      }}
    }}
    return models;
  }}`;
  if (!source.includes(before)) {{
    throw new Error("Unsupported codex-acp build: model-list patch target missing");
  }}
  source = source.replace(before, after);
  fs.writeFileSync(path, source);
}}
""".strip()


def codex_acp_patch_command() -> str:
    encoded = base64.b64encode(CODEX_ACP_PATCH_JS.encode("utf-8")).decode("ascii")
    patch_path = "/tmp/benchflow-codex-acp-model-patch.cjs"
    node = "/opt/benchflow/node/bin/node"
    return (
        f"echo {encoded} | base64 -d > {patch_path} && "
        f"{node} {patch_path} && rm -f {patch_path}"
    )


def patch_codex_acp_installer() -> None:
    import benchflow.agents.install as agent_install
    import benchflow.agents.registry as registry

    original = agent_install.AGENT_INSTALLERS["codex-acp"]
    if "benchflow-codex-acp-model-patch.cjs" in original:
        return
    patched = f"{original} && {codex_acp_patch_command()}"
    agent_install.AGENT_INSTALLERS["codex-acp"] = patched
    registry.AGENT_INSTALLERS["codex-acp"] = patched
    registry.AGENTS["codex-acp"].install_cmd = patched


def _container_aware_path(original_path):
    def path(value="."):
        raw = os.fspath(value)
        if isinstance(raw, str) and raw.startswith("/"):
            return PurePosixPath(raw)
        return original_path(value)

    return path


def patch_container_path_handling() -> None:
    import benchflow.agents.credentials as credentials
    import benchflow.agents.install as agent_install
    import benchflow.sandbox.lockdown as lockdown

    for module in (credentials, agent_install, lockdown):
        module.Path = _container_aware_path(module.Path)

    def validate_locked_path(path: str) -> None:
        normalized = posixpath.normpath(path)
        if normalized != path:
            raise ValueError(
                f"Invalid locked path {path!r}: normalizes to {normalized!r} - "
                "use the normalized form directly"
            )
        if any(component == ".." for component in path.split("/")):
            raise ValueError(f"Invalid locked path {path!r}: '..' component not allowed")
        if not lockdown._SAFE_PATH_RE.match(path):
            raise ValueError(
                f"Invalid locked path {path!r}: must be absolute, "
                "alphanumeric with /-_.*? only"
            )
        if path.endswith("/") and path != "/":
            raise ValueError(
                f"Invalid locked path {path!r}: trailing slash not allowed"
            )

    lockdown._validate_locked_path = validate_locked_path


def patch_skill_injection() -> None:
    import benchflow.rollout_planes as rollout_planes
    import benchflow.sandbox.lockdown as lockdown
    import benchflow.sandbox.setup as setup

    def inject_skills_into_dockerfile(
        task_path: Path,
        skills_dir: Path,
        *,
        sandbox_dir: str = "/skills",
    ) -> None:
        env_dir = task_path / "environment"
        sandbox_dir = setup.validate_container_mount_path(sandbox_dir)
        dockerfile_path = env_dir / "Dockerfile"
        if not dockerfile_path.exists() or not skills_dir.is_dir():
            return
        if not any(skills_dir.iterdir()):
            setup.logger.info("Skills injection skipped: skills directory is empty")
            return

        destination = env_dir / "_deps" / "skills"
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(
            skills_dir,
            destination,
            symlinks=False,
            ignore=setup._stage_ignore,
        )

        lines = [
            "",
            "# Skills directory (injected by benchflow --skills-dir)",
            f"COPY _deps/skills {setup._docker_copy_dir(sandbox_dir)}",
        ]
        for agent_path in setup._get_agent_skill_paths():
            parent = PurePosixPath(agent_path).parent.as_posix()
            lines.append(
                f"RUN mkdir -p {parent} && ln -sf {sandbox_dir} {agent_path}"
            )

        content = dockerfile_path.read_text(encoding="utf-8")
        # Path.write_text() translates newlines on Windows, which breaks Docker
        # heredocs when the generated Dockerfile is executed in Linux.
        dockerfile_path.write_bytes(
            (content.rstrip("\r\n") + "\n" + "\n".join(lines) + "\n").encode("utf-8")
        )
        setup.logger.info(
            "Skills injected into Dockerfile: %d items",
            len(list(skills_dir.iterdir())),
        )

    setup._inject_skills_into_dockerfile = inject_skills_into_dockerfile
    rollout_planes._inject_skills_into_dockerfile = inject_skills_into_dockerfile

    def validate_locked_path(path: str) -> None:
        normalized = posixpath.normpath(path)
        if normalized != path:
            raise ValueError(
                f"Invalid locked path {path!r}: normalizes to {normalized!r}; "
                "use the normalized form directly"
            )
        if any(component == ".." for component in path.split("/")):
            raise ValueError(f"Invalid locked path {path!r}: '..' component not allowed")
        if not lockdown._SAFE_PATH_RE.match(path):
            raise ValueError(
                f"Invalid locked path {path!r}: must be absolute, "
                "alphanumeric with /-_.*? only"
            )
        if path.endswith("/") and path != "/":
            raise ValueError(
                f"Invalid locked path {path!r}: trailing slash not allowed "
                "(chown on '/dir/' may have unintended scope)"
            )

    def legacy_root_tool_link_cmd(source: str, destination: str) -> str:
        source_quoted = shlex.quote(source)
        destination_quoted = shlex.quote(destination)
        parent = shlex.quote(PurePosixPath(destination).parent.as_posix())
        return (
            f"if [ -e {source_quoted} ] && [ ! -L {destination_quoted} ]; then "
            f"mkdir -p {parent} && "
            f"rmdir {destination_quoted} 2>/dev/null || true; "
            f"[ -e {destination_quoted} ] || ln -s {source_quoted} {destination_quoted}; "
            "fi"
        )

    lockdown._validate_locked_path = validate_locked_path
    lockdown._legacy_root_tool_link_cmd = legacy_root_tool_link_cmd


def main() -> None:
    patch_container_path_handling()
    patch_skill_injection()
    patch_codex_acp_installer()
    from benchflow.cli.main import app

    app()


if __name__ == "__main__":
    main()
