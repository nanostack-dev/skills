"""Contract and rendering tests; run with python3 scripts/test_build.py."""
import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('builder', ROOT/'scripts/build.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
EXAMPLE = json.loads((ROOT/'examples/shipping/design.json').read_text())


class BuildContract(unittest.TestCase):
    def test_complete_example_and_derived_field_ownership_changes(self):
        builder.validate(copy.deepcopy(EXAMPLE))
        view = EXAMPLE['views'][1]
        delta = builder.changes(view['before']['nodes'], view['after']['nodes'])
        self.assertEqual({v['id']:v['status'] for v in delta}, {'customer':'unchanged','order':'changed','command':'added'})
        after = copy.deepcopy(view['after']['nodes'])
        after[0]['owner'] = 'Different authority'
        self.assertEqual(builder.changes(view['after']['nodes'],after)[0]['status'],'changed')

    def test_rename_cardinality_endpoint_and_removal_are_changes(self):
        before = EXAMPLE['views'][1]['before']
        renamed = copy.deepcopy(before['nodes'])
        renamed[0]['name'] = 'Account'
        self.assertEqual(builder.changes(before['nodes'],renamed)[0]['status'],'changed')
        self.assertEqual(builder.changes(before['nodes'],[before['nodes'][0]])[1]['status'],'removed')
        changed = copy.deepcopy(before['edges'])
        changed[0]['cardinality'] = '1 : 1'
        self.assertEqual(builder.changes(before['edges'],changed)[0]['status'],'changed')
        changed[0]['to'] = 'customer'
        self.assertEqual(builder.changes(before['edges'],changed)[0]['status'],'changed')

    def test_missing_references_dangling_edges_and_duplicate_ids_rejected(self):
        mutations = [
            lambda d:d['pseudocode'][0]['acceptance'].append('nonexistent'),
            lambda d:d['views'][0]['after']['edges'][0].update(to='nonexistent'),
            lambda d:d['views'][0]['after']['nodes'].append(d['views'][0]['after']['nodes'][0]),
            lambda d:d['flows'][0]['scenarios'][0]['steps'][0].update(mode='local'),
            lambda d:d['acceptance'][0].update(status=['passed']),
            lambda d:d.update(unsupported='silent data loss'),
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                d=copy.deepcopy(EXAMPLE);mutation(d)
                with self.assertRaises(builder.Invalid): builder.validate(d)

    def test_narrow_adr_can_omit_inapplicable_views_honestly(self):
        d=copy.deepcopy(EXAMPLE)
        d['views']=[];d['flows']=[];d['pseudocode']=[];d['acceptance']=[];d['risks']=[]
        d['omitted_views']=[{'view':v,'reason':'Narrow decision; this view is outside its scope.'} for v in ['big-picture','entities','service-interactions','third-party','pseudocode','acceptance']]
        builder.validate(d)
        d['omitted_views'].pop()
        with self.assertRaises(builder.Invalid): builder.validate(d)

    def test_html_escapes_executable_content_and_preserves_literal_pseudocode(self):
        if not builder.shutil.which('dot'): self.skipTest('Graphviz absent')
        d=copy.deepcopy(EXAMPLE)
        attack='</script><script>window.pwned=1</script>'
        d['title']=attack;d['views'][1]['after']['nodes'][1]['fields']['unsafe']=attack
        report=builder.html_report(builder.validate(d))
        self.assertNotIn(attack,report)
        self.assertIn('&lt;/script&gt;',report)
        self.assertIn(builder.safe(d['pseudocode'][0]['code']),report)

    def test_changed_edge_keeps_both_paths_with_before_after_endpoints(self):
        if not builder.shutil.which('dot'): self.skipTest('Graphviz absent')
        view=copy.deepcopy(EXAMPLE['views'][0])
        view['after']['edges'][0]['to']='parcel'
        svg=builder.graph(view)
        self.assertIn('context-edge-request-before',svg)
        self.assertIn('context-edge-request-after',svg)
        self.assertIn('state-removed',svg)
        self.assertIn('state-added',svg)

    def test_markdown_only_works_without_dot_and_removes_stale_html(self):
        with tempfile.TemporaryDirectory() as temp:
            source=Path(temp)/'input.json';source.write_text(json.dumps(EXAMPLE))
            output=Path(temp)/'report';output.mkdir()
            (output/'design.html').write_text('stale generated report')
            env={**os.environ,'PATH':''}
            result=subprocess.run([sys.executable,str(ROOT/'scripts/build.py'),str(source),'--out',str(output),'--markdown-only'],env=env,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertTrue((output/'design.md').exists())
            self.assertTrue((output/'adr-D1.md').exists())
            self.assertFalse((output/'design.html').exists())

    def test_failed_render_leaves_previous_outputs_intact(self):
        with tempfile.TemporaryDirectory() as temp:
            source=Path(temp)/'input.json';source.write_text(json.dumps(EXAMPLE))
            output=Path(temp)/'report';output.mkdir()
            (output/'design.md').write_text('previous good report')
            env={**os.environ,'PATH':''}
            result=subprocess.run([sys.executable,str(ROOT/'scripts/build.py'),str(source),'--out',str(output)],env=env,capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertEqual((output/'design.md').read_text(),'previous good report')


if __name__=='__main__': unittest.main()
