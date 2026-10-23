"""Check meaningful export boundaries without any network or live credentials."""

import contextlib
import importlib.util
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SPEC = importlib.util.spec_from_file_location(
    "workspace", Path(__file__).resolve().parents[1] / "scripts/workspace.py"
)
workspace = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(workspace)


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = self.base / "repo"
        self.root.mkdir()
        self.run_git("init", "-q")
        self.run_git("config", "user.email", "test@example.invalid")
        self.run_git("config", "user.name", "Boundary test")
        self.write("AGENTS.md", "Shared instructions")
        self.write(".agents/skills/example/SKILL.md", "Shared skill")
        self.write("playbooks/shared.md", "Shared procedure")
        source = workspace.ROOT / "stores/Noureli/store.json"
        self.manifest = json.loads(source.read_text())
        # This fixture intentionally models an unknown shop, independently of
        # the actual store identity recorded in the repository.
        self.manifest["shopify"] = {"permanent_domain": None, "shop_id": None}
        self.write("stores/Noureli/store.json", json.dumps(self.manifest))
        for name in workspace.REQUIRED_DIRS:
            self.write(f"stores/Noureli/{name}/README.md", "Store material")
        self.write("stores/Noureli/AGENTS.md", "Store instructions")
        self.write("stores/Noureli/.env.example", "NOURELI_SHOPIFY_ADMIN_TOKEN=\n")
        self.write("stores/OtherStore/store.json", '{"private": "other store material"}')
        self.commit()

    def run_git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args],
                              capture_output=True, check=True)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def commit(self):
        self.run_git("add", "--all")
        self.run_git("commit", "-qm", "Fixture")

    def export(self):
        destination = self.base / "export"
        with contextlib.redirect_stdout(io.StringIO()):
            workspace.bundle(self.root, "Noureli", destination)
        return destination

    def test_exports_one_committed_store_and_shared_guidance(self):
        self.write("stores/Noureli/.env", "not-a-real-secret")
        self.write("stores/Noureli/content/untracked.md", "Uncommitted material")
        destination = self.export()
        self.assertTrue((destination / "stores/Noureli/store.json").is_file())
        self.assertTrue((destination / ".agents/skills/example/SKILL.md").is_file())
        self.assertTrue((destination / "stores/Noureli/.env.example").is_file())
        self.assertFalse((destination / "stores/OtherStore").exists())
        self.assertFalse((destination / ".git").exists())
        self.assertFalse((destination / "stores/Noureli/.env").exists())
        self.assertFalse((destination / "stores/Noureli/content/untracked.md").exists())
        metadata = json.loads((destination / ".bundle.json").read_text())
        self.assertEqual(metadata["source_commit"],
                         self.run_git("rev-parse", "HEAD").stdout.decode().strip())

    def test_rejects_a_tracked_secret_path_without_partial_output(self):
        self.write("stores/Noureli/.env", "not-a-real-secret")
        self.commit()
        with self.assertRaises(workspace.WorkspaceError):
            self.export()
        self.assertFalse((self.base / "export").exists())

    def test_rejects_private_data_even_when_tracked(self):
        self.write("stores/Noureli/data/private/orders.csv", "fake fixture")
        self.commit()
        with self.assertRaises(workspace.WorkspaceError):
            self.export()

    def test_rejects_symlinks_to_any_target(self):
        target = self.root / "stores/Noureli/content/link"
        target.symlink_to("../../OtherStore/store.json")
        self.commit()
        with self.assertRaises(workspace.WorkspaceError):
            self.export()

    def test_rejects_dirty_tracked_files(self):
        self.write("stores/Noureli/AGENTS.md", "Changed without a commit")
        with self.assertRaises(workspace.WorkspaceError):
            self.export()

    def test_rejects_required_instructions_present_only_as_untracked_file(self):
        path = self.root / "stores/Noureli/AGENTS.md"
        path.unlink()
        self.commit()
        path.write_text("Untracked instructions must not satisfy export readiness")
        with self.assertRaises(workspace.WorkspaceError):
            self.export()
        self.assertFalse((self.base / "export").exists())

    def test_rejects_required_directory_present_only_as_untracked_files(self):
        path = self.root / "stores/Noureli/brand/README.md"
        path.unlink()
        self.commit()
        path.write_text("Untracked brand material")
        with self.assertRaises(workspace.WorkspaceError):
            self.export()

    def test_preserves_executable_shared_helpers(self):
        self.write(".agents/skills/example/helper.sh", "#!/bin/sh\nexit 0\n")
        (self.root / ".agents/skills/example/helper.sh").chmod(0o755)
        self.commit()
        destination = self.export()
        self.assertEqual((destination / ".agents/skills/example/helper.sh").stat().st_mode & 0o777,
                         0o755)

    def test_refuses_destination_inside_repo(self):
        with self.assertRaises(workspace.WorkspaceError):
            workspace.bundle(self.root, "Noureli", self.root / "bundle")

    def test_does_not_overwrite_existing_destination(self):
        destination = self.base / "export"
        destination.mkdir()
        (destination / "keep.txt").write_text("Keep existing work")
        with self.assertRaises(workspace.WorkspaceError):
            self.export()
        self.assertEqual((destination / "keep.txt").read_text(), "Keep existing work")

    def test_rejects_store_path_traversal(self):
        with self.assertRaises(workspace.WorkspaceError):
            workspace.load_store(self.root, "../OtherStore")

    def test_rejects_cross_store_credential_namespace(self):
        self.manifest["connections"][0]["credential_env"] = "OTHER_SHOPIFY_ADMIN_TOKEN"
        self.write("stores/Noureli/store.json", json.dumps(self.manifest))
        with self.assertRaises(workspace.WorkspaceError):
            workspace.load_store(self.root, "Noureli")

    def test_manifest_cannot_claim_runtime_verification(self):
        self.manifest["connections"][0]["status"] = "verified"
        self.write("stores/Noureli/store.json", json.dumps(self.manifest))
        with self.assertRaises(workspace.WorkspaceError):
            workspace.load_store(self.root, "Noureli")

    def test_valid_manifest_with_unknown_account_is_offline_only(self):
        data = workspace.load_store(self.root, "Noureli")
        self.assertIsNone(data["shopify"]["permanent_domain"])
        self.assertEqual(data["access"]["runtime_status"], "not_provisioned")


if __name__ == "__main__":
    unittest.main()
