#!/usr/bin/env python3
"""Regression checks for false completeness and private/export boundary failures."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from verify_content_catalog import verify_quest_graph

HERE=Path(__file__).resolve().parent

class InventoryGuards(unittest.TestCase):
    def test_optimized_python_cannot_skip_checks(self):
        result=subprocess.run([sys.executable,'-O',str(HERE/'verify_content_catalog.py')],
                              text=True,capture_output=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('without Python optimization',result.stderr)
    def test_quest_graph_rejects_unknown_endpoints(self):
        quest={'locations':[{'id':1},{'id':2}], 'locations_cnt':2,
               'jumps':[{'id':7,'from_to':[1,2]}], 'jumps_cnt':1}
        verify_quest_graph(quest,'fixture')
        quest['jumps'][0]['from_to']=[1,3]
        with self.assertRaisesRegex(AssertionError,'Invalid QMM jump endpoints'):
            verify_quest_graph(quest,'fixture')
    def setup_paths(self,base):
        paths={k:base/k for k in ['install','private','export','parser']}
        for p in paths.values():p.mkdir()
        return paths
    def run_verify(self,p):
        return subprocess.run([sys.executable,str(HERE/'verify_content_catalog.py'),
            '--install',str(p['install']),'--private-out',str(p['private']),
            '--export-out',str(p['export']),'--ranger-tools',str(p['parser'])],text=True,capture_output=True)
    def test_empty_dataset_is_not_a_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=self.setup_paths(Path(tmp));(p['export']/'resource-sources.json').write_text('[]')
            result=self.run_verify(p)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('Empty expected inventory',result.stderr)
    def test_missing_script_manifest_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=self.setup_paths(Path(tmp));(p['install']/'fixture.dat').write_bytes(b'fixture')
            values={'resource-sources.json':[{'source':'fixture.dat'}],
                'archive-entry-index.json':[{'archive':'x.pkg','path':'A.scr'},{'archive':'x.pkg','path':'B.scr'}],
                'script-payloads.json':[{'archive':'x.pkg','path':'A.scr'}], 'text-quest-payloads.json':[]}
            for name,value in values.items():(p['export']/name).write_text(json.dumps(value))
            result=self.run_verify(p)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('Inventory mismatch .scr payload manifest: missing=1',result.stderr)
    def test_output_boundaries(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);p=self.setup_paths(base)
            for private,public in [(base/'same',base/'same'),(base/'a',base/'a'/'b'),(base/'a'/'b',base/'a')]:
                with self.subTest(private=private,public=public):
                    result=subprocess.run([sys.executable,str(HERE/'catalog_game_content.py'),
                        '--install',str(p['install']),'--private-out',str(private),
                        '--export-out',str(public),'--ranger-tools',str(p['parser']),
                        '--rangers-utils',str(p['parser'])],text=True,capture_output=True)
                    self.assertNotEqual(result.returncode,0)
                    self.assertIn('Private and export output directories must not overlap',result.stderr)
                    self.assertFalse(private.exists())
                    self.assertFalse(public.exists())

if __name__=='__main__':unittest.main()
