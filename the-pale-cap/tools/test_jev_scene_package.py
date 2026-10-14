"""Mechanical invariants for the draft scene compiler; no model or network."""
import copy
import json
import unittest

from jev_scene_package import compile_package, harvest


def record(terrain, interactions, cols=3):
    rows = len(terrain)//cols
    cells = [{'id':f'{chr(65+i%cols)}{i//cols+1}'} for i in range(len(terrain))]
    answers = {}
    for cell,t,a in zip(cells,terrain,interactions):
        answers[cell['id']] = {'choice':t}
        answers['interact_'+cell['id']] = {'choice':a}
    return {'sourceSize':[cols*16,rows*16],'cells':cells,'sourceSHA256':'test-art',
            'fingerprint':'test-interpretation','response':{'model':'test','answers':answers}}


class PackageTests(unittest.TestCase):
    def test_broad_colony_becomes_bounded_sites(self):
        r = record(['ground']*6,['none','harvest','harvest','none','harvest','harvest'])
        scene = compile_package(r,'test',3,2)
        self.assertEqual(len(scene['semanticRegions']),1)
        enabled = [o for o in scene['objects'] if o['enabledInPrototype']]
        self.assertEqual(len(enabled),2)
        for obj in enabled:
            self.assertEqual(len(obj['cells']),1)
            self.assertTrue(set(obj['workCells']) <= set(scene['grid']['activeComponentCells']))
        for job in scene['artStateJobs']:
            self.assertEqual(len(job['allowedNativeRectsXYWH']),1)
            self.assertEqual(job['allowedNativeRectsXYWH'][0][2:],[16,16])

    def test_harvest_survives_serialization_without_duplicate_reward(self):
        scene = compile_package(record(['ground']*6,['none','harvest','none','none','none','none']),'test',3,2)
        obj = next(o for o in scene['objects'] if o['enabledInPrototype'])
        state = copy.deepcopy(scene['persistence']['initialObjectStates'])
        self.assertEqual(harvest(scene,state,obj['id']),1)
        restored_scene = json.loads(json.dumps(scene))
        restored_state = json.loads(json.dumps(state))
        self.assertEqual(harvest(restored_scene,restored_state,obj['id']),0)
        self.assertEqual(state[obj['id']],'depleted')

    def test_no_route_disables_interaction(self):
        scene = compile_package(record(['ground','water','solid','ground','water','solid'],
                                       ['none','none','harvest','none','none','none']),'test',3,2)
        self.assertFalse(scene['objects'][0]['enabledInPrototype'])
        self.assertEqual(scene['objects'][0]['disabledReason'],'unreachable')
        self.assertFalse(scene['artStateJobs'])
        self.assertIn('no_reachable_supported_interaction',scene['validation']['promotionBlockers'])

    def test_missing_cells_rejected(self):
        r = record(['ground']*6,['none']*6)
        r['cells'].pop()
        with self.assertRaises(ValueError):compile_package(r,'test',3,2)

    def test_revision_repeatable_and_not_runtime_ready(self):
        r = record(['ground']*6,['none','harvest','none','none','none','none'])
        a = compile_package(r,'test',3,2);b=compile_package(r,'test',3,2)
        self.assertEqual(a,b)
        self.assertFalse(a['runtimeReady'])
        self.assertIn('native_runtime_not_integrated',a['validation']['promotionBlockers'])

    def test_hud_covered_foot_positions_are_excluded(self):
        scene = compile_package(record(['ground']*6,['none']*6),'test',3,2,visible_height=24)
        self.assertEqual(scene['grid']['uiOccludedFootCells'],[3,4,5])
        self.assertTrue(scene['spawnCell'] in [0,1,2])
        self.assertFalse(set(scene['grid']['proposedWalkableCells']) & {3,4,5})
        scene = compile_package(record(['ground']*6,['none','none','none','harvest','none','none']),
                                'test',3,2,visible_height=24)
        self.assertEqual(scene['objects'][0]['disabledReason'],'hidden_by_ui')


if __name__=='__main__':unittest.main()
