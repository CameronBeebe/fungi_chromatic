import copy
import json
from pathlib import Path
import tempfile
import unittest

import scene_contract as contract
import scene_prototype as prototype


class PrototypeTests(unittest.TestCase):
    def test_review_requires_two_explicit_booleans(self):
        payload={'spec':{'example':1},'reviewedGeometry':True,'reviewedMechanics':True}
        self.assertEqual(prototype.approved_spec(payload),payload['spec'])
        for key in ('reviewedGeometry','reviewedMechanics'):
            for value in (False,1,'true',None):
                changed={**payload,key:value}
                with self.assertRaises(ValueError):prototype.approved_spec(changed)
        with self.assertRaises(ValueError):prototype.approved_spec({**payload,'runCommand':'anything'})

    def test_snapshot_changes_invalidate_candidate(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'art').mkdir();(root/'engine').mkdir()
            (root/'art/master.til').write_bytes(b'original')
            candidate={'artHashes':{'master.til':prototype.patch.sha(b'original')},'engineHashes':{},'presentationHashes':{}}
            candidate['revision']=contract.identity(candidate)
            prototype.json_write(root/'candidate.json',candidate)
            self.assertEqual(prototype.load_candidate(root),candidate)
            (root/'art/master.til').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'Snapshot changed'):prototype.load_candidate(root)

    def test_reviewer_pixels_are_bound_to_candidate(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'source.png').write_bytes(b'original')
            candidate={'artHashes':{},'engineHashes':{},'presentationHashes':{'source.png':prototype.patch.sha(b'original')}}
            candidate['revision']=contract.identity(candidate)
            prototype.json_write(root/'candidate.json',candidate)
            prototype.load_candidate(root)
            (root/'source.png').write_bytes(b'different image')
            with self.assertRaisesRegex(ValueError,'Snapshot changed'):prototype.load_candidate(root)

    def test_candidate_metadata_change_is_not_silent(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            candidate={'artHashes':{},'engineHashes':{},'defaults':{'yield':2}}
            candidate['revision']=contract.identity(candidate)
            candidate['defaults']['yield']=99
            prototype.json_write(root/'candidate.json',candidate)
            with self.assertRaisesRegex(ValueError,'Candidate was changed'):prototype.load_candidate(root)

    def test_embedded_evidence_cannot_close_script(self):
        output=prototype.render_editor({'note':'</script><script>bad()</script>'},[])
        self.assertNotIn('</script><script>bad()',output)
        self.assertIn('\\u003c/script\\u003e',output)


if __name__=='__main__':unittest.main()
