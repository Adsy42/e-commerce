#!/usr/bin/env python3
"""Validate store declarations and export committed material for one store.

The export is a file projection, not an operating-system sandbox or credential
manager. See docs/ACCESS.md before connecting any external service.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_DIRS = ("brand", "catalog", "content", "theme", "config", "operations", "reports")
SHARED_PREFIXES = (".agents/skills/", "playbooks/", "templates/")
SHARED_FILES = {
    "AGENTS.md", ".gitignore", "scripts/workspace.py", "docs/ACCESS.md",
    "docs/CODEX-PROJECTS.md", "docs/STORE-WORKFLOW.md", "docs/SYNC.md"
}
STATUSES = {"not_configured", "verification_required"}


class WorkspaceError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise WorkspaceError(message)


def git(root, *args):
    result = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, check=False
    )
    if result.returncode:
        # Avoid printing remote URLs, credentials, or arbitrary provider output.
        raise WorkspaceError("Git operation failed: " + " ".join(args[:2]))
    return result.stdout


def load_store(root, name):
    require(re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", name), "Invalid store directory name")
    directory = root / "stores" / name
    require(directory.is_dir() and not directory.is_symlink(), f"Missing store: {name}")
    manifest = directory / "store.json"
    require(not manifest.is_symlink(), f"{name}: store manifest cannot be a symlink")
    try:
        data = json.loads(manifest.read_text())
    except (OSError, ValueError) as error:
        raise WorkspaceError(f"{name}: cannot read a valid store.json") from error
    require(isinstance(data, dict), f"{name}: manifest must be an object")
    expected = {"schema_version", "id", "name", "shopify", "access", "connections"}
    require(set(data) == expected, f"{name}: manifest fields must match the documented structure")
    require(type(data["schema_version"]) is int and data["schema_version"] == 1,
            f"{name}: unsupported schema_version")
    require(data["id"] == name.lower(), f"{name}: id must equal its lower-case directory name")
    require(data["name"] == name, f"{name}: name must match directory")
    shop = data["shopify"]
    require(isinstance(shop, dict) and set(shop) == {"permanent_domain", "shop_id"},
            f"{name}: invalid shopify fields")
    domain = shop["permanent_domain"]
    require(domain is None or (isinstance(domain, str) and re.fullmatch(
        r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.myshopify\.com", domain)),
        f"{name}: use the permanent myshopify.com hostname without scheme or path")
    shop_id = shop["shop_id"]
    require(shop_id is None or (isinstance(shop_id, str) and re.fullmatch(
        r"gid://shopify/Shop/[0-9]+", shop_id)), f"{name}: use a Shopify Shop GraphQL ID")
    access = data["access"]
    require(isinstance(access, dict) and set(access) == {
        "isolation", "runtime_status", "live_writes", "private_data"
    }, f"{name}: invalid access fields")
    require(access["isolation"] == "strict", f"{name}: strict isolation is required")
    require(access["runtime_status"] in {"not_provisioned", "provisioned"},
            f"{name}: invalid runtime_status")
    require(access["live_writes"] == "explicit_authorization",
            f"{name}: live writes need explicit authorization")
    require(access["private_data"] == "external_only", f"{name}: private data must stay external")
    connections = data["connections"]
    require(isinstance(connections, list) and connections, f"{name}: declare required connections")
    instances, variables, services = set(), set(), set()
    for connection in connections:
        require(isinstance(connection, dict) and set(connection) == {
            "service", "instance", "status", "account_id", "credential_env", "permissions", "identity_check"
        }, f"{name}: invalid connection fields; never add secret values")
        service = connection["service"]
        require(isinstance(service, str) and re.fullmatch(r"[a-z][a-z0-9_-]*", service),
                f"{name}: invalid service name")
        instance = connection["instance"]
        require(isinstance(instance, str) and re.fullmatch(
            rf"[a-z][a-z0-9_]*_{re.escape(data['id'].replace('-', '_'))}", instance),
            f"{name}: connection instance must end with the store id")
        require(instance not in instances, f"{name}: duplicate connection instance")
        instances.add(instance)
        services.add(service)
        variable = connection["credential_env"]
        prefix = data["id"].upper().replace("-", "_") + "_"
        require(isinstance(variable, str) and re.fullmatch(
            re.escape(prefix) + r"[A-Z][A-Z0-9_]*", variable),
            f"{name}: credential variable must use the store namespace")
        require(variable not in variables, f"{name}: duplicate credential variable")
        variables.add(variable)
        require(connection["status"] in STATUSES,
                f"{name}: connection declarations cannot claim runtime verification")
        account = connection["account_id"]
        require(account is None or (isinstance(account, str) and bool(account.strip())),
                f"{name}: account_id must be a nonempty identifier or null")
        permissions = connection["permissions"]
        require(isinstance(permissions, list) and all(
            isinstance(scope, str) and re.fullmatch(r"[A-Za-z][A-Za-z0-9_.:-]*", scope)
            for scope in permissions), f"{name}: invalid permission list")
        require(isinstance(connection["identity_check"], str) and connection["identity_check"].strip(),
                f"{name}: describe the required provider identity check")
    require("shopify" in services, f"{name}: Shopify connection requirement missing")
    for item in ("AGENTS.md", ".env.example", *REQUIRED_DIRS):
        path = directory / item
        require(path.exists() and not path.is_symlink(), f"{name}: missing or symlinked {item}")
    return data


def check(root, selected=None):
    stores = root / "stores"
    require(stores.is_dir() and not stores.is_symlink(), "Missing or symlinked stores directory")
    names = sorted(path.name for path in stores.iterdir() if path.is_dir() or path.is_symlink())
    require(names, "No stores declared")
    require(len({name.lower() for name in names}) == len(names), "Duplicate store names ignoring case")
    require(len({name.lower().replace('-', '_') for name in names}) == len(names),
            "Store names must use different credential namespaces")
    require(selected is None or selected in names, "Selected store does not exist")
    domains = set()
    for name in names:
        data = load_store(root, name)
        domain = data["shopify"]["permanent_domain"]
        require(domain is None or domain not in domains, "The same Shopify domain is assigned to several stores")
        if domain:
            domains.add(domain)
        if selected is None or selected == name:
            print(f"{name}: structure valid; runtime={data['access']['runtime_status']}; "
                  f"Shopify identity={'declared' if domain and data['shopify']['shop_id'] else 'not configured'}")
    print("Declarations checked. Live credentials, effective tool access, and runtime isolation were not verified.")


def safe_export_path(name):
    path = PurePosixPath(name)
    require(not path.is_absolute() and ".." not in path.parts, "Unsafe export path")
    lowered = [part.lower() for part in path.parts]
    forbidden = {".git", ".codex", ".runtime", ".local", "private", "node_modules", ".venv",
                 "auth.json", ".credentials.json", "credentials.json", "cookies.json",
                 "storage-state.json", "browser-profile"}
    require(not forbidden.intersection(lowered), "Sensitive or machine-local path cannot be exported: " + name)
    leaf = lowered[-1]
    require(not ((leaf == ".env" or leaf.startswith(".env.")) and leaf != ".env.example"),
            "Environment file cannot be exported: " + name)
    require(not leaf.endswith((".pem", ".key", ".p12", ".pfx")),
            "Credential/key file cannot be exported: " + name)


def bundle(root, name, destination):
    load_store(root, name)
    root = root.resolve()
    destination = Path(destination).absolute()
    resolved = destination.resolve()
    require(not destination.exists() and not destination.is_symlink(), "Destination must not already exist")
    require(resolved != root and root not in resolved.parents, "Destination must be outside the source checkout")
    require(destination.parent.is_dir(), "Destination parent directory must already exist")
    require(not git(root, "status", "--porcelain=v1", "--untracked-files=no").strip(),
            "Commit or preserve tracked changes before exporting")
    commit = git(root, "rev-parse", "--verify", "HEAD^{commit}").decode().strip()
    prefix = f"stores/{name}/"
    selected = []
    for entry in git(root, "ls-tree", "-rz", "HEAD").split(b"\0"):
        if not entry:
            continue
        metadata, raw_name = entry.split(b"\t", 1)
        filename = raw_name.decode("utf-8")
        if not (filename in SHARED_FILES or filename.startswith(SHARED_PREFIXES) or filename.startswith(prefix)):
            continue
        safe_export_path(filename)
        mode, kind, object_id = metadata.split()
        require(mode in {b"100644", b"100755"} and kind == b"blob",
                "Symlinks/submodules cannot be exported: " + filename)
        selected.append((filename, object_id.decode(), mode))
    filenames = {filename for filename, _, _ in selected}
    require(prefix + "store.json" in filenames and "AGENTS.md" in filenames,
            "Store and shared instructions must be committed before export")
    # Build in a temporary sibling. A rejected file never leaves a partial bundle.
    temporary = Path(tempfile.mkdtemp(prefix=".store-bundle-", dir=destination.parent))
    try:
        for filename, object_id, mode in selected:
            target = temporary / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(git(root, "cat-file", "blob", object_id))
            target.chmod(0o755 if mode == b"100755" else 0o644)
        # Required files must exist in the committed projection, not merely as
        # ignored/untracked files in the administrator's working directory.
        load_store(temporary, name)
        (temporary / ".bundle.json").write_text(json.dumps({
            "format_version": 1, "store": name, "source_commit": commit,
            "notice": "File projection only. Provision an isolated runtime and store-only credentials separately."
        }, indent=2) + "\n")
        require(not destination.exists(), "Destination appeared during export")
        temporary.rename(destination)
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    print(f"Exported {len(selected)} committed files for {name} to {destination}")
    print("No Git history or other store directories included. This command did not create a sandbox or connect accounts.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("check", help="Validate store declarations (not live access)")
    validate.add_argument("--store")
    export = commands.add_parser("bundle", help="Export one committed store and approved shared files")
    export.add_argument("store")
    export.add_argument("destination", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "check":
            check(ROOT, args.store)
        else:
            bundle(ROOT, args.store, args.destination)
    except (WorkspaceError, OSError, UnicodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
