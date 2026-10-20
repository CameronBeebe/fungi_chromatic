import copy
import unittest
import scene_contract as contract


def spec():
    walk=[0]*360
    for x in range(5,13):walk[12*20+x]=1
    return {'candidateRevision':'candidate','walkable':walk,'spawn':[5,12],'approach':[12,12],
            'workTicks':60,'yield':2,'cost':1,'startSupplies':3}


class ContractTests(unittest.TestCase):
    def test_connected_approach_and_exact_budget(self):
        result=contract.validate(spec(),'candidate')
        self.assertTrue(result['spawnReachesWork']);self.assertEqual(result['routeBytes'],424)

    def test_blocked_spawn_and_disconnected_cells_rejected(self):
        for mutate in (lambda s:s['walkable'].__setitem__(245,0),lambda s:s['walkable'].__setitem__(0,1)):
            s=spec();mutate(s)
            with self.assertRaises(ValueError):contract.validate(s,'candidate')

    def test_work_must_touch_fixed_art_and_not_stand_inside_it(self):
        s=spec();s['approach']=[5,12]
        with self.assertRaises(ValueError):contract.validate(s,'candidate')
        s=spec();s['walkable'][253]=1;s['approach']=[13,12]
        with self.assertRaises(ValueError):contract.validate(s,'candidate')

    def test_stale_unknown_fields_bool_and_bad_economy_rejected(self):
        for mutate in (lambda s:s.update(candidateRevision='other'),lambda s:s.update(command='echo nope'),
                       lambda s:s.update(cost=True),lambda s:s.update(workTicks=256),lambda s:s.update(yield_value=1)):
            s=spec();mutate(s)
            with self.assertRaises(ValueError):contract.validate(s,'candidate')

    def test_hud_and_route_bank_budget(self):
        s=spec();s['walkable'][340]=1
        with self.assertRaises(ValueError):contract.validate(s,'candidate')
        s=spec();s['walkable']=[1]*360
        with self.assertRaises(ValueError):contract.validate(s,'candidate')

    def test_unaffordable_is_explicit_not_silently_changed(self):
        s=spec();s['cost']=4
        self.assertFalse(contract.validate(s,'candidate')['initiallyAffordable'])
        self.assertEqual(s['cost'],4)

    def test_revision_changes_for_mechanics_or_one_cell(self):
        a=spec();b=copy.deepcopy(a);b['yield']=3
        self.assertNotEqual(contract.identity(a),contract.identity(b))
        b=copy.deepcopy(a);b['walkable'][244]=1
        self.assertNotEqual(contract.identity(a),contract.identity(b))

    def test_generated_header_uses_reviewed_values(self):
        s=spec();contract.validate(s,'candidate');header=contract.header(s)
        self.assertIn('#define SCENE_WORK_TICKS 60',header);self.assertIn('#define SCENE_HARVEST_COST 1',header)
        self.assertIn('GATHERED +2',header);self.assertIn('#define SCENE_WORK_X 12',header)

    def test_route_lookup_has_no_row_wrapping(self):
        self.assertNotIn(20,contract.neighbours(19));self.assertNotIn(19,contract.neighbours(20))
        code=contract.routes(spec()['walkable']);self.assertIn('#pragma bank 3',code);self.assertIn('a*8+b',code)


if __name__=='__main__':unittest.main()
