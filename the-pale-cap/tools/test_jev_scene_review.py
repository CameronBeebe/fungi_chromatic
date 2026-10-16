"""Offline tests: locality, fixed palette decoding, evidence and graph gates."""
import unittest
from PIL import Image
import heartwood_patch_audit as patch
import jev_scene_review as review
import jev_scene_inspect as inspect
from jev_scene_package import fingerprint


def scene_plan():
    objects = [{'id':key,'name':key,'locator':'a visible feature','accepted':True,
                'anchorCell':'C4','box':{'left':.1,'top':.1,'right':.3,'bottom':.3}}
               for key in ('root','shelf')]
    return {'revision':'rev','objects':objects}, {'sourceRevision':'rev','relationships':[
        {'id':'growth','a':'shelf','b':'root','kind':'attached_to'}]}


def master():
    tilemap=bytes(i%256 for i in range(360))
    attrs=bytes(8 if i>=256 else 0 for i in range(360))
    return bytes(360*16),tilemap,attrs,bytes(4640)


class PatchTests(unittest.TestCase):
    def test_escaped_pixel_and_empty_change_fail(self):
        a=Image.new('RGB',(160,144));b=a.copy()
        self.assertFalse(patch.audit_pixels(a,b)[0]['passed'])
        b.putpixel((104,80),(10,20,30))
        report,_=patch.audit_pixels(a,b)
        self.assertTrue(report['passed']);self.assertEqual(report['changedBoundsXYXY'],[104,80,105,81])
        b.putpixel((136,80),(10,20,30))
        report,_=patch.audit_pixels(a,b)
        self.assertEqual(report['outsidePixels'],1);self.assertFalse(report['passed'])

    def test_wrong_size_and_footprint_rejected(self):
        a=Image.new('RGB',(160,144))
        with self.assertRaises(ValueError):patch.audit_pixels(a,Image.new('RGB',(80,72)))
        with self.assertRaises(ValueError):patch.audit_pixels(a,a,(150,0,20,8))

    def test_patch_roundtrip_and_alias_escape(self):
        tiles,tilemap,attrs,pal=master();ids=[213,214,215,216,233,234,235,236,253,254,255,256]
        cut=bytes([255])*192
        after=patch.apply_patch(tiles,tilemap,attrs,ids,bytes(192),cut)
        self.assertEqual(len(after),len(tiles));self.assertEqual(after[213*16:214*16],cut[:16])
        bad=bytearray(tilemap);bad[0]=213
        with self.assertRaises(ValueError):patch.apply_patch(tiles,bad,attrs,ids,bytes(192),cut)
        with self.assertRaises(ValueError):patch.apply_patch(tiles,tilemap,attrs,ids,cut,cut)
        with self.assertRaises(ValueError):patch.apply_patch(tiles,tilemap,attrs,ids+[213],bytes(208),bytes(208))

    def test_decode_palette_and_flip_bits(self):
        tiles,tilemap,attrs,pal=master();tiles=bytearray(tiles);tiles[0]=128
        pal=bytearray(pal)
        # Row zero uses the initial palette block; index one is its second word.
        pal[2]=31
        image=patch.decode(tiles,tilemap,attrs,pal)
        self.assertEqual(image.getpixel((0,0)),(255,0,0));self.assertEqual(image.getpixel((7,0)),(0,0,0))
        attrs=bytearray(attrs);attrs[0]|=0x20
        image=patch.decode(tiles,tilemap,attrs,pal)
        self.assertEqual(image.getpixel((7,0)),(255,0,0))
        with self.assertRaises(ValueError):patch.decode(tiles,tilemap,attrs,pal[:-1])

    def test_c_arrays_are_literal_not_executable(self):
        self.assertEqual(patch.c_array('const uint8_t v[] = {1, 2,};','v',8),[1,2])
        for text in ['const uint8_t v[] = {256};','const uint8_t v[] = {1<<2};','const uint8_t v[] = {-1};']:
            with self.assertRaises(ValueError):patch.c_array(text,'v',8)


class RelationshipTests(unittest.TestCase):
    def test_direction_and_symmetric_duplicates(self):
        scene,plan=scene_plan();reverse={'id':'reverse','a':'root','b':'shelf','kind':'attached_to'}
        plan['relationships'].append(reverse);review.validate_plan(scene,plan)
        for e in plan['relationships']:e['kind']='same_growth'
        with self.assertRaises(ValueError):review.validate_plan(scene,plan)

    def test_missing_identity_stale_revision_and_bound(self):
        for mutate in [lambda p:p.update(sourceRevision='stale'),lambda p:p['relationships'][0].update(a='missing'),lambda p:p.update(relationships=p['relationships']*17)]:
            scene,plan=scene_plan();mutate(plan)
            with self.assertRaises(ValueError):review.validate_plan(scene,plan)

    def test_unresolved_object_is_not_rescued_by_high_relation(self):
        scene,plan=scene_plan();image=Image.new('RGB',(160,144))
        payload,aliases=review.relationship_request(scene,plan,image)
        answers={q:{'type':'noul','noul':.99} for q in payload['questions']}
        edge=review.compile_relations(scene,plan,aliases,answers)[0]
        self.assertTrue(edge['candidateSupported']);self.assertEqual(edge['enabledActions'],[])
        scene['objects'][0]['accepted']=False
        edge=review.compile_relations(scene,plan,aliases,answers)[0]
        self.assertFalse(edge['candidateSupported']);self.assertIn('b_inspect_unresolved',edge['reviewReasons'])

    def test_fresh_presence_gates_and_probabilities_remain_separate(self):
        scene,plan=scene_plan();payload,aliases=review.relationship_request(scene,plan,Image.new('RGB',(160,144)))
        answers={q:{'type':'noul','noul':.9} for q in payload['questions']}
        answers[aliases['shelf']+'_presence']['noul']=.2
        edge=review.compile_relations(scene,plan,aliases,answers)[0]
        self.assertFalse(edge['candidateSupported']);self.assertEqual(edge['probability'],.9)
        self.assertEqual(edge['presence']['a'],.2)

    def test_comparison_has_registered_full_and_crop_images_no_old_scores(self):
        a=Image.new('RGB',(160,144));b=a.copy();b.putpixel((104,80),(255,0,0))
        request=review.comparison_request(a,b)
        self.assertEqual(len(request['assets']),4);self.assertEqual(set(request['questions']),set(review.CHECKS))
        self.assertNotIn('exactAudit',request['state'])
        repeat=review.comparison_request(a,b)
        self.assertEqual(fingerprint(request),fingerprint(repeat))
        self.assertNotEqual(fingerprint(request),fingerprint(review.comparison_request(b,a)))

    def test_bad_answers_rejected_and_html_escaped(self):
        req=review.comparison_request(Image.new('RGB',(160,144)),Image.new('RGB',(160,144)))
        resp={'model':inspect.JUDGE,'answers':{q:{'type':'noul','noul':.8} for q in req['questions']}}
        inspect.validate_judgments(req,resp)
        resp['answers']['intact_visible']['noul']=float('nan')
        with self.assertRaises(ValueError):inspect.validate_judgments(req,resp)
        html=review.render({'name':'</script><script>alert(1)</script>'})
        self.assertNotIn('</script><script>alert(1)',html)

    def test_strong_change_cannot_override_missing_target_or_bad_exact_check(self):
        answers={k:{'noul':.95} for k in review.CHECKS}
        answers['intact_visible']['noul']=.42
        checks,status=review.compile_comparison(answers,{'passed':True})
        self.assertFalse(status['candidateSupported']);self.assertIn('intact_visible',status['reviewReasons'])
        self.assertEqual(checks['depleted_readable']['probability'],.95)
        answers['intact_visible']['noul']=.95
        _,status=review.compile_comparison(answers,{'passed':False})
        self.assertFalse(status['candidateSupported']);self.assertIn('exact_pixel_audit_failed',status['reviewReasons'])


if __name__=='__main__':unittest.main()
